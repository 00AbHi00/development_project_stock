// I want to create a single csv file as date as a single parameter if the date is already contained in the file nothing to do, if not need to 
// Add new values
// Meaning that automatic_1.js scans if the data is already contained in the folder or not, automatic_2.js needs to load the value to 
// updated_csv if data is not present

const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, 'date');
const masterFilePath = path.join(__dirname, 'updated_data.csv');

function getBusinessDatesFromMaster() {
  if (!fs.existsSync(masterFilePath)) return new Set();

  const content = fs.readFileSync(masterFilePath, 'utf8');
  const lines = content.trim().split('\n').slice(1); // skip header
  const dates = lines.map(line => line.split(',')[1]); // Business Date
  return new Set(dates);
}

function getHeaderFromSampleFile() {
  const files = fs.readdirSync(dataDir).filter(f => f.endsWith('.csv'));
  if (files.length === 0) throw new Error('No sample file found');
  const sample = fs.readFileSync(path.join(dataDir, files[0]), 'utf8');
  return sample.split('\n')[0];
}

function ensureMasterHasHeader() {
  if (!fs.existsSync(masterFilePath)) {
    const header = getHeaderFromSampleFile();
    fs.writeFileSync(masterFilePath, header + '\n');
    console.log(' Header initialized in updated_data.csv');
  }
}

function appendNewData() {
  ensureMasterHasHeader();
  const existingDates = getBusinessDatesFromMaster();

  const files = fs.readdirSync(dataDir).filter(f => f.endsWith('.csv'));

  let appendedCount = 0;

  for (const file of files) {
    const fullPath = path.join(dataDir, file);
    const content = fs.readFileSync(fullPath, 'utf8');
    const lines = content.trim().split('\n');

    if (lines.length < 2) continue;

    const businessDate = lines[1].split(',')[1];

    if (existingDates.has(businessDate)) {
    //   console.log(`Skipped ${file} — already in master`);
      continue;
    }

    const dataLines = lines.slice(1).join('\n');
    fs.appendFileSync(masterFilePath, dataLines + '\n');
    // console.log(`Appended ${file}`);
    appendedCount++;
  }

  if (appendedCount === 0) {
    console.log('No new data to append. Master is up to date.');
  } else {
    console.log(`Appended ${appendedCount} new files to master.`);
  }
}

appendNewData();
