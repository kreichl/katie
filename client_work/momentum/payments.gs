/**
 * Opens the "Generate Payments" sidebar
 * Retrieves the bid amount from the selected row and passes it into the form.
 */
function showPaymentSidebar() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const row = parseInt(PropertiesService.getScriptProperties().getProperty("selectedRow"), 10);
    const bidAmount = sheet.getRange(row, 4).getValue(); // Column D: Bid Amount

    const template = HtmlService.createTemplateFromFile("PaymentSidebar");
    template.bidAmount = bidAmount;

    const html = template.evaluate().setTitle("Generate Payments");
    SpreadsheetApp.getUi().showSidebar(html);

    console.log(`Sidebar "Generate Payments" successfully opened for row ${row} with bid amount $${bidAmount}`);

  } catch (err) {
    const context = {
      function: "showPaymentSidebar",
      selectedRow: PropertiesService.getScriptProperties().getProperty("selectedRow")
    };
    const details = logError("showPaymentSidebar", err, context);
    showUserError("Error Opening Sidebar", "Unable to open the Generate Payments sidebar.", details);
  }
}

/**
 * Opens the "Generate Single Payments" sidebar
 * Retrieves the bid amount from the selected row and passes it into the form.
 */
function showSinglePaymentSidebar() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const row = parseInt(PropertiesService.getScriptProperties().getProperty("selectedRow"), 10);

    const project = sheet.getRange(row, 1).getValue();         // A
    const trade = sheet.getRange(row, 2).getValue();           // B
    const bidAmount = sheet.getRange(row, 4).getValue();       // D
    const subcontractor = sheet.getRange(row, 8).getValue();   // H

    const template = HtmlService.createTemplateFromFile("SinglePaymentSidebar");
    template.project = project;
    template.trade = trade;
    template.bidAmount = bidAmount;
    template.subcontractor = subcontractor;
    template.row = row;

    const html = template.evaluate().setTitle("Single Payment Setup");
    SpreadsheetApp.getUi().showSidebar(html);
  } catch (err) {
    const details = logError("showSinglePaymentSidebar", err);
    showUserError("Error Opening Sidebar", "Unable to open single payment entry.", details);
  }
}


/**
 * Opens the "Confirm Completed Payment" sidebar.
 */
function showCompletedPaymentSidebar() {
  try {
    const html = HtmlService.createHtmlOutputFromFile("CompletedPaymentSidebar")
      .setTitle("Confirm Completed Payment");
    SpreadsheetApp.getUi().showSidebar(html);

    console.log(`Sidebar "Confirm Completed Payment" successfully opened.`);

  } catch (err) {
    const details = logError("showCompletedPaymentSidebar", err);
    showUserError("Error Opening Sidebar", "Unable to open the Completed Payment sidebar.", details);
  }
}

/**
 * Handles the form submission from the Generate Payments sidebar.
 * Splits the total bid into scheduled payments and appends them to the sheet.
 */
function processSidebarForm(formData) {
  try {
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

    console.log(`Successfully added ${payments.length} scheduled payment(s) for "${project}" → ${subcontractor}`);
    return "Saved to Payments sheet";

  } catch (err) {
    const context = { formData };
    const details = logError("processSidebarForm", err, context);
    showUserError("Payment Processing Error", "Something went wrong while saving the payments.", details);
  }
}

/**
 * Supplies data to the CompletedPaymentSidebar.
 * Uses stored properties to return validation status and row details.
 */
