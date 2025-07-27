function generateFinancialSummary() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName("Project Tracking") || ss.insertSheet("Project Tracking");

  // Clear and setup
  sheet.clear();
  sheet.setFrozenRows(3);

  // Add timestamp in Row 1
  const now = new Date();
  const formatted = Utilities.formatDate(now, ss.getSpreadsheetTimeZone(), "MM/dd/yyyy h:mm a");
  sheet.getRange("D1").setValue("Last updated: " + formatted);
  sheet.getRange("B1:C1").merge();
  sheet.getRange("D1:E1").merge();
  sheet.getRange("B1:E1").setFontFamily("Roboto");
  sheet.getRange("D1").setHorizontalAlignment("center").setVerticalAlignment("middle");

  const headers = [
    "Date",
    "Trade / Status",
    "Subcontractor",
    "Description",
    "Short Term Liabilities",
    "Long Term Debt",
    "Reimbursement",
    "Accounts Receivable"
  ];
  sheet.getRange(2, 1, 1, headers.length)
    .setValues([headers])
    .setFontFamily("Roboto")
    .setFontWeight("bold")
    .setBackground("#666666")
    .setFontColor("white");

  // TOTALS label (Row 3)
  sheet.getRange(3, 1).setValue("TOTALS").setFontWeight("bold").setFontFamily("Roboto");
  sheet.getRange(3, 1, 1, 8).setBackground("#fff2cc").setFontFamily("Roboto");

  const schedSheet = ss.getSheetByName("Scheduled Payments");
  const invSheet = ss.getSheetByName("Invoices");

  const schedHeader = schedSheet.getRange(3, 1, 1, schedSheet.getLastColumn()).getValues()[0];
  const schedData = schedSheet.getRange(4, 1, schedSheet.getLastRow() - 3, schedSheet.getLastColumn()).getValues();
  const schedByProject = groupBy(schedData, schedHeader.indexOf("Project"));

  const invHeader = invSheet.getRange(2, 1, 1, invSheet.getLastColumn()).getValues()[0];
  const invData = invSheet.getRange(3, 1, invSheet.getLastRow() - 2, invSheet.getLastColumn()).getValues();
  const invByProject = groupBy(invData, invHeader.indexOf("Project"));

  const getSchedCol = (name) => schedHeader.indexOf(name);
  const getInvCol = (name) => invHeader.indexOf(name);

  let row = 4;
  let dataStartRow = null;
  let dataEndRow = null;

  let totalRows = [];
  for (const project in schedByProject) {
    const schedRows = schedByProject[project];
    const invRows = invByProject[project] || [];

    const stl = -1 * sumByCategory(schedRows, "Short Term Liability", getSchedCol("Estimated Amount"), getSchedCol("Category"));
    const ltd = -1 * sumByCategory(schedRows, "Long Term Debt", getSchedCol("Estimated Amount"), getSchedCol("Category"));
    const reimb = sumByCategory(schedRows, "Reimbursement", getSchedCol("Estimated Amount"), getSchedCol("Category"));
    const ar = invRows
      .filter(r => r[getInvCol("Invoice Status")] && r[getInvCol("Invoice Status")].toLowerCase() !== "paid")
      .reduce((sum, r) => sum + (parseFloat(r[getInvCol("Invoiced Amount")]) || 0), 0);

    sheet.getRange(row, 1, 1, 8).setValues([[project, "", "", "", stl, ltd, reimb, ar]]);
    sheet.getRange(row, 1, 1, 8).setFontWeight("bold").setFontFamily("Roboto").setBackground("#d9e1f2");

    if (!dataStartRow) dataStartRow = row;
    dataEndRow = row;
    row++;

    const filteredInvoices = invRows.filter(inv => {
      const status = inv[getInvCol("Invoice Status")];
      return status && status.toLowerCase() !== "paid";
    }).sort((a, b) => {
      const d1 = new Date(a[getInvCol("Date Invoice Sent")] || "2100-01-01");
      const d2 = new Date(b[getInvCol("Date Invoice Sent")] || "2100-01-01");
      return d1 - d2;
    });

    if (filteredInvoices.length) {
      sheet.getRange(row, 1).setValue("Invoices").setFontStyle("italic").setFontColor("#555").setFontFamily("Roboto");
      sheet.getRange(row, 8).setValue(ar);
      row++;

      filteredInvoices.forEach(inv => {
        const date = inv[getInvCol("Date Invoice Sent")];
        const status = inv[getInvCol("Invoice Status")];
        const amount = parseFloat(inv[getInvCol("Invoiced Amount")]) || 0;

        sheet.getRange(row, 1, 1, 8).setValues([[date || "", status, "", "", "", "", "", amount]]);
        totalRows.push(row);
        sheet.getRange(row, 1, 1, 8).setFontFamily("Roboto");

        if (!dataStartRow) dataStartRow = row;
        dataEndRow = row;
        row++;
      });
    }

    const sortedSched = schedRows
      .filter(r => {
        const paid = r[getSchedCol("Payment Made?")];
        return !(paid && paid.toString().toLowerCase() === "true");
      })
      .sort((a, b) => {
        const d1 = new Date(a[getSchedCol("Estimated Payment Date")] || "2100-01-01");
        const d2 = new Date(b[getSchedCol("Estimated Payment Date")] || "2100-01-01");
        return d1 - d2;
      });


    if (sortedSched.length) {
      sheet.getRange(row, 1).setValue("Scheduled Payments").setFontStyle("italic").setFontColor("#555").setFontFamily("Roboto");
      row++;

      sortedSched.forEach(s => {
        const date = s[getSchedCol("Estimated Payment Date")];
        const trade = s[getSchedCol("Trade")];
        const sub = s[getSchedCol("Subcontractor")];
        const desc = s[getSchedCol("Details")];
        const category = s[getSchedCol("Category")];
        const amount = parseFloat(s[getSchedCol("Estimated Amount")]) || "";

        const line = [date, trade, sub, desc, "", "", "", ""];
        if (category === "Short Term Liability") line[4] = -1 * amount;
        else if (category === "Long Term Debt") line[5] = -1 * amount;
        else if (category === "Reimbursement") line[6] = amount;

        sheet.getRange(row, 1, 1, 8).setValues([line]);
        totalRows.push(row);
        sheet.getRange(row, 1, 1, 8).setFontFamily("Roboto");

        if (!dataStartRow) dataStartRow = row;
        dataEndRow = row;
        row++;
      });
    }

    sheet.getRange(row - 1, 1, 1, 8).setBorder(false, false, true, false, false, false, "black", SpreadsheetApp.BorderStyle.SOLID);
    row++;
  }

  // Updated: Format totals with correct range
  if (totalRows.length) {
    ["E", "F", "G", "H"].forEach((col, i) => {
      const ranges = totalRows.map(r => `${col}${r}`).join(",");
      sheet.getRange(3, 5 + i).setFormula(`=SUM(${ranges})`);
    });
  }

  sheet.getRange(3, 5, sheet.getLastRow() - 2, 4).setNumberFormat('_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)');
  sheet.getRange(2, 1, sheet.getLastRow(), 8).setFontFamily("Roboto");

  SpreadsheetApp.flush();
}

// === Helpers ===
function groupBy(rows, colIndex) {
  return rows.reduce((acc, row) => {
    const key = row[colIndex];
    if (!key) return acc;
    if (!acc[key]) acc[key] = [];
    acc[key].push(row);
    return acc;
  }, {});
}

function sumByCategory(rows, target, amountCol, categoryCol) {
  return rows
    .filter(r => r[categoryCol] === target)
    .reduce((sum, r) => sum + (parseFloat(r[amountCol]) || 0), 0);
}
