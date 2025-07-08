const puppeteer = require('puppeteer');
const { setTimeout } = require('node:timers/promises'); 



(async () => {
  const date= Date.now()
  const downloadPath = 'C:\\CSIT\\Abhi Semester 7\\project\\0 Program\\stock_scraper_day_wise'; 

  // Launch the browser
  const browser = await puppeteer.launch({
    headless: false,
  });

  const page = await browser.newPage();

  await page._client().send('Page.setDownloadBehavior', {
    behavior: 'allow',
    downloadPath: downloadPath,
  });

  // Go to the target URL
  await page.goto('https://nepalstock.com/today-price', { waitUntil: 'networkidle2' });

  // Wait for the "Download as CSV" button to appear
  await page.waitForSelector('div.download-csv a.table__file');

  await page.click('div.download-csv a.table__file');


  await setTimeout(1000);
  await browser.close();
})();
