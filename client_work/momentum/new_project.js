function testCreateNewProjectSheets() {
  const testAddress = "TEST Project 022";
  createNewProjectSheets(testAddress);
}

function createNewProjectSheets(propertyAddress) {
  const functionName = "createNewProjectSheets";
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  try {
    console.log(`[${functionName}] Starting creation for: "${propertyAddress}"`);

    const summarySheetName = `${propertyAddress} - Summary`;
    const costsSheetName = `${propertyAddress} - Costs`;

    // Early check for duplicate sheets
    if (ss.getSheetByName(summarySheetName) || ss.getSheetByName(costsSheetName)) {
      throw new Error(`A project with this name already exists (duplicate sheet name).`);
    }

    const summaryTemplate = ss.getSheetByName("TEMPLATE - Summary");
    const costsTemplate = ss.getSheetByName("TEMPLATE - Costs");
    console.log(`[${functionName}] Templates loaded`);

    const slug = propertyAddress.replace(/[^\w\s]/g, '').replace(/\s+/g, '').trim();

    const summarySheet = summaryTemplate.copyTo(ss).setName(summarySheetName);
    console.log(`[${functionName}] Created summary sheet: "${summarySheetName}"`);
    removeTemplateNamedRanges(summarySheet);

    const costsSheet = costsTemplate.copyTo(ss).setName(costsSheetName);
    console.log(`[${functionName}] Created costs sheet: "${costsSheetName}"`);
    removeTemplateNamedRanges(costsSheet);

    const colorHex = "#f4c542"; // yellow-orange

    // Move and recolor summary sheet
    ss.setActiveSheet(summarySheet);
    ss.moveActiveSheet(ss.getSheets().length);
    summarySheet.setTabColor(colorHex);

    // Move and recolor costs sheet
    ss.setActiveSheet(costsSheet);
    ss.moveActiveSheet(ss.getSheets().length);
    costsSheet.setTabColor(colorHex);

    console.log(`[${functionName}] Moved new sheets to end of workbook and applied tab color`);

    ss.setNamedRange(`Job_Costs_${slug}`, costsSheet.getRange("A3:I400"));
    ss.setNamedRange(`Detailed_Invoices_${slug}`, summarySheet.getRange("B52:O98"));
    ss.setNamedRange(`Projected_Costs_${slug}`, summarySheet.getRange("B3:H49"));
    console.log(`[${functionName}] Named ranges created`);

    replaceNamedRangeReferences(summarySheet, slug);
    replaceNamedRangeReferences(costsSheet, slug);
    console.log(`[${functionName}] Replaced all named range references`);

    recreatePivotTable(summarySheet, costsSheet, slug);

    summarySheet.getRange("C1").setValue(`${propertyAddress} - Summary`);
    costsSheet.getRange("B1").setValue(`${propertyAddress} - Job Costs`);
    console.log(`[${functionName}] Sheet headers updated to reflect property name "${propertyAddress}"`);

    // Add Protections
    addSheetProtections(costsSheet, "1:3", "Job Costs Proections");
    const summaryProtectedRanges = [
      "U102:Y111",
      "G4:H48",
      "R102:R111",
      "D53:D97",
      "O53:P97",
      "A:B",
      "I98:I101",
      "I49:S52",
      "S115",
      "A100:P200"
    ];
    addSheetProtections(summarySheet, summaryProtectedRanges, "Summary Protections");

    updateTOC(propertyAddress, summarySheetName, costsSheetName);
    updateProjectsNamedRange();
    SpreadsheetApp.flush();

    moveAndHideTemplateSheets()

    console.log(`[${functionName}] Project setup complete for "${propertyAddress}"`);
  } catch (err) {
    const context = { propertyAddress };
    const details = logError(functionName, err, context);
    showUserError("Project Setup Failed", "Something went wrong while creating the new project.", details);
  }
}

