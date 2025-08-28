// Checking if the files are upto date
// If the files are not upto date, new files are downloaded


const fs = require('fs')
const path = require('path')
const { setTimeout } = require("node:timers/promises");
const puppeteer= require('puppeteer');

const directoryPath = path.join(__dirname, 'date')

const TodaysDate= new Date()

// Date and differnce
abh_map=[new Date(),5000]


function addOneDay(date) {
  const newDate = new Date(date);
  newDate.setDate(newDate.getDate() + 1);
  return newDate;
}



function extractDateParts(date) {
    return (`${date.getFullYear()},${date.getMonth() + 1},${date.getDate()}`)
}

function getLastDate(list){
    // Month starts form 0
    tempDate=new Date(list[0],list[1]-1,list[2])
    differenceInDateInDays= (Math.round((TodaysDate-tempDate)/ (1000 * 60 * 60 * 24)))
    // console.log(differenceInDateInDays,"<",abh_map[1])

    if(differenceInDateInDays<abh_map[1])
    {
        abh_map[0]=tempDate 
        abh_map[1]=differenceInDateInDays
    }
}

// Read all files in the directory
 
async function processFiles() {
    try {
        const files = await fs.promises.readdir(directoryPath);

        for (const fileName of files) {
            const fullPath = path.join(directoryPath, fileName);
            const stat = await fs.promises.stat(fullPath);

            if (stat.isFile()) {
                let cleanName = fileName.replace("Today's Price - ", '').replace('.csv', '');
                getLastDate(cleanName.split('-'));
            }
        }
        // Date to fetch from is the date value + 1

        // console.log("Final abh_map:", abh_map);
        // Return at last
        console.log(extractDateParts(abh_map[0]),extractDateParts(TodaysDate))

        console.log(abh_map[0])


        if (extractDateParts(abh_map[0])==extractDateParts(TodaysDate)){
            console.log('Already upto Date')
            process.exit()
        }


        return abh_map

    } catch (err) {
        console.error("Error reading directory:", err.message);
        return abh_map
    }
}

// Function to format date as MM/DD/YYYY
function formatDate(date) {
  if (!(date instanceof Date) || isNaN(date.getTime())) {
    throw new Error("Invalid date passed to formatDate");
  }
  const month = `0${date.getMonth() + 1}`.slice(-2);
  const day = `0${date.getDate()}`.slice(-2);
  const year = date.getFullYear();
  return `${month}/${day}/${year}`;
}



// Function to get an array of dates between start and end date
function getDatesInRange(startDate, endDate) {
  const dates = [];
  let currentDate = new Date(startDate);
  const end = new Date(endDate);

  while (currentDate <= end) {
    dates.push(new Date(currentDate));
    currentDate.setDate(currentDate.getDate() + 1); // Increment the date by 1 day
  }

  return dates;
}


(async () => {
  const abh_map= await processFiles();
  const startDate = formatDate(new Date(abh_map[0])) // Start Date (MM/DD/YYYY)
  const endDate = formatDate(new Date()) 
  const downloadPath =
    "C:\\CSIT\\Abhi Semester 7\\project\\0 Program\\1_automation\\date";

  const browser = await puppeteer.launch({
    headless: false,
  });

  const page = await browser.newPage();

  // Set up the download path behavior (CSV download)
  await page._client().send("Page.setDownloadBehavior", {
    behavior: "allow",
    downloadPath: downloadPath,
  });

  // Get array of dates in the range
  const dates = getDatesInRange(startDate, endDate);

  // Loop through each date and download CSV
  for (let date of dates) {
    const formattedDate = formatDate(date);

    // Go to the target URL
    await page.goto("https://nepalstock.com/today-price", {
      waitUntil: "networkidle2",
    });

    // Wait for the date picker to load
    await page.waitForSelector("input[bsdatepicker]");

    // Select the existing value in the date input and clear it
    const dateInput = await page.$("input[bsdatepicker]");
    await dateInput.click(); // Focus the input field

    // Set the date using JavaScript in MM/DD/YYYY format
    await page.evaluate(
      (input, date) => {
        input.value = date;

        // Create and dispatch input event
        const inputEvent = new Event("input", { bubbles: true });
        input.dispatchEvent(inputEvent);

        // Create and dispatch change event
        const changeEvent = new Event("change", { bubbles: true });
        input.dispatchEvent(changeEvent);
      },
      dateInput,
      formattedDate
    );
    
    // Wait for the date input to settle before clicking the filter button
    await setTimeout(500); // Wait briefly to ensure the input is fully typed

    // Click the "Filter" button to apply the selected date
    await page.click(".box__filter--search");
    await setTimeout(1000); // Wait for download to trigger

    // Wait for the "Download as CSV" button to appear
    await page.waitForSelector("div.download-csv a.table__file");
    await page.click("div.download-csv a.table__file");

    // Wait for the download to start (or the page to finish)
    await setTimeout(2000); // Wait for download to trigger

    console.log(`Download triggered for ${formattedDate}`);
  }

  // Close the browser
  await browser.close();
})();

