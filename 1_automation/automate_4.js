// node --env-file=.env automate_4.js
const puppeteer = require("puppeteer");
const fs = require("fs");
const path = require("path");
const { Pool } = require("pg");
const { Resend } = require("resend");

(async () => {
  // DB pool
  const pool = new Pool({
  user: 'postgres',
  host: 'localhost',
  database: 'Stock',
  password: '1234',
  port: 5432,
  });

  const browser = await puppeteer.launch({
    headless: false,
  });

  const page = await browser.newPage();
  await page.goto("https://nepsealpha.com/investment-calandar/ipo", {
    waitUntil: "networkidle2",
  });

  await page.waitForSelector("table.table");

  const ipoData = await page.evaluate(() => {
    const rows = document.querySelectorAll("table.table tbody tr");
    const data = [];

    const Registered_Meroshare_Users = 6135325;
    const minimum_share = 10;

    rows.forEach((row) => {
      const cols = row.querySelectorAll("td");
      if (cols.length > 0) {
        const totalUnits = parseInt(
          cols[1]?.innerText.trim().replace(/,/g, "")
        ) || 0;

        const estimatedShareToApply = Math.max(
          minimum_share,
          Math.floor(totalUnits / Registered_Meroshare_Users)
        );

        const probability = totalUnits / Registered_Meroshare_Users;

        const today = new Date();
        const closingDateStr = cols[3]?.innerText.trim();
        const closingDate = new Date(closingDateStr);
        const timeDiff = closingDate - today;
        const daysRemaining = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));

        data.push({
          company: cols[0]?.innerText.trim(),
          units: cols[1]?.innerText.trim(),
          issueOpen: cols[2]?.innerText.trim(),
          issueClose: closingDateStr,
          status: cols[5]?.innerText.trim(),
          share_to_apply: estimatedShareToApply,
          probability: probability.toFixed(10),
          days_remaining: daysRemaining >= 0 ? daysRemaining : 0,
        });
      }
    });

    return data;
  });

  console.log("IPO Data:", ipoData);

  const openIPOs = ipoData.filter(
    (ipo) => ipo.status.toLowerCase() === "open"
  );

  const dirPath = path.join(__dirname, "ipo");
  const dataFilePath = path.join(dirPath, "data.json");
  const logFilePath = path.join(dirPath, "log.json");

  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath);
  }

  // overwrite data.json
  fs.writeFileSync(dataFilePath, JSON.stringify(openIPOs, null, 2), "utf-8");

  // append to log.json
  let logs = [];
  if (fs.existsSync(logFilePath)) {
    try {
      logs = JSON.parse(fs.readFileSync(logFilePath, "utf-8"));
    } catch {
      logs = [];
    }
  }
  logs.push({ timestamp: new Date().toISOString(), openIPOs });
  fs.writeFileSync(logFilePath, JSON.stringify(logs, null, 2), "utf-8");

  // fetch all users from DB
  const client = await pool.connect();
  let emails = [];
  try {
    const res = await client.query("SELECT email FROM public.users WHERE email IS NOT NULL");
    emails = res.rows.map((row) => row.email);
  } catch (err) {
    console.error("DB Error:", err);
  } finally {
    client.release();
  }

  if (emails.length === 0) {
    console.log("No user emails found, skipping email sending.");
    await browser.close();
    await pool.end();
    return;
  }

  // send via Resend with BCC
  const resend = new Resend(process.env.RESEND_API);


  const formattedTable = openIPOs
    .map(
      (ipo) => `
        <tr>
          <td>${ipo.company}</td>
          <td>${ipo.units}</td>
          <td>${ipo.issueOpen}</td>
          <td>${ipo.issueClose}</td>
          <td>${ipo.status}</td>
          <td>${ipo.share_to_apply}</td>
          <td>${ipo.probability}</td>
          <td>${ipo.days_remaining}</td>
        </tr>`
    )
    .join("");

  const htmlContent = `
    <h2>Latest Open IPOs</h2>
    <table border="1" cellspacing="0" cellpadding="5">
      <thead>
        <tr>
          <th>Company</th>
          <th>Units</th>
          <th>Issue Open</th>
          <th>Issue Close</th>
          <th>Status</th>
          <th>Share to Apply</th>
          <th>Probability</th>
          <th>Days Remaining</th>
        </tr>
      </thead>
      <tbody>${formattedTable}</tbody>
    </table>
    <div style='background-color:red; padding:10px;'> This is an automated message please don't reply to this message </div>
  `;

  try {
    await resend.emails.send({
      from: "ipo-tracker@abhisheksilwal.com.np",
      to: "noreply@abhisheksilwal.com.np",
      bcc: emails, 
      subject: "Latest IPO Updates",
      html: htmlContent,
    });
    console.log("IPO update email sent to all users via BCC.");
  } catch (error) {
    console.error("Error sending email:", error);
  }

  await browser.close();
  await pool.end();
})();
