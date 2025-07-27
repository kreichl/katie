// Show sidebar to select project and mark archived
function showArchiveSidebar() {
  const html = HtmlService.createHtmlOutputFromFile("ArchiveSidebar")
    .setTitle("Archive Project");
  SpreadsheetApp.getUi().showSidebar(html);
}

function getActiveProjectsOnly() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Projects");
  const data = sheet.getRange("A4:C").getValues();
  const activeProjects = [];

  for (let i = 0; i < data.length; i++) {
    const name = data[i][0];
    const status = data[i][2];
    if (name && status === "Active") {
      activeProjects.push(name);
    }
  }

  return activeProjects;
}


function archiveProjectFromSidebar(project, newStatus) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Projects");
  const data = sheet.getDataRange().getValues();

  for (let r = 3; r < data.length; r++) {
    if (data[r][0] === project) { // Column A = Property Address
      sheet.getRange(r + 1, 3).setValue(newStatus); // Column C = Status
      updateProjectsNamedRange();
      moveAndHideTemplateSheets();
      return;
    }
  }

  throw new Error("Project not found: " + project);
}


