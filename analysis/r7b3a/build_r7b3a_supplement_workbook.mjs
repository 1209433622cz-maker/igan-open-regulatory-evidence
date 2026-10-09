import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const base = "H:/SCI2/YR1/5_manuscript/R7B3A_ManuscriptV2/supplements";
const output = path.join(base, "R7B3A_Supplementary_Tables_S1-S10.xlsx");
const workbook = Workbook.create();

const sheetNames = [
  "S1 Sources", "S2 Screen registry", "S3 A0-A2-M paths", "S4 Support identity",
  "S5 Fit QC", "S6 Signal pairs", "S7 Simulations", "S8 External evidence",
  "S9 Liver donors", "S10 Claim ledger",
];

for (let i = 1; i <= 10; i += 1) {
  const jsonPath = path.join(base, `S${i}`, `S${i}_workbook_view.json`);
  const records = JSON.parse(await fs.readFile(jsonPath, "utf8"));
  if (!Array.isArray(records) || records.length === 0) {
    throw new Error(`S${i}: no workbook records`);
  }
  const headers = Object.keys(records[0]);
  const matrix = [headers, ...records.map((record) => headers.map((key) => {
    const value = record[key];
    if (value === null || value === undefined) return null;
    return value;
  }))];

  const sheet = workbook.worksheets.add(sheetNames[i - 1]);
  sheet.showGridLines = false;
  sheet.freezePanes.freezeRows(1);
  sheet.freezePanes.freezeColumns(Math.min(4, headers.length));
  sheet.getRange("A1").write(matrix);
  const used = sheet.getRangeByIndexes(0, 0, matrix.length, headers.length);
  used.format.font = { name: "Arial", size: 9, color: "#1F2937" };
  used.format.verticalAlignment = "center";
  const header = sheet.getRangeByIndexes(0, 0, 1, headers.length);
  header.format = {
    fill: "#1F4E78",
    font: { name: "Arial", size: 9, bold: true, color: "#FFFFFF" },
    wrapText: true,
    horizontalAlignment: "center",
    verticalAlignment: "center",
    borders: { preset: "all", style: "thin", color: "#FFFFFF" },
  };
  header.format.rowHeight = 34;

  for (let col = 0; col < headers.length; col += 1) {
    const sample = [headers[col], ...records.slice(0, 100).map((r) => r[headers[col]] ?? "")];
    const maxChars = Math.max(...sample.map((v) => String(v).length));
    const width = Math.max(10, Math.min(28, maxChars + 2));
    sheet.getRangeByIndexes(0, col, matrix.length, 1).format.columnWidth = width;
  }
  if (matrix.length > 1) {
    sheet.getRangeByIndexes(1, 0, matrix.length - 1, headers.length).format.borders = {
      insideHorizontal: { style: "thin", color: "#E5E7EB" },
    };
  }
  sheet.tabColor = i === 1 ? "#1F4E78" : (i >= 8 ? "#7A5195" : "#2A9D8F");
}

workbook.recalculate();

const inspect = await workbook.inspect({
  kind: "sheet,table",
  maxChars: 6000,
  tableMaxRows: 3,
  tableMaxCols: 8,
});
await fs.writeFile(path.join(base, "R7B3A_workbook_inspect.ndjson"), inspect.ndjson, "utf8");

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
await fs.writeFile(path.join(base, "R7B3A_workbook_error_scan.ndjson"), errors.ndjson, "utf8");

for (const sheetName of ["S1 Sources", "S3 A0-A2-M paths", "S6 Signal pairs", "S10 Claim ledger"]) {
  const preview = await workbook.render({ sheetName, range: "A1:H18", scale: 1.25, format: "png" });
  await fs.writeFile(path.join(base, `${sheetName.replaceAll(" ", "_")}_preview.png`), new Uint8Array(await preview.arrayBuffer()));
}

const file = await SpreadsheetFile.exportXlsx(workbook);
await file.save(output);
console.log(JSON.stringify({ output, sheets: 10 }));
