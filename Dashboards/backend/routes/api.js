const express = require('express');
const router = express.Router();
const {
  getHistoricalData,
  getPredictionData,
  getDevicesWithSensors,
  getDashboardStats
} = require('../controllers/dashboardController');

// Dashboard routes
router.get('/dashboard/stats', getDashboardStats);
router.get('/historical-data', getHistoricalData);
router.get('/prediction-data', getPredictionData);
router.get('/devices', getDevicesWithSensors);

// Health check
router.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'NutricycleAI API is running',
    timestamp: new Date().toISOString()
  });
});

module.exports = router;