function getSidebarData() {
  try {
    const props = PropertiesService.getDocumentProperties();
    const row = props.getProperty("row");

    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Scheduled Payments");
    const headers = sheet.getRange(3, 1, 1, sheet.getLastColumn()).getValues()[0];
    const rowData = sheet.getRange(row, 1, 1, headers.length).getValues()[0];

    const data = {};
    headers.forEach((header, index) => {
      data[header] = rowData[index];
    });

    const project = data["Project"];
    const trade = data["Trade"];
    const approved = data["Payment Approved?"];
    const actualDate = data["Actual Payment Date"];
    const actualAmount = data["Actual Amount"];
    const subcontractor = data["Subcontractor"];
    const description = data["Details"];

    if (!actualDate || !actualAmount || approved !== "Approved") {
      const issues = [];
      if (!actualDate) issues.push("• Missing 'Actual Payment Date'");
      if (!actualAmount) issues.push("• Missing 'Actual Amount'");
      if (approved !== "Approved") issues.push("• 'Payment Approved?' is not set to 'Approved'");

      return {
        valid: false,
        row,
        message: `The following issues must be resolved:<br>${issues.join('<br>')}`
      };
    }

    console.log(`Validated payment data for "${subcontractor}" on row ${row}`);
    return {
      valid: true,
      row,
      project,
      trade,
      actualDate: actualDate.toISOString(),
      actualAmount,
      subcontractor,
      description
    };

  } catch (err) {
    const context = { row: PropertiesService.getDocumentProperties().getProperty("row") };
    const details = logError("getSidebarData", err, context);
    showUserError("Sidebar Load Error", "Unable to load payment data for validation.", details);
    return { valid: false, row: "unknown", message: "Unexpected error. See logs." };
  }
}

function moveRowToProjectCosts() {
  try {
    const props = PropertiesService.getDocumentProperties();
    const row = props.getProperty("row");

    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Scheduled Payments");
    const headers = sheet.getRange(3, 1, 1, sheet.getLastColumn()).getValues()[0];
    const rowData = sheet.getRange(row, 1, 1, headers.length).getValues()[0];
    const data = {};
    headers.forEach((header, index) => {
      data[header] = rowData[index];
    });

    const project = data["Project"];
    const trade = data["Trade"];
    const actualDate = data["Actual Payment Date"];
    const actualAmount = data["Actual Amount"];
    const subcontractor = data["Subcontractor"];
    const description = data["Details"];

    const costsSheetName = `${project} - Costs`;
    const costsSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(costsSheetName);

    if (!costsSheet) {
      SpreadsheetApp.getUi().alert(`Sheet "${costsSheetName}" not found.`);
      return;
    }

    const newRow = [
      trade,        // Trade
      actualDate,   // Actual Payment Date
      actualAmount, // Actual Amount
      '',           // Assigned Invoice
      '',           // Status
      description,  // Description
      subcontractor,// Sub / Store
      '',           // Payment Type
      ''            // Check Number
    ];

    costsSheet.appendRow(newRow);

    console.log(`Moved payment for "${subcontractor}" from Scheduled Payments to "${costsSheetName}"`);

  } catch (err) {
    const context = { row: PropertiesService.getDocumentProperties().getProperty("row") };
    const details = logError("moveRowToProjectCosts", err, context);
    showUserError("Move Payment Error", "Could not move payment to project cost sheet.", details);
  }
}

function saveSinglePayment(dateString) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const tz = ss.getSpreadsheetTimeZone();
    const sheet = ss.getActiveSheet();
    const row = parseInt(PropertiesService.getScriptProperties().getProperty("selectedRow"), 10);
    const paymentsSheet = ss.getSheetByName("Scheduled Payments");

    const project = sheet.getRange(row, 1).getValue();         // A
    const trade = sheet.getRange(row, 2).getValue();           // B
    const bidAmount = sheet.getRange(row, 4).getValue();       // D
    const subcontractor = sheet.getRange(row, 8).getValue();   // H

    const parts = dateString.split("-");
    const year = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1; // Month is 0-based
    const day = parseInt(parts[2], 10);
    const estimatedDate = new Date(year, month, day, 12, 0, 0); // Noon prevents TZ shift

    const today = new Date();
    const daysUntil = Math.floor((estimatedDate - today) / (1000 * 60 * 60 * 24));

    paymentsSheet.appendRow([
      project,
      trade,
      subcontractor,
      estimatedDate,
      daysUntil,
      bidAmount
    ]);

    console.log(`✅ Saved scheduled payment for "${subcontractor}" on ${estimatedDate}`);
  } catch (err) {
    const details = logError("saveSinglePayment", err);
    showUserError("Save Failed", "Could not save payment row.", details);
  }
}