function addSheetProtections(sheet, ranges, description = "Protected Range") {
  const functionName = "addSheetProtections";
  const sheetName = sheet.getName();
  
  try {
    SpreadsheetApp.flush();
    Utilities.sleep(1000); // Add delay to ensure sheet operations complete
    
    // Convert single range to array for consistent handling
    const rangeArray = Array.isArray(ranges) ? ranges : [ranges];
    
    rangeArray.forEach((rangeNotation, index) => {
      // Remove any existing protections on this range first
      const existingProtections = sheet.getProtections(SpreadsheetApp.ProtectionType.RANGE);
      existingProtections.forEach(protection => {
        const protectedRange = protection.getRange();
        if (protectedRange && protectedRange.getA1Notation() === rangeNotation) {
          console.log(`[${functionName}] Removing existing protection on ${sheetName}: ${protectedRange.getA1Notation()}`);
          protection.remove();
        }
      });
      
      // Apply new protection
      const targetRange = sheet.getRange(rangeNotation);
      console.log(`[${functionName}] Protecting range on ${sheetName}: ${targetRange.getA1Notation()}`);
      
      const protection = targetRange.protect();
      protection.setWarningOnly(true);
      protection.setDescription(`${description} ${index > 0 ? `(${index + 1})` : ''}`);
      
      console.log(`[${functionName}] Protection applied successfully to ${sheetName}: ${rangeNotation}`);
    });
    
  } catch (protectionError) {
    console.error(`[${functionName}] Protection failed on ${sheetName}:`, protectionError);
    throw protectionError; // Re-throw to maintain error handling in calling function
  }
}

function updateTOC(projectName, summarySheetName, costsSheetName) {
  const functionName = "updateTOC";
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  try {
    const tocSheet = ss.getSheetByName("TOC");
    if (!tocSheet) throw new Error(`Sheet "TOC" not found.`);

    const startRow = 12;  // Project list starts from row 12
    const projectColumn = 1; // Column A
    const summaryColumn = 2; // Column B
    const costsColumn = 3;   // Column C

    const lastRow = tocSheet.getLastRow();

    let row = startRow;
    while (tocSheet.getRange(row, projectColumn).getValue() !== "" && row <= lastRow) {
      row++;
    }

    tocSheet.getRange(row, projectColumn).setValue(projectName);
    tocSheet.getRange(row, summaryColumn).setFormula(`=HYPERLINK("#gid=${getSheetId(summarySheetName)}", "Summary")`);
    tocSheet.getRange(row, costsColumn).setFormula(`=HYPERLINK("#gid=${getSheetId(costsSheetName)}", "Job Costs")`);

    console.log(`[${functionName}] TOC updated with new project "${projectName}" at row ${row}`);

  } catch (err) {
    const context = { projectName, summarySheetName, costsSheetName };
    const details = logError(functionName, err, context);
    showUserError("TOC Update Failed", "Could not add project to the TOC.", details);
  }
}

function getSheetId(sheetName) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
  return sheet.getSheetId();
}

function updateProjectsNamedRange() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const projectSheet = ss.getSheetByName("Projects");
  const dataSheet = ss.getSheetByName("Data");

  const data = projectSheet.getRange("A4:C").getValues();

  const activeProjects = [];
  const allProjects = [];

  for (let i = 0; i < data.length; i++) {
    const name = data[i][0];
    const status = data[i][2];
    if (name) {
      allProjects.push([name]);
      if (status === "Active" || status === "Estimate") {
        activeProjects.push([name]);
      }
    }
  }

  if (projectSheet.getRange("A3").getValue() !== "Property Address") {
    throw new Error('Expected header "Property Address" in cell A3');
  }

  // ✅ Write active projects into Data!B1 downward
  dataSheet.getRange("B1:B").clearContent();
  if (activeProjects.length > 0) {
    dataSheet.getRange(1, 2, activeProjects.length, 1).setValues(activeProjects);
  } else {
    dataSheet.getRange("B1").setValue(""); // Optional: clear fallback cell
  }

  // ✅ Update named ranges
  const namedRanges = ss.getNamedRanges();
  const namesToDelete = ["Projects", "Projects_ALL"];
  namedRanges.forEach(namedRange => {
    if (namesToDelete.includes(namedRange.getName())) {
      namedRange.remove();
    }
  });

  // ✅ New: Set "Projects" named range to the data sheet column B
  if (activeProjects.length > 0) {
    const activeRange = dataSheet.getRange(1, 2, activeProjects.length, 1); // Data!B1:B
    ss.setNamedRange("Projects", activeRange);
  } else {
    ss.setNamedRange("Projects", dataSheet.getRange("B1"));
  }

  // "Projects_ALL" still uses original Projects sheet column A
  if (allProjects.length > 0) {
    const allRange = projectSheet.getRange(4, 1, allProjects.length, 1);
    ss.setNamedRange("Projects_ALL", allRange);
  } else {
    ss.setNamedRange("Projects_ALL", projectSheet.getRange("A4"));
  }
}

