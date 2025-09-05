//Fetch https://www.sharesansar.com/upcoming-issue

const puppeteer= require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({
        headless: false,
    });

    const page = await browser.newPage();

      await page.goto("https://www.sharesansar.com/upcoming-issue", {
      waitUntil: "networkidle2",
    });

})();
