const fs = require('fs');
const csvParser = require('csv-parser');
const path = require('path');

// Function to check if the directory exists and create it if not
function ensureDirectoryExistence(filePath) {
  const dirname = path.dirname(filePath);
  if (!fs.existsSync(dirname)) {
    fs.mkdirSync(dirname, { recursive: true }); // This will create the directory and any intermediate directories
  }
}



// Function to convert CSV to JSON
function convertCSVtoJSON(csvFilePath, jsonFilePath) {
  const data = [];
  let totalAmt = 0;
  let totalQty = 0;

  fs.createReadStream(csvFilePath)
    .pipe(csvParser())
    .on('data', (row) => {
      // Extract relevant information from each row
      const tradedQty = parseFloat(row['Total Traded Quantity']);
      const tradedValue = parseFloat(row['Total Traded Value']);
      const closePrice = parseFloat(row['Close Price']);
      const prevClosePrice = parseFloat(row['Previous Day Close Price']);
      const symbol = row['Symbol'];
      const securityName = row['Security Name'];

      // Add to the total amounts and quantities
      totalAmt += tradedValue;
      totalQty += tradedQty;

      // Build the JSON data for each record
      data.push({
        company: {
          name: securityName,
          code: symbol,
          cat: null, // Assuming "cat" is not available in the data
        },
        price: {
          max: parseFloat(row['High Price']),
          min: parseFloat(row['Low Price']),
          close: closePrice,
          prevClose: prevClosePrice,
          diff: closePrice - prevClosePrice, // Price difference
        },
        numTrans: parseInt(row['Total Trades'], 10),
        tradedShares: tradedQty,
        amount: tradedValue,
      });
    })
    .on('end', () => {
      // Final metadata and data structure
      const result = {
        metadata: {
          totalAmt: totalAmt,
          totalQty: totalQty,
          totalTrans: data.length, // Count of total records (transactions)
        },
        data: data,
      };

      // Write the JSON to the file
      fs.writeFileSync(jsonFilePath, JSON.stringify(result, null, 2));
      console.log('CSV to JSON conversion completed!');
    });
}

// Use the function
const csvFilePath = `Today's Price - 2025-07-08.csv`; // Path to the input CSV file

fileName= csvFilePath.slice(16).replace('csv','json')
const jsonFilePath = `date/${fileName}`; // Path where you want the output JSON

// Ensure the directory exists before writing the file
ensureDirectoryExistence(jsonFilePath);
convertCSVtoJSON(csvFilePath, jsonFilePath);