function showNewProjectSidebar() {
  const html = HtmlService.createHtmlOutputFromFile("NewProjectSidebar")
    .setTitle("Add New Project");
  SpreadsheetApp.getUi().showSidebar(html);
}

function handleNewProjectSubmission(data) {
  if (isDuplicatePropertyAddress(data.propertyAddress)) {
    throw new Error("A project with this property address already exists.");
  }

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Projects");
  sheet.appendRow([
    data.propertyAddress,
    data.city,
    data.status,
    data.type,
    data.owner,
    data.startDate,
    data.finishDate,
    "" // Notes
  ]);

  createNewProjectSheets(data.propertyAddress);
}

function isDuplicatePropertyAddress(address) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Projects");
  const values = sheet.getRange("A4:A").getValues().flat().filter(v => v); // ignore blanks
  return values.includes(address.trim());
}

function replaceNamedRangeReferences(sheet, slug) {
  const range = sheet.getDataRange();
  const formulas = range.getFormulas();
  const functionName = "replaceNamedRangeReferences";

  const updated = formulas.map((row, rowIndex) =>
    row.map((cell, colIndex) => {
      const r = rowIndex + 1;
      const c = colIndex + 1;
      const a1 = sheet.getRange(r, c).getA1Notation();

      const original = cell || ""; // Coerce null to empty string

      if (
        original.includes("Job_Costs_TEMPLATE") ||
        original.includes("Detailed_Invoices_TEMPLATE") ||
        original.includes("Projected_Costs_TEMPLATE")
      ) {

        const updatedCell = original
          .replace(/Job_Costs_TEMPLATE/g, `Job_Costs_${slug}`)
          .replace(/Detailed_Invoices_TEMPLATE/g, `Detailed_Invoices_${slug}`)
          .replace(/Projected_Costs_TEMPLATE/g, `Projected_Costs_${slug}`);

        console.log(`[${functionName}] Replacing formula in ${a1}: ${original} → ${updatedCell}`);
        return updatedCell;
      }

      return original; // Return original even if not matched
    })
  );

  updated.forEach((row, rowIndex) => {
    row.forEach((formula, colIndex) => {
      if (formulas[rowIndex][colIndex] !== formula) {
        const targetCell = sheet.getRange(rowIndex + 1, colIndex + 1);
        targetCell.setFormula(formula);
      }
    });
  });

  console.log(`[${functionName}] All named range formulas replaced for slug "${slug}"`);
}

function removeTemplateNamedRanges(sheet) {
  const functionName = "removeTemplateNamedRanges";
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const namedRanges = ss.getNamedRanges();
  const sheetName = sheet.getName();
  let removedCount = 0;

  namedRanges.forEach(range => {
    const rangeName = range.getName();
    let targetSheet;

    try {
      targetSheet = range.getRange().getSheet();
    } catch (err) {
      targetSheet = null;
    }

    const isTemplate = /_TEMPLATE$/.test(rangeName);
    const isOnTargetSheet = targetSheet && targetSheet.getName() === sheetName;

    if (isTemplate && isOnTargetSheet) {
      range.remove();
      removedCount++;
    }
  });

  console.log(`[${functionName}] Removed ${removedCount} template named range(s) from "${sheetName}"`);
}

function recreatePivotTable(summarySheet, costsSheet, slug) {
  const functionName = "recreatePivotTable";
  try {
    // Step 1: Clear old pivot table cell range
    const pivotAnchor = summarySheet.getRange("B100"); // Update if needed
    pivotAnchor.clearContent(); // Remove any old pivot metadata

    // Step 2: Define source range for the pivot
    const sourceRange = costsSheet.getRange("A3:I400"); // Adjust columns if necessary

    // Step 3: Create the pivot table
    const pivotTable = pivotAnchor.createPivotTable(sourceRange);

    // Step 4: Configure pivot settings
    pivotTable.addRowGroup(1); // Trade (column A)
    pivotTable.addRowGroup(7); // Sub / Store (column G)
    pivotTable.addColumnGroup(4); // Assigned Invoice (column D)
    pivotTable.addPivotValue(3, SpreadsheetApp.PivotTableSummarizeFunction.SUM); // Amount (Job Costs per Invoice, column C)

    console.log(`[${functionName}] Pivot table created successfully for slug "${slug}"`);

  } catch (err) {
    console.error(`[${functionName}] Error creating pivot for "${slug}":`, err);
    throw err; // Bubble it up if needed
  }
}


