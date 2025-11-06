const express = require('express');
const { Pool } = require('pg');
const path = require('path');

const router = express.Router();

// PostgreSQL connection
const pool = new Pool({
  user: 'postgres',
  host: 'localhost',
  database: 'Stock',
  password: '1234',
  port: 5432,
});

// Middleware to check if user is logged in
function requireLogin(req, res, next) {
  if (!req.session.user) return res.status(401).send('Unauthorized');
  next();
}

// Serve watchlist HTML page (protected)
router.get('/', requireLogin, (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'index2.html'));
});

// Create new watchlist entry
router.post('/', requireLogin, async (req, res) => {
  try {
    const { stock_symbol_name, per_unit_cost, units, alert_unit_price } = req.body;

    const result = await pool.query(
      `INSERT INTO public.watchlist 
       (id, stock_symbol_name, per_unit_cost, units, alert_unit_price)
       VALUES ($1, $2, $3, $4, $5) RETURNING *`,
      [req.session.user.uid, stock_symbol_name, per_unit_cost, units, alert_unit_price]
    );

    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).send('Insert failed');
  }
});

// Get all watchlist entries for logged-in user
router.get('/all', requireLogin, async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM public.watchlist WHERE id = $1 ORDER BY wid ASC',
      [req.session.user.uid]
    );
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).send('Error fetching data');
  }
});

// Delete watchlist entry by wid
router.delete('/:wid', requireLogin, async (req, res) => {
  try {
    const { wid } = req.params;
    await pool.query(
      'DELETE FROM public.watchlist WHERE wid = $1 AND id = $2',
      [wid, req.session.user.uid]
    );
    res.sendStatus(204);
  } catch (err) {
    console.error(err);
    res.status(500).send('Delete failed');
  }
});

// Update watchlist entry by wid
router.put('/:wid', requireLogin, async (req, res) => {
  console.log('req')
  try {
    const { wid } = req.params;
    const { stock_symbol_name, per_unit_cost, units, alert_unit_price } = req.body;

    await pool.query(
      `UPDATE public.watchlist
       SET stock_symbol_name = $1, per_unit_cost = $2, units = $3, alert_unit_price = $4
       WHERE wid = $5 AND id = $6`,
      [stock_symbol_name, per_unit_cost, units, alert_unit_price, wid, req.session.user.uid]
    );
    res.sendStatus(200);
  } catch (err) {
    console.error(err);
    res.status(500).send('Update failed');
  }
});

// Get logged-in user info (username and email)
router.get('/me', requireLogin, async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT uid, name, email FROM public.users WHERE uid = $1',
      [req.session.user.uid]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to fetch user info' });
  }
});

// Logout endpoint

// Logout endpoint (no requireLogin)
router.post('/logout', (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: 'Logout failed' });
    }
    res.clearCookie('connect.sid');
    res.json({ message: 'Logged out successfully' });
  });
});

module.exports = router;
