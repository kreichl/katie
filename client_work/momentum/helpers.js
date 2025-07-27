function handleEdit(e) {}
// function handleEdit(e) {
//   try {
//     const sheet = e.source.getActiveSheet();
//     const sheetName = sheet.getName();
//     const headers = sheet.getRange(3, 1, 1, sheet.getLastColumn()).getValues()[0];
//     const col = e.range.getColumn();
//     const row = e.range.getRow();
//     const editedHeader = headers[col - 1] || `Column ${col}`;
//     const newValue = e.value;
//     const oldValue = e.oldValue;
//     const user = Session.getActiveUser().getEmail() || "Unknown User";

//     // Log every edit
//     console.log(
//       `📝 Edit made by ${user} on sheet "${sheetName}":\n` +
//       `- Row: ${row}, Column: ${col} (${editedHeader})\n` +
//       `- Old Value: ${oldValue || "(empty)"}\n` +
//       `- New Value: ${newValue || "(empty)"}`
//     );

//     const generatePaymentsCol = headers.indexOf("Generate Payments") + 1;
//     const paymentMadeCol = headers.indexOf("Payment Made?") + 1;

//     // Case 1: Generate Payments clicked
//     if (col === generatePaymentsCol && newValue === "TRUE") {
//       PropertiesService.getScriptProperties().setProperty("selectedRow", row);
//       console.log(`⚡ Trigger: "Generate Payments" clicked on row ${row} in sheet "${sheetName}" by ${user}`);
//       showSinglePaymentSidebar();
//       return;
//     }

//     // Case 2: Payment Made? clicked
//     if (col === paymentMadeCol && newValue === "TRUE") {
//       PropertiesService.getDocumentProperties().setProperty("row", row.toString());
//       console.log(`✅ Trigger: "Payment Made?" marked TRUE on row ${row} in sheet "${sheetName}" by ${user}`);
//       showCompletedPaymentSidebar();
//       return;
//     }

//     // Case 3: Project Status updated in Projects sheet
//     if (sheetName === "Projects" && editedHeader === "Status") {
//       const projectName = sheet.getRange(row, 1).getValue(); // Column A = Project name
//       const ss = SpreadsheetApp.getActiveSpreadsheet();
//       const summarySheet = ss.getSheetByName(`${projectName} - Summary`);
//       const costsSheet = ss.getSheetByName(`${projectName} - Costs`);
//       const colorHex = "#f4c542"; // yellow-orange
//       const ui = SpreadsheetApp.getUi();

//       // ARCHIVE
//       if (newValue === "Completed" || newValue === "On Hold") {
//         const response = ui.alert(
//           "Archive Project?",
//           `Changing the status to "${newValue}" will archive the project by hiding its sheets. This will NOT delete any data.\n\nWould you like to proceed?`,
//           ui.ButtonSet.OK_CANCEL
//         );

//         if (response === ui.Button.OK) {
//           console.log(`📦 Trigger: Archiving project "${projectName}" as "${newValue}" by ${user}`);
//           updateProjectsNamedRange();
//           moveAndHideTemplateSheets();
//         } else {
//           sheet.getRange(row, col).setValue(oldValue || "Active");
//           console.log(`❌ User cancelled archive action. Status reverted by ${user}`);
//         }

//         return;
//       }

//       // REACTIVATE
//       if (newValue === "Active" || newValue === "Estimate") {
//         const response = ui.alert(
//           "Reactivate Project?",
//           `Changing the status to "${newValue}" will unhide and reactivate the project sheets.\n\nProceed?`,
//           ui.ButtonSet.OK_CANCEL
//         );

//         if (response === ui.Button.OK) {
//           console.log(`🔓 Trigger: Reactivating project "${projectName}" as "${newValue}" by ${user}`);
//           updateProjectsNamedRange();

//           if (summarySheet) {
//             if (summarySheet.isSheetHidden()) summarySheet.showSheet();
//             summarySheet.setTabColor(colorHex);
//           }
//           if (costsSheet) {
//             if (costsSheet.isSheetHidden()) costsSheet.showSheet();
//             costsSheet.setTabColor(colorHex);
//           }

//         } else {
//           sheet.getRange(row, col).setValue(oldValue || "Active");
//           console.log(`❌ User cancelled reactivation. Status reverted by ${user}`);
//         }

//         return;
//       }
//     }

//   } catch (err) {
//     const context = {
//       sheet: e.source.getActiveSheet().getName(),
//       row: e.range.getRow(),
//       column: e.range.getColumn(),
//       value: e.value,
//       user: Session.getActiveUser().getEmail()
//     };
//     const details = logError("handleEdit", err, context);
//     showUserError("Sheet Edit Error", "Something went wrong while responding to your edit.", details);
//   }
// }


function moveAndHideTemplateSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const tocSheet = ss.getSheetByName('TOC');
  const projectsSheet = ss.getSheetByName('Projects');
  const darkPurple = '#5b3b84';
  const hideStatuses = ['Completed', 'On Hold'];

  if (!projectsSheet || !tocSheet) {
    console.warn('[moveAndHideTemplateSheets] Projects or TOC sheet missing.');
    return;
  }

  const data = projectsSheet.getRange('A4:C').getValues();

  let totalHidden = 0;

  data.forEach(row => {
    const [propertyAddress, , status] = row;
    if (!propertyAddress || !hideStatuses.includes(status)) return;

    ['Summary', 'Costs'].forEach(type => {
      const sheetName = `${propertyAddress} - ${type}`;
      const sheet = ss.getSheetByName(sheetName);

      if (sheet) {
        try {
          sheet.setTabColor(darkPurple);
          SpreadsheetApp.flush(); // Apply formatting

          ss.setActiveSheet(sheet);
          SpreadsheetApp.flush(); // Ensure active context

          ss.moveActiveSheet(ss.getSheets().length);
          SpreadsheetApp.flush(); // Wait for move

          sheet.hideSheet();
          SpreadsheetApp.flush(); // Ensure hide

          totalHidden++;
          console.log(`[moveAndHideTemplateSheets] Moved & hid "${sheetName}"`);
        } catch (err) {
          console.error(`[moveAndHideTemplateSheets] Error handling "${sheetName}": ${err}`);
        }
      } else {
        console.warn(`[moveAndHideTemplateSheets] Sheet not found: "${sheetName}"`);
      }
    });
  });

  // Move & hide utility sheets
  const utilitySheets = ['TEMPLATE - Summary', 'TEMPLATE - Costs', 'Data', 'Error Log'];

  utilitySheets.forEach(name => {
    const sheet = ss.getSheetByName(name);
    if (sheet) {
      try {
        ss.setActiveSheet(sheet);
        SpreadsheetApp.flush();
        ss.moveActiveSheet(ss.getSheets().length);
        sheet.hideSheet();
        SpreadsheetApp.flush();
        console.log(`[moveAndHideTemplateSheets] Moved & hid utility sheet: "${name}"`);
      } catch (err) {
        console.error(`[moveAndHideTemplateSheets] Error with utility sheet "${name}": ${err}`);
      }
    }
  });

  // Return to TOC
  ss.setActiveSheet(tocSheet);
  console.log(`[moveAndHideTemplateSheets] Finished. Total project sheets hidden: ${totalHidden}`);
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("Project Tools")
    .addItem("Add New Project", "showNewProjectSidebar")
    // .addItem("Archive Project", "showArchiveSidebar")
    .addItem("Hide Inactive Sheets", "moveAndHideTemplateSheets")
    .addItem("Authorize Scripts", "showAuthorizeSidebar")
    .addItem("About Financials Toolkit", "showAboutDialog")
    .addToUi();
}

function showAboutDialog() {
  const html = HtmlService.createHtmlOutput(`
    <div style="font-family: Roboto, sans-serif; padding: 20px; max-width: 400px;">
      <h2 style="margin: 0; font-size: 20px;">Financials Toolkit</h2>
      <p style="margin: 8px 0;">Built by <strong>CapraFlow</strong></p>
      <p style="margin: 8px 0;">Version: 1.0.0</p>
      <p style="margin: 8px 0;">Website: <a href="https://capraflow.com" target="_blank">capraflow.com</a></p>
      <p style="margin: 8px 0;">Contact: <a href="mailto:katie@capraflow.com">katie@capraflow.com</a></p>
      <div style="margin-top: 20px; text-align: center;">
        <img src="https://capraflow.com/logo.png" alt="CapraFlow Logo" style="height: 40px;">
      </div>
    </div>
  `)
  .setWidth(420)
  .setHeight(280);

  SpreadsheetApp.getUi().showModalDialog(html, "About");
}

function showAuthorizeSidebar() {
  const html = HtmlService.createHtmlOutputFromFile("AuthorizeSidebar")
    .setTitle("Script Access");
  SpreadsheetApp.getUi().showSidebar(html);
}

/**
 * Dummy function to trigger OAuth flow.
 * Called via a sidebar button to request user authorization.
 */
function authorizeScript() {
  // This function does nothing — it's just here to trigger the OAuth prompt
  return true;
}


function deleteTestProjectSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheets = ss.getSheets();
  const functionName = "deleteTestProjectSheets";
  let deletedCount = 0;

  sheets.forEach(sheet => {
    const name = sheet.getName();
    if (/TEST Project/i.test(name)) {
      console.log(`[${functionName}] Deleting sheet: "${name}"`);
      ss.deleteSheet(sheet);
      deletedCount++;
    }
  });

  console.log(`[${functionName}] ✅ Deleted ${deletedCount} test sheet(s).`);
}

/**
 * Utility function to log detailed errors and show user-friendly messages
 */
function logError(functionName, error, context = {}) {
  const timestamp = new Date().toISOString();
  const errorDetails = {
    timestamp,
    function: functionName,
    error: error.toString(),
    stack: error.stack,
    context
  };
  
  // Log to console (visible in Apps Script editor)
  console.error(`[${timestamp}] ERROR in ${functionName}:`, errorDetails);
  
  // Try to log to a dedicated error sheet
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let errorSheet = ss.getSheetByName('Error Log');
    
    if (!errorSheet) {
      errorSheet = ss.insertSheet('Error Log');
      errorSheet.getRange(1, 1, 1, 6).setValues([['Timestamp', 'Function', 'Error', 'Stack Trace', 'Context', 'User Email']]);
    }
    
    // Use try-catch for getting user email since it may fail in some contexts
    let userEmail = 'Unknown';
    try {
      userEmail = Session.getActiveUser().getEmail() || 'Unknown';
    } catch (emailError) {
      console.warn('Could not get user email:', emailError.toString());
      userEmail = 'Permission Denied';
    }
    
    errorSheet.appendRow([
      timestamp,
      functionName,
      error.toString(),
      error.stack || 'No stack trace',
      JSON.stringify(context),
      userEmail
    ]);
    
    console.log('Successfully logged error to Error Log sheet');
  } catch (logError) {
    console.error('Failed to log to error sheet:', logError);
  }
  
  return errorDetails;
}

/**
 * Show user-friendly error message
 */
function showUserError(title, message, technicalDetails = null) {
  const ui = SpreadsheetApp.getUi();
  let fullMessage = message;
  
  if (technicalDetails) {
    fullMessage += '\n\nTechnical Details:\n' + JSON.stringify(technicalDetails, null, 2);
  }
  
  ui.alert(title, fullMessage, ui.ButtonSet.OK);
}