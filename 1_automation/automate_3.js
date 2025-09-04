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

    for (const { stock_symbol_name, alert_unit_price, per_unit_cost, units, user_email } of result.rows) {
      const match = latestData.find(row =>
        row['Symbol'] === stock_symbol_name || row['Security Name'] === stock_symbol_name
      );

      if (match) {
        const currentPrice = parseFloat(match['Last Updated Price']);
        const alertPrice = parseFloat(alert_unit_price);
        const costPrice = parseFloat(per_unit_cost);
        const numberOfUnits = parseFloat(units);

        if (!isNaN(currentPrice) && !isNaN(alertPrice)) {
          if (currentPrice > alertPrice) {
            console.log(`ALERT: ${stock_symbol_name} is ABOVE alert (${currentPrice} > ${alertPrice})`);

            if (user_email) {
              await sendStockAlertEmail(user_email, stock_symbol_name, costPrice, currentPrice, numberOfUnits);
            } else {
              console.warn(`No email found for user watching ${stock_symbol_name}, skipping email.`);
            }
          } else {
            console.log(` OK: ${stock_symbol_name} is within range (${currentPrice} <= ${alertPrice})`);
          }
        } else {
          console.warn(` Price data missing for: ${stock_symbol_name}`);
        }
      } else {
        console.warn(` No match found in CSV for: ${stock_symbol_name}`);
      }
    }
  } catch (err) {
    console.error(' Error checking alerts:', err);
  } finally {
    await pool.end();
  }
}

// Updated sendStockAlertEmail function to include units and cost price

async function sendStockAlertEmail(toEmail, symbol, costPrice, currentPrice, units) {
  const profitPerUnit = currentPrice - costPrice;
  const totalProfit = profitPerUnit * units;
  const profitPercent = (profitPerUnit / costPrice) * 100;
  console.log(toEmail)
  const emailHtml = `
    <h2>Stock Alert for ${symbol}</h2>
    <p>Your stock <strong>${symbol}</strong> is doing well.</p>
    <p>Here's a quick calculation based on current data:</p>
    <ul>
      <li>Cost Price per Unit: ₹${costPrice.toFixed(2)}</li>
      <li>Units Owned: ${units}</li>
      <li>Current Price: ₹${currentPrice.toFixed(2)}</li>
      <li><strong>Potential Profit if sold today:</strong> ₹${totalProfit.toFixed(2)} (${profitPercent.toFixed(2)}% per unit)</li>
    </ul>
    <p>Keep an eye on your investment!</p>
  `;

  try {
    const data = await resend.emails.send({
      from: 'AbhishekSilwal@abhisheksilwal.com.np',
      to: toEmail,
      subject: `Stock Alert for ${symbol}`,
      html: emailHtml,
    });
    console.log(`Email sent for ${symbol}:`, data);
  } catch (error) {
    console.error('Error sending email:', error);
  }
}


checkAlerts();
