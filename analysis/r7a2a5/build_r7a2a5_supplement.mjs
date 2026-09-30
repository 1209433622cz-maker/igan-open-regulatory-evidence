import fs from "node:fs/promises";
import zlib from "node:zlib";
import { promisify } from "node:util";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const gunzip = promisify(zlib.gunzip);
const root = "H:/SCI2/YR1";
const outputDir = `${root}/5_manuscript/R7A2A5_HumanGenomics/supplement`;
const qaDir = `${root}/5_manuscript/R7A2A5_HumanGenomics/qa/supplement_workbook`;
await fs.mkdir(outputDir, {recursive:true});
await fs.mkdir(qaDir, {recursive:true});

function parseTsv(text) {
  const lines = text.replace(/^\uFEFF/, "").trim().split(/\r?\n/);
  const split = line => {
    const out=[]; let cur=""; let quoted=false;
    for (let i=0;i<line.length;i++) {
      const ch=line[i];
      if (ch==='"') { if (quoted && line[i+1]==='"') {cur+='"';i++;} else quoted=!quoted; }
      else if (ch==='\t' && !quoted) {out.push(cur);cur="";}
      else cur+=ch;
    }
    out.push(cur); return out;
  };
  return lines.map(split);
}

async function readTsv(path) { return parseTsv(await fs.readFile(path, "utf8")); }
async function readGzTsv(path) { return parseTsv((await gunzip(await fs.readFile(path))).toString("utf8")); }

function typed(rows) {
  return rows.map((row, ri) => row.map(v => {
    if (ri===0) return v;
    if (v === "TRUE") return true;
    if (v === "FALSE") return false;
    if (v !== "" && /^-?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?$/i.test(v)) return Number(v);
    return v;
  }));
}

const wb = Workbook.create();
const navy="#17365D", teal="#1F6E78", light="#EAF2F4", amber="#FFF2CC", text="#1F2937", grid="#D9E1E8";

function addSheet(name, title, note, rows, tableName) {
  const s=wb.worksheets.add(name);
  s.showGridLines=false;
  s.getRange("A1").values=[[title]];
  s.getRange("A1").format={font:{name:"Arial",size:14,bold:true,color:navy}};
  s.getRange("A2").values=[[note]];
  s.getRange("A2").format={font:{name:"Arial",size:10,italic:true,color:"#5A6675"},wrapText:true};
  const matrix=typed(rows);
  const nrows=matrix.length, ncols=Math.max(...matrix.map(r=>r.length));
  matrix.forEach(r=>{while(r.length<ncols)r.push("");});
  const endCol=colName(ncols);
  const target=s.getRange(`A4:${endCol}${3+nrows}`);
  target.values=matrix;
  target.format.font={name:"Arial",size:9,color:text};
  target.format.verticalAlignment="center";
  s.getRange(`A4:${endCol}4`).format={fill:navy,font:{name:"Arial",size:9,bold:true,color:"#FFFFFF"},wrapText:true,verticalAlignment:"center",horizontalAlignment:"center",borders:{preset:"all",style:"thin",color:"#FFFFFF"}};
  if (nrows>1) {
    s.getRange(`A5:${endCol}${3+nrows}`).format.borders={insideHorizontal:{style:"thin",color:grid},bottom:{style:"thin",color:grid}};
  }
  s.getRange(`A1:${endCol}1`).format.rowHeight=25;
  s.getRange(`A2:${endCol}2`).format.rowHeight=34;
  s.getRange(`A4:${endCol}${Math.min(3+nrows,40)}`).format.autofitColumns();
  for(let c=0;c<ncols;c++){
    const rng=s.getRange(`${colName(c+1)}4:${colName(c+1)}${3+nrows}`);
    const width=Math.min(Math.max(rng.format.columnWidth||10,10),38);
    rng.format.columnWidth=width;
  }
  s.getRange(`A4:${endCol}${3+nrows}`).format.wrapText=false;
  s.freezePanes.freezeRows(4);
  if (nrows>1 && nrows<100000) {
    const t=s.tables.add(`A4:${endCol}${3+nrows}`,true,tableName);
    t.style="TableStyleMedium2";
    t.showBandedColumns=false;
  }
  return {sheet:s, range:`A1:${endCol}${Math.min(3+nrows,24)}`};
}

