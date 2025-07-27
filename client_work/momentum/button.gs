function goToTOC() {
  const targetSheetId = 1787546266;
  const sheets = SpreadsheetApp.getActiveSpreadsheet().getSheets();

  const targetSheet = sheets.find(sheet => sheet.getSheetId() === targetSheetId);

  if (targetSheet) {
    SpreadsheetApp.getActiveSpreadsheet().setActiveSheet(targetSheet);
  } else {
    SpreadsheetApp.getUi().alert("Sheet with ID '" + targetSheetId + "' not found.");
  }
}

function updateAllTables() {
  combineProjectInvoices()
  generateFinancialSummary()
}