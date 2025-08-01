const express = require('express');
const router = express.Router();
const {
  getHistoricalData,
  getPredictionData,
  getDevicesWithSensors,
  getDashboardStats,
  getUserCO2Impact,
  getGlobalStats,
  getUserFeedingLogs,
  getUsersWithFeedingData,
  getPlantMoistureUsers,
  getUserPlantMoisture,
  getUserMoisturePredictions,
  getSoilECUsers,
  getUserSoilEC,
  getUserECPredictions
} = require('../controllers/dashboardController');

// CO2E Dashboard routes
router.get('/users-with-data', getUsersWithFeedingData);
router.get('/user/:username/co2-impact', getUserCO2Impact);
router.get('/global-stats', getGlobalStats);
router.get('/feeding-logs/:username', getUserFeedingLogs);

// Plant Moisture Dashboard routes
router.get('/plant-moisture-users', getPlantMoistureUsers);
router.get('/user/:username/plant-moisture', getUserPlantMoisture);
router.get('/user/:username/moisture-predictions', getUserMoisturePredictions);

// Soil EC Dashboard routes
router.get('/soil-ec-users', getSoilECUsers);
router.get('/user/:username/soil-ec', getUserSoilEC);
router.get('/user/:username/ec-predictions', getUserECPredictions);

// Legacy dashboard routes (keeping for compatibility)
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