function colName(n){let s="";while(n){n--;s=String.fromCharCode(65+n%26)+s;n=Math.floor(n/26);}return s;}

const indexRows=[
  ["item","title","content","file role"],
  ["Table S1","Data-source and accession manifest","GWAS, GJOKA LD, OneK1K, TenK10K, HRA008003","Source/provenance"],
  ["Table S2","Frozen candidate/control universe","Three genes and nine OneK1K cell-gene comparisons","Design"],
  ["Table S3","OneK1K ABF screen","All nine frozen comparisons and prior sensitivity","Screening"],
  ["Table S4","Source-LD QC","Cell-specific donors, variants and residual-LD diagnostics","Quality control"],
  ["Table S5","SuSiE and signal-pair results","All configurations, signal pairs and priors","Primary signal analysis"],
  ["Table S6","Credible-set members","Disease and QTL membership and PIP","Primary signal detail"],
  ["Table S7","TenK10K replication","Two axes across all shared-signal priors","Cross-resource replication"],
  ["Table S8","Liver donor metrics","Ten donors x two target-lineage pairs","Tissue"],
  ["Table S9","Liver sensitivity","Exact permutation, BH q and leave-one-donor-out range","Tissue sensitivity"],
  ["Table S10","Claim-evidence ledger","Allowed/prohibited wording and evidence ceiling","Interpretation"],
];

const gw=await readTsv(`${root}/3_results/01_intake/R7A1A/R7A1A_PBC_byte_receipt.tsv`);
const gj=await readTsv(`${root}/3_results/00_audit/R7A1B/R7A1B_GJOKA_target_member_receipt.tsv`);
const one=JSON.parse(await fs.readFile(`${root}/3_results/00_audit/R7A1B/R7A1B_OneK_archive_gate.json`,"utf8"));
const pbc=await readTsv(`${root}/3_results/00_audit/R7A1C1/R7A1C1_HRA008003_receipts_v2.tsv`);
const ctl=await readTsv(`${root}/3_results/00_audit/R7A2A1/R7A2A1_HRA008003_control_receipts.tsv`);
const fcrReceipt=JSON.parse(await fs.readFile(`${root}/1_data/qtl/eqtl/tenk10k/derived/FCRL3_full/B_intermediate/TenK10K_B_intermediate_FCRL3_selective_intake_receipt.json`,"utf8"));
const nkReceipt=JSON.parse(await fs.readFile(`${root}/1_data/qtl/eqtl/tenk10k/derived/IL12RB2_full/remote_NK/TenK10K_NK_IL12RB2_selective_intake_receipt.json`,"utf8"));

const s1=[["resource","accession_or_member","role","url","bytes","md5_or_crc32","sha256","status"]];
s1.push(["PBC GWAS",gw[1][1],"Disease summary statistics",gw[1][3],gw[1][5],gw[1][6],gw[1][7],gw[1][8]]);
for(const r of gj.slice(1))s1.push(["GJOKA",r[1],`Disease locus ${r[0]} sumstats/LD`,`https://www.staff.ncl.ac.uk/heather.cordell/GJOKA_SUMSTATS.zip`,r[2],r[3],r[4],"PASS"]);
s1.push(["OneK1K","Zenodo 18910121","Cell-specific eQTL + genotypes","https://zenodo.org/records/18910121",one.archive_bytes,one.md5,one.sha256,one.gate]);
function receiptRow(obj, label){
  const flat=JSON.stringify(obj);
  return ["TenK10K",label,"Independent molecular-QTL resource","https://zenodo.org/records/18221260",obj.total_bytes||obj.bytes||"see receipt",obj.md5||obj.observed_md5||"",obj.sha256||"",obj.status||obj.gate||"PASS"];
}
s1.push(receiptRow(fcrReceipt,"FCRL3/B_intermediate selective intake"));
s1.push(receiptRow(nkReceipt,"IL12RB2/NK selective intake"));
for(const r of [...ctl.slice(1),...pbc.slice(1)])s1.push(["HRA008003",r[0],"Liver scRNA BAM",r[1],r[2],r[3],r[5],r[6]]);

