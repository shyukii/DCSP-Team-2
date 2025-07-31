const { Pool } = require('pg');
require('dotenv').config();

// Debug environment variables
console.log('🔍 Database Environment Variables:');
console.log('DB_HOST:', process.env.DB_HOST);
console.log('DB_PORT:', process.env.DB_PORT);
console.log('DB_NAME:', process.env.DB_NAME);
console.log('DB_USER:', process.env.DB_USER ? '***SET***' : 'MISSING');
console.log('DB_PASSWORD:', process.env.DB_PASSWORD ? '***SET***' : 'MISSING');
console.log('DATABASE_URL:', process.env.DATABASE_URL ? '***SET***' : 'MISSING');

// Try DATABASE_URL first, then individual variables
let poolConfig;
if (process.env.DATABASE_URL) {
  poolConfig = {
    connectionString: process.env.DATABASE_URL,
    ssl: {
      rejectUnauthorized: false
    }
  };
} else {
  poolConfig = {
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    ssl: {
      rejectUnauthorized: false
    }
  };
}

const pool = new Pool({
  ...poolConfig,
  ssl: {
    rejectUnauthorized: false
  },
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Test connection
pool.on('connect', () => {
  console.log('✅ Connected to Supabase PostgreSQL database');
});

pool.on('error', (err) => {
  console.error('❌ Database connection error:', err);
});

module.exports = pool;