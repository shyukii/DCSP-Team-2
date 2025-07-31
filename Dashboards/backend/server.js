const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Import routes
const apiRoutes = require('./routes/api');

// Middleware - Explicit CORS configuration
console.log('🚀 CORS fix deployed - version 3 - EXPLICIT CONFIG');

app.use(cors({
  origin: [
    'http://localhost:5173', 
    'http://localhost:3000', 
    'https://papas-princess.vercel.app'
  ],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api', apiRoutes);

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'NutricycleAI Backend API',
    version: '1.0.0',
    status: 'Running'
  });
});

// Health check endpoint for Railway
app.get('/api/health', (req, res) => {
  res.json({
    status: 'OK',
    message: 'NutricycleAI API is running',
    timestamp: new Date().toISOString(),
    version: 'v3-CORS-FIXED',
    uptime: process.uptime()
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err.stack);
  res.status(500).json({
    success: false,
    message: 'Internal server error',
    error: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    message: 'API endpoint not found'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📊 Dashboard API ready for predictions!`);
});

module.exports = app;