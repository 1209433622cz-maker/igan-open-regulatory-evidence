# R4A10 / H6 sex-specific SSc data intake

This kit audits newly acquired female and male summary-statistics files before any fine-mapping or colocalization.

## Input preparation

1. Keep provider files unchanged, including `.gz` compression.
2. Copy `metadata_template.json` to `female_metadata.json` and, if available, `male_metadata.json`.
3. Fill the exact source URL, accession/provider, GRCh38/hg38 assembly, effect scale, case/control counts, and sample-size design. Do not infer them from the filename.
4. Set `effect_scale` to exactly `beta`, `log_odds`, or `odds_ratio`; the declared scale must match a mapped BETA or OR column.
5. Enter at least one trusted provider or previously frozen checksum as `expected_sha256` or `expected_md5`. The script computes both hashes and checks every supplied value. A hash calculated only after the same first download helps detect later changes but does not independently authenticate its source.
6. Per-variant sample size or cohort count is preferred. Global case/control counts alone remain `CONDITIONAL`; they pass the sample-design gate only when the provider explicitly documents a fixed sample size for every variant and `variant_sample_size_constant=true` with a matching `total_sample_size`.

## Run

```powershell
cd H:\SCI2\YR1\R4A9\h6_intake
.\RUN_H6_INTAKE.ps1 `
  -FemalePath 'D:\downloads\female_ssc_sumstats.tsv.gz' `
  -FemaleMetadata '.\female_metadata.json' `
  -MalePath 'D:\downloads\male_ssc_sumstats.tsv.gz' `
  -MaleMetadata '.\male_metadata.json'
```

Female-only intake is allowed for the first pass:

```powershell
.\RUN_H6_INTAKE.ps1 `
  -FemalePath 'D:\downloads\female_ssc_sumstats.tsv.gz' `
  -FemaleMetadata '.\female_metadata.json'
```

The runner defaults to `D:\bioinfor\python.exe` in the current workspace. On another machine, pass `-PythonPath 'C:\path\to\python.exe'`; the intake uses only the Python standard library.

## Hard intake checks

The script scans the whole file and checks mapped core values row by row, numeric ranges, exact effect scale, GRCh38/hg38, trusted checksum, both frozen regional windows, regional duplicate variant keys, EAF, INFO, provenance, and sample-size design. `--max-rows` is diagnostic only and can never return a paper-grade PASS.

## Status meaning

- `PASS_PAPER_GRADE_INTAKE_READY_FOR_HARMONIZATION`: every hard intake and support-field gate passed. This authorizes harmonization only.
- `CONDITIONAL_CORE_INTAKE_PASS_SUPPORT_FIELDS_INCOMPLETE`: core statistics are usable, but one or more support fields or sample-design requirements remain incomplete.
- `DIAGNOSTIC_ONLY_MAX_ROWS_NO_PAPER_GRADE_DECISION`: a deliberately truncated scan; never use it to authorize analysis.
- `HOLD_*`: resolve the reported schema, row, assembly, checksum, regional-coverage, duplicate-key, or metadata fault before analysis.

The script writes only the two frozen ±1 Mb regions and audit summaries. It streams the full input and does not duplicate the whole downloaded file. A PASS still does not establish disease–QTL colocalization.
