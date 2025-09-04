const express = require('express');
const { Pool } = require('pg');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const port = 8000;

app.use(express.static('frontend'));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Connect to PostgreSQL
const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'Stock',
    password: '1234',
    port: 5432,
});

// Serve HTML
app.get('/update', (req, res) => {
    res.sendFile(path.join(__dirname, 'frontend', 'index.html'));
});

app.post('/api/watchlist', async (req, res) => {
    try {
        const { stock_symbol_name, per_unit_cost, units, alert_unit_price } = req.body;

        const result = await pool.query(
            `INSERT INTO public.watchlist 
                (id, stock_symbol_name, per_unit_cost, units, alert_unit_price)
             VALUES ($1, $2, $3, $4, $5) RETURNING *`,
            [1,stock_symbol_name, per_unit_cost, units, alert_unit_price]
        );

        res.status(201).json(result.rows[0]);
    } catch (err) {
        console.error(err);
        res.status(500).send('Insert failed');
    }
});

// GET all rows
app.get('/api/watchlist', async (req, res) => {
    try {
        const result = await pool.query('SELECT * FROM public.watchlist ORDER BY wid ASC');
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).send('Error fetching data');
    }
});

// DELETE by wid
app.delete('/api/watchlist/:wid', async (req, res) => {
    try {
        const wid = req.params.wid;
        await pool.query('DELETE FROM public.watchlist WHERE wid = $1', [wid]);
        res.sendStatus(204);
    } catch (err) {
        console.error(err);
        res.status(500).send('Delete failed');
    }
});

// UPDATE by wid
app.put('/api/watchlist/:wid', async (req, res) => {
    try {
        const { wid } = req.params;
        const { id, stock_symbol_name, per_unit_cost, units, alert_unit_price } = req.body;

        await pool.query(
            `UPDATE public.watchlist SET 
                id = $1,
                stock_symbol_name = $2,
                per_unit_cost = $3,
                units = $4,
                alert_unit_price = $5
             WHERE wid = $6`,
            [id, stock_symbol_name, per_unit_cost, units, alert_unit_price, wid]
        );
        res.sendStatus(200);
    } catch (err) {
        console.error(err);
        res.status(500).send('Update failed');
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
