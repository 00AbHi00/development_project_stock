const puppeteer = require("puppeteer");
const { setTimeout } = require("node:timers/promises");
const fs = require("fs");
const path = require("path");

// Function to format date as MM/DD/YYYY
function formatDate(date) {
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
  const startDate = "09/01/2024"; // Start Date (MM/DD/YYYY)
  const endDate = "08/24/2025"; // End Date (MM/DD/YYYY)
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
