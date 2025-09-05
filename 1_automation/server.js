//login
// silwalabhi3@gmail.com
//password: 1234


const express = require('express');
const session = require('express-session');
const bcrypt = require('bcrypt');
const bodyParser = require('body-parser');
const path = require('path');
const { Pool } = require('pg');

const watchlistRoutes = require('./watchlist'); // Import router

const app = express();
const port = 8000;

// Middleware
app.use(express.static('frontend'));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.use(
  session({
    secret: 'supersecretkey',
    resave: false,
    saveUninitialized: true,
    cookie: { maxAge: 1000 * 60 * 60 }, // 1 hour
  })
);

// DB connection
const pool = new Pool({
  user: 'postgres',
  host: 'localhost',
  database: 'Stock',
  password: '1234',
  port: 5432,
});

// Middleware to check login
function requireLogin(req, res, next) {
  if (!req.session.user) {
    return res.redirect('/login');
  }
  next();
}

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'home.html'));
});


// Register
app.post('/api/register', async (req, res) => {
  const { name, email, password } = req.body;
  const hashedPassword = await bcrypt.hash(password, 10);
  await pool.query(
    `INSERT INTO public.users (name, email, password) VALUES ($1, $2, $3)`,
    [name, email, hashedPassword]
  );
  res.redirect('/login');
});

// Login
app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;
  const result = await pool.query(`SELECT * FROM public.users WHERE email = $1`, [email]);
  if (result.rows.length === 0) return res.status(400).send('User not found');

  const user = result.rows[0];
  const valid = await bcrypt.compare(password, user.password);
  if (!valid) return res.status(400).send('Invalid password');

  req.session.user = { uid: user.uid, email: user.email };
  res.redirect('/update');
});

// Logout
app.get('/api/logout', (req, res) => {
  req.session.destroy(err => {
    if (err) console.error(err);
    res.redirect('/login');
  });
});

// Use watchlist routes (protected)
app.use('/api/watchlist', requireLogin, watchlistRoutes);

// Serve pages
app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'login.html'));
});
app.get('/register', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'register.html'));
});
app.get('/update', requireLogin, (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'index2.html'));
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
