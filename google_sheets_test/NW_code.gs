/**
 * Triggered when a user edits the sheet.
 * Depending on the column edited, it either opens the Generate Payments sidebar,
 * or the Completed Payments sidebar, and stores the relevant row data.
 */
function handleEdit(e) {
  const sheet = e.source.getActiveSheet();

  // Read headers from row 3 (since rows 1–2 are reserved for UI)
  const headers = sheet.getRange(3, 1, 1, sheet.getLastColumn()).getValues()[0];
  const col = e.range.getColumn();
  const row = e.range.getRow();

  const generatePaymentsCol = headers.indexOf("Generate Payments") + 1;
  const paymentMadeCol = headers.indexOf("Payment Made?") + 1;

  // Case 1: Generate Payments clicked
  if (col === generatePaymentsCol && e.value === "TRUE") {
    PropertiesService.getScriptProperties().setProperty("selectedRow", row);
    showPaymentSidebar();
    return;
  }

  // Case 2: Payment Made? clicked
  if (col === paymentMadeCol && e.value === "TRUE") {
    const props = PropertiesService.getDocumentProperties();
    props.setProperties({
      row: row.toString(),
      sheetName: sheet.getName()
    });

    showCompletedPaymentSidebar();
    return;
  }
}

/**
 * Opens the "Generate Payments" sidebar
 * Retrieves the bid amount from the selected row and passes it into the form.
 */
function showPaymentSidebar() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const row = parseInt(PropertiesService.getScriptProperties().getProperty("selectedRow"), 10);

  const bidAmount = sheet.getRange(row, 4).getValue(); // Column D: Bid Amount

  const template = HtmlService.createTemplateFromFile("PaymentSidebar");
  template.bidAmount = bidAmount;

  const html = template.evaluate().setTitle("Generate Payments");
  SpreadsheetApp.getUi().showSidebar(html);
}

/**
 * Opens the "Confirm Completed Payment" sidebar.
 */
function showCompletedPaymentSidebar() {
  const html = HtmlService.createHtmlOutputFromFile("CompletedPaymentSidebar")
    .setTitle("Confirm Completed Payment");
  SpreadsheetApp.getUi().showSidebar(html);
}


/**
 * Handles the form submission from the Generate Payments sidebar.
 * Splits the total bid into scheduled payments and appends them to the sheet.
 */
function processSidebarForm(formData) {
  const row = parseInt(PropertiesService.getScriptProperties().getProperty("selectedRow"), 10);
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const paymentsSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Scheduled Payments");

  const project = sheet.getRange(row, 1).getValue();         // Column A
  const trade = sheet.getRange(row, 2).getValue();           // Column B
  const subcontractor = sheet.getRange(row, 8).getValue();   // Column H
  const bidAmount = sheet.getRange(row, 4).getValue();       // Column D

  const numPayments = parseInt(formData.numPayments, 10);
  const splitType = formData.splitType;
  const rawValues = formData.values.split(",").map(v => parseFloat(v.trim()));
  const baseDate = new Date(formData.startDate);

  // Convert input values to final dollar amounts
  const payments = (splitType === "percent")
    ? rawValues.map(p => bidAmount * (p / 100))
    : rawValues;

  for (let i = 0; i < payments.length; i++) {
    const estimatedDate = new Date(baseDate);
    estimatedDate.setDate(baseDate.getDate() + (i * 14)); // Space payments 2 weeks apart

    const today = new Date();
    const daysUntil = Math.floor((estimatedDate - today) / (1000 * 60 * 60 * 24));

    paymentsSheet.appendRow([
      project,
      trade,
      subcontractor,
      "",         // Estimated Payment Date (optional)
      "",         // Days Until (optional)
      payments[i]
    ]);
  }

  return "Saved to Payments sheet";
}

/**
 * Supplies data to the CompletedPaymentSidebar.
 * Uses stored properties to return validation status and row details.
 */
function getSidebarData() {
  try {
    const props = PropertiesService.getDocumentProperties();
    const row = Number(props.getProperty("row"));
    const sheetName = props.getProperty("sheetName");

    Logger.log("Fetching sidebar data for sheet: %s, row: %s", sheetName, row);

    if (!row || !sheetName) {
      Logger.log("Missing row or sheetName from props");
      return {
        valid: false,
        row: "N/A",
        message: "⚠️ Could not find row or sheet name in saved state."
      };
    }

    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
    if (!sheet) {
      Logger.log("Sheet not found: " + sheetName);
      return {
        valid: false,
        row,
        message: "⚠️ Sheet not found: " + sheetName
      };
    }

    const headers = sheet.getRange(3, 1, 1, sheet.getLastColumn()).getValues()[0];
    const rowData = sheet.getRange(row, 1, 1, headers.length).getValues()[0];

    Logger.log("Headers: %s", JSON.stringify(headers));
    Logger.log("Row data: %s", JSON.stringify(rowData));

    const data = Object.fromEntries(headers.map((key, i) => [key, rowData[i]]));
    Logger.log("Mapped row data: %s", JSON.stringify(data));

    const issues = [];
    if (!data["Actual Payment Date"]) issues.push("• Missing 'Actual Payment Date'");
    if (!data["Actual Amount"]) issues.push("• Missing 'Actual Amount'");
    if (data["Payment Approved?"] !== "Approved") issues.push("• 'Payment Approved?' is not set to 'Approved'");

    if (issues.length > 0) {
      return {
        valid: false,
        row,
        message: `⚠️ The following issues must be resolved:<br>${issues.join('<br>')}`
      };
    }

    return {
      valid: true,
      row,
      project: data["Project"],
      trade: data["Trade"],
      actualDate: data["Actual Payment Date"],
      actualAmount: data["Actual Amount"],
      subcontractor: data["Subcontractor"],
      description: data["Details"] || "N/A"
    };

  } catch (err) {
    Logger.log("getSidebarData ERROR: %s", err.toString());
    return {
      valid: false,
      row: "unknown",
      message: "❌ Error while loading sidebar: " + err.toString()
    };
  }
}

function moveRowToProjectCosts() {
  const props = PropertiesService.getDocumentProperties();
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName("Scheduled Payments");
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert('Sheet "Scheduled Payments" not found.');
    return;
  }

  const row = parseInt(props.getProperty("row"));
  const rowData = sheet.getRange(row, 1, 1, 11).getValues()[0];

  const project = rowData[0];
  const costsSheetName = `${project} - Costs`;
  const costsSheet = ss.getSheetByName(costsSheetName);

  if (!costsSheet) {
    SpreadsheetApp.getUi().alert(`Sheet "${costsSheetName}" not found.`);
    return;
  }

  const newRow = [
    rowData[1], // Trade
    rowData[6], // Actual Payment Date
    rowData[7], // Actual Amount
    '',         // Assigned Invoice
    '',         // Status
    rowData[10], // Description
    rowData[2], // Sub / Store
    '',         // Payment Type
    ''          // Check Number
  ];

  costsSheet.appendRow(newRow);
}

function reloadSidebar() {
  const html = HtmlService.createHtmlOutputFromFile('CompletedPaymentSidebar')
    .setTitle('Confirm Completed Payment')
    .setWidth(300);
  
  SpreadsheetApp.getUi().showSidebar(html);
}