import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const base = "H:/SCI2/YR1/5_manuscript/R7B3A_ManuscriptV2/supplements";
const input = path.join(base, "R7B3A_Supplementary_Tables_S1-S10.xlsx");
const previewDir = path.join(base, "workbook_previews");
await fs.mkdir(previewDir, { recursive: true });
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(input));
const sheetInspection = await workbook.inspect({ kind: "sheet", include: "id,name", maxChars: 10000 });
await fs.writeFile(path.join(base, "R7B3A_saved_workbook_sheets.ndjson"), sheetInspection.ndjson, "utf8");
const names = [
  "S1 Sources", "S2 Screen registry", "S3 A0-A2-M paths", "S4 Support identity",
  "S5 Fit QC", "S6 Signal pairs", "S7 Simulations", "S8 External evidence",
  "S9 Liver donors", "S10 Claim ledger",
];
for (const name of names) {
  const preview = await workbook.render({ sheetName: name, range: "A1:H18", scale: 1.25, format: "png" });
  await fs.writeFile(path.join(previewDir, `${name.replaceAll(" ", "_")}.png`), new Uint8Array(await preview.arrayBuffer()));
}
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 300 },
  summary: "saved workbook formula error scan",
});
await fs.writeFile(path.join(base, "R7B3A_saved_workbook_error_scan.ndjson"), errors.ndjson, "utf8");
console.log(JSON.stringify({ sheets: names.length, previews: names.length }));
