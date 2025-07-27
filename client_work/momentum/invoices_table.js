function combineProjectInvoices() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheets = ss.getSheets();
  const masterSheetName = "Invoices";

  // Load list of active projects from named range "Projects"
  const activeProjectRange = ss.getRangeByName("Projects");
  const activeProjects = new Set(activeProjectRange.getValues().flat().filter(name => name && typeof name === "string"));

  // Create or clear master sheet
  let masterSheet = ss.getSheetByName(masterSheetName);
  if (!masterSheet) {
    masterSheet = ss.insertSheet(masterSheetName);
  } else {
    masterSheet.clearContents();
  }

  const masterData = [];
  const headers = ["Project", "Client Invoice", "Invoice Status", "Invoice Number", "Job Costs", "Invoiced Amount", "Date Invoice Sent", "Date Paid"];

  sheets.forEach(sheet => {
    const sheetName = sheet.getName();
    if (!sheetName.endsWith(" - Summary")) return;

    const projectName = sheetName.replace(" - Summary", "");
    if (!activeProjects.has(projectName)) return;

    const data = sheet.getDataRange().getValues();

    let startRow = -1, startCol = -1;

    // Find "Client Invoice" header
    outerLoop:
    for (let r = 0; r < data.length; r++) {
      for (let c = 0; c < data[r].length; c++) {
        if (data[r][c] === "Client Invoice") {
          startRow = r;
          startCol = c;
          break outerLoop;
        }
      }
    }

    if (startRow === -1 || startCol === -1) return;

    let row = startRow + 1;
    while (row < data.length) {
      const currentRow = data[row].slice(startCol, startCol + 8);
      const firstCell = currentRow[0];
      const isEmpty = currentRow.every(cell => cell === "" || cell === null);
      const isTotalRow = firstCell && firstCell.toString().trim().toLowerCase() === "totals";
      const isFirstCellBlank = !firstCell || firstCell.toString().trim() === "";

      if (isEmpty || isTotalRow || isFirstCellBlank) break;

      masterData.push([projectName, ...currentRow]);
      row++;
    }

  });

  masterSheet.getFilter()?.remove();

  // Write results
  masterSheet.getRange("A2:H2").setValues([headers]);
  if (masterData.length > 0) {
    masterSheet.getRange(3, 1, masterData.length, 8).setValues(masterData);
  } else {
    masterSheet.getRange("C1").setValue("No invoice data found.");
  }

  const lastRow = masterSheet.getLastRow();

  // Formatting
  masterSheet.getRange("A2:H2").createFilter();
  masterSheet.getBandings().forEach(b => b.remove());
  const band = masterSheet.getRange(2, 1, lastRow - 1, 8).applyRowBanding();
  band.setHeaderRowColor("#666666");
  band.setFirstRowColor("#f2f2f2");
  band.setSecondRowColor("#e0e0e0");

  const now = new Date();
  const formatted = Utilities.formatDate(now, ss.getSpreadsheetTimeZone(), "MM/dd/yyyy h:mm a");
  masterSheet.getRange("D1").setValue("Last updated: " + formatted);
}
