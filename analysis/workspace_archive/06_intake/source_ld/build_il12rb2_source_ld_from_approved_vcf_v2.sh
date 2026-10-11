#!/usr/bin/env bash
set -euo pipefail

# Run only inside the institutionally approved controlled-access environment.
# No VCF, BED/BIM/FAM, LD matrix, or logs produced here may be copied into a public release.
#
# Usage:
#   build_il12rb2_source_ld_from_approved_vcf_v2.sh \
#     <chr1.vcf.gz> <GRCh38.fa> <variant_manifest.tsv> \
#     <four_cell_cs.tsv> <required_anchors.tsv> <controlled_outdir>

if [[ $# -ne 6 ]]; then
  echo "Expected 6 arguments; see script header." >&2
  exit 64
fi

VCF=$1
REF=$2
MANIFEST=$3
CS_MANIFEST=$4
ANCHORS=$5
OUTDIR=$6
REGION="1:67207364-67498724"
GENE="ENSG00000081985"
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
VALIDATOR="$SCRIPT_DIR/validate_received_tenk10k_source_ld_v2.py"

for tool in bcftools tabix plink2 plink python3 sha256sum; do
  command -v "$tool" >/dev/null 2>&1 || { echo "Missing dependency: $tool" >&2; exit 69; }
done
for input in "$VCF" "$REF" "$MANIFEST" "$CS_MANIFEST" "$ANCHORS" "$VALIDATOR"; do
  [[ -f "$input" ]] || { echo "Missing input: $input" >&2; exit 66; }
done

# Reduce the chance that controlled output is accidentally written into a report/release tree.
OUTDIR_ABS=$(python3 - "$OUTDIR" <<'PY'
import pathlib, sys
print(pathlib.Path(sys.argv[1]).expanduser().resolve())
PY
)
OUTDIR_NORM=$(printf '%s' "$OUTDIR_ABS" | tr '\\' '/' | tr '[:upper:]' '[:lower:]')
case "/$OUTDIR_NORM/" in
  */6_release/*|*/7.report/*|*/public/*|*/shared/*)
    echo "Refusing controlled output directory inside a release/report/public/shared path: $OUTDIR_ABS" >&2
    exit 77
    ;;
esac

mkdir -p "$OUTDIR_ABS/work" "$OUTDIR_ABS/result" "$OUTDIR_ABS/receipts"
chmod 700 "$OUTDIR_ABS" "$OUTDIR_ABS/work" "$OUTDIR_ABS/result" "$OUTDIR_ABS/receipts" 2>/dev/null || true

python3 - "$MANIFEST" "$OUTDIR_ABS/work/requested.ids" "$OUTDIR_ABS/work/a1_allele.tsv" <<'PY'
import re, sys
import pandas as pd

manifest, ids_out, a1_out = sys.argv[1:]
m = pd.read_csv(manifest, sep="\t", dtype=str, keep_default_na=False)
required = {"variant_key", "MarkerID", "CHR", "POS", "Allele1", "Allele2", "gene"}
missing = required - set(m.columns)
if missing:
    raise SystemExit(f"manifest missing columns: {sorted(missing)}")
if len(m) != 1366 or m.MarkerID.duplicated().any() or m.variant_key.duplicated().any():
    raise SystemExit("manifest must contain exactly 1,366 unique MarkerID and variant_key rows")
if not (m.MarkerID == m.variant_key).all() or set(m.gene) != {"ENSG00000081985"}:
    raise SystemExit("manifest identity/gene freeze failed")
pat = re.compile(r"^(?:chr)?1:\d+:[ACGT]+:[ACGT]+$", re.I)
if not m.MarkerID.map(lambda x: bool(pat.fullmatch(x))).all():
    raise SystemExit("manifest contains noncanonical chr1 MarkerID")
m[["MarkerID"]].to_csv(ids_out, sep="\t", header=False, index=False, lineterminator="\n")
m[["Allele1", "MarkerID"]].to_csv(a1_out, sep="\t", header=False, index=False, lineterminator="\n")
PY

NORM_VCF="$OUTDIR_ABS/work/IL12RB2.region.norm.vcf.gz"
bcftools view -r "$REGION" "$VCF" -Ou \
  | bcftools norm -f "$REF" -m -any -Oz -o "$NORM_VCF"
tabix -f -p vcf "$NORM_VCF"

# Recreate chr:pos:REF:ALT IDs. Intermediate genotype files remain controlled.
plink2 --vcf "$NORM_VCF" \
  --max-alleles 2 --snps-only just-acgt \
  --set-all-var-ids '@:#:$r:$a' --new-id-max-allele-len 200 missing \
  --make-bed --out "$OUTDIR_ABS/work/IL12RB2.native"

# Fail before LD calculation unless all 1,366 requested SNPs and allele pairs exist.
python3 - "$MANIFEST" "$OUTDIR_ABS/work/IL12RB2.native.bim" "$OUTDIR_ABS/receipts/preflight.json" <<'PY'
import hashlib, json, os, pathlib, sys, tempfile
import pandas as pd

manifest, bim_path, out_path = map(pathlib.Path, sys.argv[1:])
m = pd.read_csv(manifest, sep="\t", dtype=str, keep_default_na=False).set_index("MarkerID")
b = pd.read_csv(bim_path, sep=r"\s+", header=None, names=["CHR","SNP","CM","POS","A1","A2"], dtype=str)
dups = sorted(b.loc[b.SNP.duplicated(False), "SNP"].unique())
b = b.loc[~b.SNP.duplicated(False)].set_index("SNP")
missing = sorted(set(m.index) - set(b.index))
bad = []
for marker in sorted(set(m.index) & set(b.index)):
    if {str(b.at[marker,"A1"]).upper(), str(b.at[marker,"A2"]).upper()} != {
        str(m.at[marker,"Allele1"]).upper(), str(m.at[marker,"Allele2"]).upper()
    }:
        bad.append(marker)
payload = {
    "status": "PASS" if not (dups or missing or bad) else "HOLD",
    "requested": len(m), "bfile_variants": len(b), "duplicate_requested_ids": dups,
    "missing_requested_ids": missing, "allele_pair_mismatches": bad,
}
pathlib.Path(out_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
if payload["status"] != "PASS":
    raise SystemExit("preflight HOLD; inspect receipts/preflight.json")
PY

# This controlled reconstruction deliberately limits the matrix to the frozen 1,366
# public eQTL variants. The official public rule instead selects every bfile variant
# in the gene window, so this output must be labelled "native-manifest reconstruction"
# rather than an exact byte reproduction of an author-derived matrix.
plink --bfile "$OUTDIR_ABS/work/IL12RB2.native" \
  --extract "$OUTDIR_ABS/work/requested.ids" \
  --r square --make-just-bim \
  --a1-allele "$OUTDIR_ABS/work/a1_allele.tsv" 1 2 \
  --out "$OUTDIR_ABS/result/$GENE"

python3 "$VALIDATOR" \
  --bim "$OUTDIR_ABS/result/$GENE.bim" \
  --ld "$OUTDIR_ABS/result/$GENE.ld" \
  --variant-manifest "$MANIFEST" \
  --cs-manifest "$CS_MANIFEST" \
  --anchors "$ANCHORS" \
  --out-json "$OUTDIR_ABS/receipts/source_ld_validation.json"

sha256sum \
  "$OUTDIR_ABS/result/$GENE.bim" \
  "$OUTDIR_ABS/result/$GENE.ld" \
  "$MANIFEST" "$CS_MANIFEST" "$ANCHORS" \
  > "$OUTDIR_ABS/receipts/checksums.sha256"

{
  echo "scope=native-manifest-reconstruction"
  echo "region=$REGION"
  echo "requested_variants=1366"
  echo "generated_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  bcftools --version | head -n 1
  plink2 --version 2>&1 | head -n 1
  plink --version 2>&1 | head -n 1
  python3 --version 2>&1
} > "$OUTDIR_ABS/receipts/tool_versions.txt"

echo "PASS: source-LD reconstruction and strict structural validation completed."
echo "Keep the entire output directory inside the approved controlled environment."