const smoke=await readTsv(`${root}/3_results/04_integration/R7A1B/R7A1B_coloc_smoke.tsv`);
const ranges=await readTsv(`${root}/3_results/01_intake/R7A1A/R7A1A_PBC_GJOKA_locus_ranges.tsv`);
const rangeMap=new Map(ranges.slice(1).map(r=>[r[0],r]));
const s2=[["gene","cell_type","locus_index","chromosome","min_bp_grch37","max_bp_grch37","force_multisignal","design_role","promotion_status"]];
for(const r of smoke.slice(1)){
  const m=rangeMap.get(r[2]); const role=r[0]==="INAVA"?"weak-QTL control":(r[0]==="IL12RB2"?"positive-control axis":"cell-context competition");
  const promoted=r[18]==="PASS_SINGLE_CAUSAL_SMOKE"?"triggered_source_LD":r[18];
  s2.push([r[0],r[1],r[2],m[1],m[2],m[3],r[3],role,promoted]);
}

const s3=smoke;
const ldSummary=await readTsv(`${root}/3_results/04_integration/R7A1B/sourceLD/R7A1B_covariate_residual_LD_summary.tsv`);
const s4=[["gene","cell","n_samples","n_variants","model","design_columns","design_rank","residual_df","min_eigenvalue","negative_eigen_lt_minus1e8","max_asymmetry","max_diag_deviation","gate_pass"]];
for(const r of ldSummary.slice(1)){
  const qc=JSON.parse(await fs.readFile(`${root}/3_results/04_integration/R7A1B/sourceLD/${r[0]}_${r[1]}/covariate_residual_LD_QC.json`,"utf8"));
  for(const model of ["PF10","PF50"]){const q=qc.results[model];s4.push([r[0],r[1],r[2],r[3],model,q.design_columns,q.design_rank,q.residual_df,q.dual_min_eigenvalue,q.dual_negative_lt_1e8,q.max_asymmetry,q.max_diag_dev,q.gate_pass]);}
}
const fit=await readTsv(`${root}/3_results/04_integration/R7A1B/multisignal/R7A1B_susie_fit_summary.tsv`);
const coloc=await readTsv(`${root}/3_results/04_integration/R7A1B/multisignal/R7A1B_signal_coloc_susie.tsv`);
const s5=[["record_type",...fit[0]],...fit.slice(1).map(r=>["fit_summary",...r]),[],["record_type",...coloc[0]],...coloc.slice(1).map(r=>["signal_pair",...r])];
const s6=await readGzTsv(`${root}/3_results/04_integration/R7A1B/multisignal/R7A1B_susie_credible_set_members.tsv.gz`);
const fcr=await readTsv(`${root}/3_results/04_integration/R7A1C/R7A1C_FCRL3_TenK_Bintermediate_coloc.tsv`);
const il=await readTsv(`${root}/3_results/04_integration/R7A1C/R7A1C_IL12RB2_TenK_NK_fullPBC_coloc.tsv`);
const s7=[["gene","cell","p12","n","PP_H0","PP_H1","PP_H2","PP_H3","PP_H4","H4_over_H3H4","model_boundary"]];
for(const r of fcr.slice(1))s7.push(["FCRL3","B_intermediate",...r,"single-causal cross-resource replication; source-CS support"]);
for(const r of il.slice(1))s7.push(["IL12RB2","NK",r[0],r[1],"NA","NA","NA",r[2],r[3],r[4],"single-causal cross-resource replication"]);
const s8=await readTsv(`${root}/3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel.tsv`);
const s9=await readTsv(`${root}/3_results/05_tissue/R7A2A1_control/PBC_vs_control_target_panel_sensitivity.tsv`);
const s10=await readTsv(`${root}/6_release/CMM_R7A2A2_ManuscriptEvidenceFreeze_FigureAssembly_2026-09-30/results/R7A2A2_claim_evidence_matrix_v2.tsv`);

