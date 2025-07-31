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

// Hardcode for Railway deployment (temporary)
const poolConfig = {
  host: 'aws-0-us-east-2.pooler.supabase.com',
  port: 6543,
  database: 'postgres',
  user: 'postgres.nimflhaujdwzwirodude',
  password: 'Zss-3617sigma',
  ssl: {
    rejectUnauthorized: false
  }
};

console.log('🔧 Using hardcoded database configuration for Railway');

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