// 📦 backend/server.js

require('dotenv').config()

console.log("📦 Backend starting...")

const express = require('express')
const cors = require('cors')
const { Pool } = require('pg')
const fs = require('fs')
const path = require('path')

const app = express()
app.use(cors())

// 🌐 PostgreSQL connection
const pool = new Pool({
  user: process.env.PG_USER,
  host: process.env.PG_HOST,
  database: process.env.PG_DATABASE,
  password: process.env.PG_PASSWORD,
  port: parseInt(process.env.PG_PORT, 10),
})

// 🧠 Load and parse named SQL blocks
const sqlText = fs.readFileSync(path.join(__dirname, 'queries.sql'), 'utf8')
const sql = { queries: parseNamedQueries(sqlText) }

function parseNamedQueries(text) {
  const queries = {}
  const blocks = text.split('-- name:')
  for (const block of blocks.slice(1)) {
    const [nameLine, ...lines] = block.split('\n')
    queries[nameLine.trim()] = lines.join('\n').trim()
  }
  return queries
}

// 🔁 Simple memory cache (30s TTL)
const cache = new Map()
function getCached(key, ttl = 30000) {
  const item = cache.get(key)
  if (item && Date.now() - item.timestamp < ttl) return item.data
  return null
}

// 🧪 Readiness API
app.get('/readiness-latest', async (req, res) => {
  const cached = getCached('readiness-latest')
  if (cached) return res.json(cached)

  try {
    const { rows } = await pool.query(sql.queries['readiness-latest'])
    cache.set('readiness-latest', { data: rows, timestamp: Date.now() })
    res.json(rows)
  } catch (err) {
    console.error('Error:', err)
    res.status(500).json({ error: 'Internal error' })
  }
})

app.get('/readiness-quarterly', async (req, res) => {
  const cached = getCached('readiness-quarterly')
  if (cached) return res.json(cached)

  try {
    const { rows } = await pool.query(sql.queries['readiness-daily-quarters'])
    cache.set('readiness-quarterly', { data: rows, timestamp: Date.now() })
    res.json(rows)
  } catch (err) {
    console.error('Error in /readiness-quarterly:', err)
    res.status(500).json({ error: 'Internal error' })
  }
})

// ✅ Start
const PORT = 3001
app.listen(PORT, () => {
  console.log(`✅ Backend running at http://localhost:${PORT}`)
})
