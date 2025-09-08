// run: node --env-file=.env automate_3.js
// Oepns the updated file and 

const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse/sync');
const { Pool } = require('pg');
const { Resend } = require('resend');

// Initialize Postgres Pool
const pool = new Pool({
  connectionString: 'postgresql://postgres:1234@localhost:5432/Stock',
});

// Initialize Resend with your API key from env variable
const resend = new Resend(process.env.RESEND_API);

// Read and parse CSV with relaxed quotes option
const csvPath = path.join(__dirname, 'updated_data.csv');
const csvContent = fs.readFileSync(csvPath, 'utf-8');

const records = parse(csvContent, {
  columns: true,
  skip_empty_lines: true,
  relax_column_count: true,
  relax_quotes: true,  // <-- This allows parser to handle bad/unescaped quotes gracefully
});

// Get latest business date
const allDates = [...new Set(records.map(row => row['Business Date']))].filter(Boolean);
const latestDate = allDates.sort().reverse()[0];
const latestData = records.filter(row => row['Business Date'] === latestDate);

console.log(`Using data for: ${latestDate}`);

async function checkAlerts() {
  try {
    const query = `
      SELECT 
        w.stock_symbol_name, 
        w.alert_unit_price, 
        w.per_unit_cost,
        w.units,
        u.email AS user_email
      FROM public.watchlist w
      JOIN public.users u ON w.id = u.uid
    `;

    const result = await pool.query(query);

    const userAlerts = {};

    for (const { stock_symbol_name, alert_unit_price, per_unit_cost, units, user_email } of result.rows) {
      const match = latestData.find(row =>
        row['Symbol'] === stock_symbol_name || row['Security Name'] === stock_symbol_name
      );

      if (!match) {
        console.warn(`No match found in CSV for: ${stock_symbol_name}`);
        continue;
      }

      const currentPrice = parseFloat(match['Last Updated Price']);
      const alertPrice = parseFloat(alert_unit_price);
      const costPrice = parseFloat(per_unit_cost);
      const numberOfUnits = parseFloat(units);

      if (isNaN(currentPrice) || isNaN(alertPrice)) {
        console.warn(`Price data missing for: ${stock_symbol_name}`);
        continue;
      }

      if (currentPrice > alertPrice) {
        console.log(`ALERT: ${stock_symbol_name} is ABOVE alert (${currentPrice} > ${alertPrice})`);

        if (!userAlerts[user_email]) {
          userAlerts[user_email] = [];
        }

        userAlerts[user_email].push({
          symbol: stock_symbol_name,
          costPrice,
          currentPrice,
          units: numberOfUnits
        });
      } else {
        console.log(`OK: ${stock_symbol_name} is within range (${currentPrice} <= ${alertPrice})`);
      }
    }

    // Send consolidated email per user
    // console.log("Sending email currently turned off")
    for (const [email, alerts] of Object.entries(userAlerts)) {
      await sendStockAlertEmail(email, alerts);
    }

  } catch (err) {
    console.error('Error checking alerts:', err);
  } finally {
    await pool.end();
  }
}

// Updated sendStockAlertEmail function to include units and cost price

async function sendStockAlertEmail(toEmail, alerts) {
  let stocksHtml = alerts.map(({ symbol, costPrice, currentPrice, units }) => {
    const profitPerUnit = currentPrice - costPrice;
    const totalProfit = profitPerUnit * units;
    const profitPercent = (profitPerUnit / costPrice) * 100;

    return `
      <li>
        <strong>${symbol}</strong><br>
        Cost Price: ${costPrice.toFixed(2)} | Current Price: ${currentPrice.toFixed(2)}<br>
        Units: ${units}<br>
        Profit: ${totalProfit.toFixed(2)} (${profitPercent.toFixed(2)}% per unit)
      </li>
    `;
  }).join("");

  const emailHtml = `
    <h2>Stock Alert</h2>
    <p>The following stocks in your watchlist are above your alert price:</p>
    <ul>${stocksHtml}</ul>
    <p>Keep an eye on your investments!</p>
  `;

  try {
    const data = await resend.emails.send({
      from: 'AbhishekSilwal@abhisheksilwal.com.np',
      to: toEmail,
      subject: `Stock Alerts (${alerts.length} stock(s) above alert price)`,
      html: emailHtml,
    });
    console.log(`Email sent to ${toEmail} for ${alerts.length} stock(s):`, data);
  } catch (error) {
    console.error('Error sending email:', error);
  }
}

checkAlerts();