const renders=[];
renders.push(addSheet("Index","Supplementary Tables S1-S10","Frozen evidence package for the Human Genomics submission-format draft. Values are copied from validated stage outputs; no new biological selection was performed.",indexRows,"IndexTable"));
renders.push(addSheet("S1 Sources","Table S1. Data-source and accession manifest","Exact public objects, bytes and checksums used by the frozen analysis.",s1,"S1Sources"));
renders.push(addSheet("S2 Universe","Table S2. Frozen candidate/control universe","All nine prespecified OneK1K cell-gene comparisons are retained.",s2,"S2Universe"));
renders.push(addSheet("S3 ABF screen","Table S3. Single-causal ABF screen","Screening results only; promotion required the frozen source-LD/multi-signal gate.",smoke,"S3ABF"));
renders.push(addSheet("S4 LD QC","Table S4. Source-matched QTL LD quality control","PF10 and PF50 covariate-residualized LD diagnostics for all seven triggered comparisons.",s4,"S4LDQC"));
renders.push(addSheet("S5 Multi-signal","Table S5. SuSiE-RSS fits and signal-pair colocalization","Complete fit summaries and all evaluated signal pairs under all frozen priors/configurations.",s5,"S5Multi"));
renders.push(addSheet("S6 Credible sets","Table S6. Disease and QTL credible-set members","Variant-level credible-set membership and posterior inclusion probabilities from frozen outputs.",s6,"S6CS"));
renders.push(addSheet("S7 TenK replication","Table S7. TenK10K cross-resource replication","Same PBC GWAS; independent molecular-QTL resource; single-causal replication boundary retained.",s7,"S7TenK"));
renders.push(addSheet("S8 Liver donors","Table S8. HRA008003 donor-level target-panel metrics","Donors are the biological replicate. PBC and non-lesion liver controls are shown together.",s8,"S8Liver"));
renders.push(addSheet("S9 Liver sensitivity","Table S9. Exact permutation and leave-one-donor-out sensitivity","Primary and supportive tissue endpoints; BH correction within each two-target family.",s9,"S9Sensitivity"));
renders.push(addSheet("S10 Claims","Table S10. Claim-evidence ledger","Allowed and prohibited wording for every central result.",s10,"S10Claims"));

wb.recalculate();
const inspect=await wb.inspect({kind:"workbook,sheet,table",maxChars:12000,tableMaxRows:5,tableMaxCols:8,tableMaxCellChars:90});
await fs.writeFile(`${qaDir}/workbook_inspect.ndjson`,inspect.ndjson,"utf8");
const errors=await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",options:{useRegex:true,maxResults:300},summary:"final formula error scan"});
await fs.writeFile(`${qaDir}/formula_error_scan.ndjson`,errors.ndjson,"utf8");
for(const item of renders){
  const preview=await wb.render({sheetName:item.sheet.name,range:item.range,scale:1,format:"png"});
  await fs.writeFile(`${qaDir}/${item.sheet.name.replace(/[^A-Za-z0-9]+/g,"_")}.png`,new Uint8Array(await preview.arrayBuffer()));
}
const out=await SpreadsheetFile.exportXlsx(wb);
const outPath=`${outputDir}/Additional_file_1_R7A2A5_Supplementary_Tables.xlsx`;
await out.save(outPath);
console.log(JSON.stringify({outPath,sheets:renders.map(x=>x.sheet.name),sheetCount:renders.length},null,2));
