const pool = require('../config/database');

/**
 * Database query wrapper with retry logic
 */
const executeQuery = async (query, params = [], retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      const result = await pool.query(query, params);
      return result;
    } catch (error) {
      console.error(`Database query attempt ${i + 1} failed:`, error.message);
      
      if (i === retries - 1) {
        throw error; // Last attempt, throw the error
      }
      
      // Wait before retry (exponential backoff)
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
    }
  }
};

/**
 * CO2 Emissions Calculator Class
 * Matches your Python EmissionsCalculator logic
 */
class EmissionsCalculator {
  static STP_AIR_CONCENTRATION_PERCENT = 21.0;
  static STP_CO2_PPM = 415.0;
  static FOOD_WASTE_CO2_FACTOR = 2.5;
  static COMPOST_REDUCTION_FACTOR = 0.8;
  static TREE_CO2_ABSORPTION = 25.0;    // was 21.9
  static PETROL_CO2_FACTOR = 2.3;       // was 2.33  
  static CAR_CO2_FACTOR = 0.4;          // was 0.454

  static calculateCO2SavedFromFoodWaste(foodWasteKg, tankVolume, soilVolume) {
    const co2Ppm = this.STP_CO2_PPM;
    const airConc = this.STP_AIR_CONCENTRATION_PERCENT / 100;

    const effectiveVolume = tankVolume - (soilVolume * airConc);
    const baselineCO2Grams = (co2Ppm / 1_000_000) * effectiveVolume * 1.8;

    // 1kg food waste → ~2.5kg CO₂, composting reduces 80%
    const co2SavedLandfillKg = foodWasteKg * this.FOOD_WASTE_CO2_FACTOR * this.COMPOST_REDUCTION_FACTOR;
    const co2SavedLandfillG = co2SavedLandfillKg * 1000;

    const totalSavedG = baselineCO2Grams + co2SavedLandfillG;
    const totalSavedKg = totalSavedG / 1000;

    return {
      foodWasteKg: foodWasteKg,
      tankVolume: tankVolume,
      soilVolume: soilVolume,
      effectiveVolume: Math.round(effectiveVolume * 10000) / 10000,
      baselineEmissionsGrams: Math.round(baselineCO2Grams * 1000000) / 1000000,
      co2SavedFromLandfillKg: Math.round(co2SavedLandfillKg * 100) / 100,
      totalCO2SavedKg: Math.round(totalSavedKg * 100) / 100,
      totalCO2SavedGrams: Math.round(totalSavedG * 100) / 100
    };
  }

  static getEnvironmentalImpactSummary(co2SavedKg) {
    return {
      treesEquivalent: Math.round((co2SavedKg / this.TREE_CO2_ABSORPTION) * 100) / 100,
      petrolLitresEquivalent: Math.round((co2SavedKg / this.PETROL_CO2_FACTOR) * 10) / 10,
      carMilesEquivalent: Math.round((co2SavedKg / this.CAR_CO2_FACTOR) * 10) / 10
    };
  }
}

/**
 * Get all users with feeding logs
 * GET /api/users-with-data
 */
const getUsersWithFeedingData = async (req, res) => {
  try {
    const query = `
      SELECT DISTINCT u.username, u.telegram_id,
             COUNT(fl.id) as feeding_logs_count,
             MAX(fl.created_at) as last_feeding_date
      FROM users u
      LEFT JOIN feeding_logs fl ON u.telegram_id = fl.telegram_id
      GROUP BY u.username, u.telegram_id
      ORDER BY feeding_logs_count DESC, u.username ASC
    `;
    
    const result = await pool.query(query);
    
    const usersWithData = result.rows.map(row => ({
      username: row.username,
      telegramId: row.telegram_id,
      feedingLogsCount: parseInt(row.feeding_logs_count),
      lastFeedingDate: row.last_feeding_date,
      hasData: parseInt(row.feeding_logs_count) > 0
    }));

    res.json({
      success: true,
      data: {
        users: usersWithData,
        totalUsers: usersWithData.length,
        usersWithData: usersWithData.filter(u => u.hasData).length,
        usersWithoutData: usersWithData.filter(u => !u.hasData).length
      }
    });

  } catch (error) {
    console.error('Error getting users with feeding data:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
  }
};

/**
 * Get user's feeding logs and calculate CO2 impact
 * GET /api/user/:username/co2-impact
 */
const getUserCO2Impact = async (req, res) => {
  try {
    const { username } = req.params;

    // Get user profile for tank and soil volumes
    const userQuery = `
      SELECT telegram_id, tank_volume, soil_volume, username 
      FROM users 
      WHERE username = $1
    `;
    const userResult = await pool.query(userQuery, [username]);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    const user = userResult.rows[0];
    const { telegram_id, tank_volume, soil_volume, username: foundUsername } = user;

    if (!tank_volume || !soil_volume) {
      return res.status(400).json({
        success: false,
        message: 'User profile incomplete. Tank and soil volumes required.'
      });
    }

    // Get feeding logs
    const feedingLogsQuery = `
      SELECT greens, browns, 
             COALESCE(moisture_percentage, 0) as moisture_percentage,
             CASE WHEN moisture_percentage IS NOT NULL THEN 'percentage' ELSE 'ml' END as moisture_type,
             created_at 
      FROM feeding_logs 
      WHERE telegram_id = $1 
      ORDER BY created_at DESC
    `;
    const feedingLogsResult = await pool.query(feedingLogsQuery, [telegram_id]);

    const feedingLogs = feedingLogsResult.rows;
    
    if (feedingLogs.length === 0) {
      return res.json({
        success: true,
        hasData: false,
        message: 'No feeding logs found. Start logging your compost materials in the NutriBot Compost Feeding feature!',
        data: {
          user: {
            username: foundUsername,
            tankVolume: tank_volume,
            soilVolume: soil_volume
          },
          totalFoodWasteKg: 0,
          totalCO2SavedKg: 0,
          feedingLogsCount: 0,
          feedingLogs: [],
          monthlyData: [],
          impact: {
            treesEquivalent: 0,
            petrolLitresEquivalent: 0,
            carMilesEquivalent: 0
          }
        }
      });
    }

    // Calculate total food waste (greens + browns) in kg - match Python rounding
    const totalFoodWasteGrams = feedingLogs.reduce((sum, log) => 
      sum + (parseFloat(log.greens) || 0) + (parseFloat(log.browns) || 0), 0
    );
    const totalFoodWasteKg = Math.round((totalFoodWasteGrams / 1000) * 100) / 100; // Round to 2 decimals like Python

    // Calculate CO2 savings
    const co2Result = EmissionsCalculator.calculateCO2SavedFromFoodWaste(
      totalFoodWasteKg, 
      tank_volume, 
      soil_volume
    );

    // Get environmental impact
    const impact = EmissionsCalculator.getEnvironmentalImpactSummary(co2Result.totalCO2SavedKg);

    // Generate monthly data
    const monthlyData = generateMonthlyData(feedingLogs, tank_volume, soil_volume);

    res.json({
      success: true,
      hasData: true,
      data: {
        user: {
          username: user.username,
          tankVolume: tank_volume,
          soilVolume: soil_volume
        },
        totalFoodWasteKg: totalFoodWasteKg,
        totalCO2SavedKg: co2Result.totalCO2SavedKg,
        feedingLogsCount: feedingLogs.length,
        feedingLogs: feedingLogs.slice(0, 10), // Return latest 10 logs
        monthlyData: monthlyData,
        impact: impact,
        breakdown: {
          baselineEmissionsGrams: co2Result.baselineEmissionsGrams,
          co2SavedFromLandfillKg: co2Result.co2SavedFromLandfillKg,
          effectiveVolume: co2Result.effectiveVolume
        }
      }
    });

  } catch (error) {
    console.error('Error getting user CO2 impact:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
  }
};

/**
 * Get global community statistics
 * GET /api/global-stats
 */
const getGlobalStats = async (req, res) => {
  try {
    // Get total users count
    const usersCountQuery = `SELECT COUNT(DISTINCT telegram_id) as total_users FROM users`;
    const usersCountResult = await pool.query(usersCountQuery);
    const totalUsers = parseInt(usersCountResult.rows[0].total_users);

    // Get all users with feeding logs (less restrictive - use defaults if volumes missing)
    const usersWithLogsQuery = `
      SELECT DISTINCT u.telegram_id, u.tank_volume, u.soil_volume
      FROM users u
      INNER JOIN feeding_logs fl ON u.telegram_id = fl.telegram_id
    `;
    const usersWithLogsResult = await pool.query(usersWithLogsQuery);
    const usersWithLogs = usersWithLogsResult.rows;

    if (usersWithLogs.length === 0) {
      // No users with complete profiles and feeding logs, but show demo values
      const demoFoodWaste = 15.5; // kg
      const demoTankVolume = 50;
      const demoSoilVolume = 20;
      const demoCO2Result = EmissionsCalculator.calculateCO2SavedFromFoodWaste(demoFoodWaste, demoTankVolume, demoSoilVolume);
      const demoImpact = EmissionsCalculator.getEnvironmentalImpactSummary(demoCO2Result.totalCO2SavedKg);
      
      return res.json({
        success: true,
        data: {
          totalUsers: totalUsers,
          globalFoodWaste: demoFoodWaste,
          globalCO2Saved: demoCO2Result.totalCO2SavedKg,
          treesPlanted: Number(demoImpact.treesEquivalent.toFixed(2)),
          avgPerUser: totalUsers > 0 ? Number((demoCO2Result.totalCO2SavedKg / totalUsers).toFixed(2)) : 0,
          petrolSaved: demoImpact.petrolLitresEquivalent,
          carMilesOffset: demoImpact.carMilesEquivalent,
          totalFeedingLogs: 0,
          avgTankVolume: demoTankVolume,
          avgSoilVolume: demoSoilVolume
        }
      });
    }

    let globalFoodWasteKg = 0;
    let globalCO2SavedKg = 0;
    let globalTreesPlanted = 0;
    let totalFeedingLogs = 0;

    // Calculate for each user individually and sum up
    for (const user of usersWithLogs) {
      const userLogsQuery = `
        SELECT greens, browns, 
               COALESCE(moisture_percentage, 0) as moisture_percentage,
               CASE WHEN moisture_percentage IS NOT NULL THEN 'percentage' ELSE 'ml' END as moisture_type,
               created_at 
        FROM feeding_logs 
        WHERE telegram_id = $1
        ORDER BY created_at DESC
      `;
      const userLogsResult = await pool.query(userLogsQuery, [user.telegram_id]);
      const userFeedingLogs = userLogsResult.rows;

      if (userFeedingLogs.length > 0) {
        // Calculate user's total food waste
        const userFoodWasteGrams = userFeedingLogs.reduce((sum, log) => 
          sum + (parseFloat(log.greens) || 0) + (parseFloat(log.browns) || 0), 0
        );
        const userFoodWasteKg = userFoodWasteGrams / 1000;

        // Use default values if tank/soil volumes are missing (like personal view)
        const tankVolume = user.tank_volume || 50;
        const soilVolume = user.soil_volume || 20;

        // Calculate user's CO2 savings using their specific or default tank/soil volumes
        const userCO2Result = EmissionsCalculator.calculateCO2SavedFromFoodWaste(
          userFoodWasteKg, 
          tankVolume, 
          soilVolume
        );

        // Calculate user's trees planted equivalent
        const userImpact = EmissionsCalculator.getEnvironmentalImpactSummary(userCO2Result.totalCO2SavedKg);

        // Add to global totals
        globalFoodWasteKg += userFoodWasteKg;
        globalCO2SavedKg += userCO2Result.totalCO2SavedKg;
        globalTreesPlanted += userImpact.treesEquivalent;
        totalFeedingLogs += userFeedingLogs.length;
      }
    }

    // Calculate averages for display
    const avgVolumesQuery = `
      SELECT 
        AVG(tank_volume) as avg_tank_volume,
        AVG(soil_volume) as avg_soil_volume 
      FROM users 
      WHERE tank_volume IS NOT NULL AND soil_volume IS NOT NULL
    `;
    const avgVolumesResult = await pool.query(avgVolumesQuery);
    const actualAvgTankVolume = parseFloat(avgVolumesResult.rows[0].avg_tank_volume) || 50;
    const actualAvgSoilVolume = parseFloat(avgVolumesResult.rows[0].avg_soil_volume) || 20;

    // Get global environmental impact for other metrics
    const globalImpact = EmissionsCalculator.getEnvironmentalImpactSummary(globalCO2SavedKg);

    res.json({
      success: true,
      data: {
        totalUsers: totalUsers,
        globalFoodWaste: Number(globalFoodWasteKg.toFixed(2)),
        globalCO2Saved: Number(globalCO2SavedKg.toFixed(2)),
        treesPlanted: Number(globalTreesPlanted.toFixed(2)),
        avgPerUser: totalUsers > 0 ? Number((globalCO2SavedKg / totalUsers).toFixed(2)) : 0,
        petrolSaved: Number(globalImpact.petrolLitresEquivalent.toFixed(1)),
        carMilesOffset: Number(globalImpact.carMilesEquivalent.toFixed(1)),
        totalFeedingLogs: totalFeedingLogs,
        avgTankVolume: Number(actualAvgTankVolume.toFixed(2)),
        avgSoilVolume: Number(actualAvgSoilVolume.toFixed(2))
      }
    });

  } catch (error) {
    console.error('Error getting global stats:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
  }
};

/**
 * Helper function to generate monthly aggregated data
 */
function generateMonthlyData(feedingLogs, tankVolume, soilVolume) {
  const monthlyMap = {};

  feedingLogs.forEach(log => {
    const date = new Date(log.created_at);
    const monthKey = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
    const monthName = date.toLocaleDateString('en-US', { month: 'short' });

    if (!monthlyMap[monthKey]) {
      monthlyMap[monthKey] = {
        month: monthName,
        year: date.getFullYear(),
        foodWaste: 0,
        co2Saved: 0,
        cumulativeCO2: 0
      };
    }

    const foodWasteKg = ((parseFloat(log.greens) || 0) + (parseFloat(log.browns) || 0)) / 1000;
    const co2Saved = EmissionsCalculator.calculateCO2SavedFromFoodWaste(
      foodWasteKg, 
      tankVolume, 
      soilVolume
    ).totalCO2SavedKg;

    monthlyMap[monthKey].foodWaste += foodWasteKg;
    monthlyMap[monthKey].co2Saved += co2Saved;
  });

  // Convert to array and sort by date
  const monthlyArray = Object.entries(monthlyMap)
    .map(([key, value]) => ({ ...value, monthKey: key }))
    .sort((a, b) => a.monthKey.localeCompare(b.monthKey));

  // Calculate cumulative CO2
  let cumulative = 0;
  return monthlyArray.map(month => {
    cumulative += month.co2Saved;
    return {
      month: month.month,
      foodWaste: Math.round(month.foodWaste * 100) / 100,
      co2Saved: Math.round(month.co2Saved * 100) / 100,
      cumulativeCO2: Math.round(cumulative * 100) / 100
    };
  });
}

/**
 * Get user's recent feeding logs
 * GET /api/feeding-logs/:username
 */
const getUserFeedingLogs = async (req, res) => {
  try {
    const { username } = req.params;
    const limit = parseInt(req.query.limit) || 10;

    // First get telegram_id from username
    const userQuery = `SELECT telegram_id FROM users WHERE username = $1`;
    const userResult = await pool.query(userQuery, [username]);
    
    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    const telegram_id = userResult.rows[0].telegram_id;

    const query = `
      SELECT greens, browns, 
             COALESCE(moisture_percentage, 0) as moisture_percentage,
             CASE WHEN moisture_percentage IS NOT NULL THEN 'percentage' ELSE 'ml' END as moisture_type,
             created_at 
      FROM feeding_logs 
      WHERE telegram_id = $1 
      ORDER BY created_at DESC 
      LIMIT $2
    `;
    
    const result = await pool.query(query, [telegram_id, limit]);

    res.json({
      success: true,
      data: result.rows
    });

  } catch (error) {
    console.error('Error getting feeding logs:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
  }
};

/**
 * Dashboard stats (legacy function - keeping for compatibility)
 */
const getDashboardStats = async (req, res) => {
  try {
    // You can implement general dashboard stats here
    // For now, redirecting to global stats
    return getGlobalStats(req, res);
  } catch (error) {
    console.error('Error getting dashboard stats:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

/**
 * Get historical data (legacy function - keeping for compatibility)
 */
const getHistoricalData = async (req, res) => {
  try {
    res.json({
      success: true,
      message: 'Historical data endpoint - implement based on your needs',
      data: []
    });
  } catch (error) {
    console.error('Error getting historical data:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

/**
 * Get prediction data (legacy function - keeping for compatibility)
 */
const getPredictionData = async (req, res) => {
  try {
    res.json({
      success: true,
      message: 'Prediction data endpoint - implement based on your needs',
      data: []
    });
  } catch (error) {
    console.error('Error getting prediction data:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

/**
 * Get devices with sensors (legacy function - keeping for compatibility)
 */
const getDevicesWithSensors = async (req, res) => {
  try {
    res.json({
      success: true,
      message: 'Devices endpoint - implement based on your needs',
      data: []
    });
  } catch (error) {
    console.error('Error getting devices:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
};

/**
 * Get all users with plant moisture logs
 * GET /api/plant-moisture-users
 */
const getPlantMoistureUsers = async (req, res) => {
  try {
    const query = `
      SELECT DISTINCT u.username, u.telegram_id,
             COUNT(p.id) as moisture_logs_count,
             MAX(p.created_at) as last_reading_date
      FROM users u
      LEFT JOIN plant p ON u.telegram_id = p.telegram_id
      GROUP BY u.username, u.telegram_id
      ORDER BY moisture_logs_count DESC, u.username ASC
    `;
    
    const result = await pool.query(query);
    
    const usersWithData = result.rows
      .filter(row => parseInt(row.moisture_logs_count) > 0)
      .map(row => ({
        username: row.username,
        telegramId: row.telegram_id,
        moistureLogsCount: parseInt(row.moisture_logs_count),
        lastReadingDate: row.last_reading_date
      }));

    const usersWithoutData = result.rows
      .filter(row => parseInt(row.moisture_logs_count) === 0)
      .map(row => ({
        username: row.username,
        telegramId: row.telegram_id,
        moistureLogsCount: 0,
        lastReadingDate: null
      }));

    res.json({
      success: true,
      data: {
        usersWithData,
        usersWithoutData,
        totalUsers: result.rows.length
      }
    });

  } catch (error) {
    console.error('Error getting plant moisture users:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
  }
};

/**
 * Get user's plant moisture data and history
 * GET /api/user/:username/plant-moisture
 */
const getUserPlantMoisture = async (req, res) => {
  try {
    const { username } = req.params;

    // Get user info
    const userQuery = `SELECT telegram_id, username FROM users WHERE username = $1`;
    const userResult = await pool.query(userQuery, [username]);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    const user = userResult.rows[0];
    const { telegram_id } = user;

    // Get moisture logs
    const moistureLogsQuery = `
      SELECT plant_moisture, created_at 
      FROM plant 
      WHERE telegram_id = $1 
      ORDER BY created_at DESC
      LIMIT 30
    `;
    const moistureLogsResult = await pool.query(moistureLogsQuery, [telegram_id]);
    const moistureLogs = moistureLogsResult.rows;

    if (moistureLogs.length === 0) {
      return res.json({
        success: true,
        hasData: false,
        message: 'No plant moisture data found',
        data: {
          user: user,
          currentMoisture: 0,
          totalReadings: 0,
          averageMoisture: 0,
          moistureLogs: []
        }
      });
    }

    // Calculate statistics
    const currentMoisture = parseFloat(moistureLogs[0].plant_moisture);
    const totalReadings = moistureLogs.length;
    const averageMoisture = moistureLogs.reduce((sum, log) => sum + parseFloat(log.plant_moisture), 0) / totalReadings;

    res.json({
      success: true,
      hasData: true,
      data: {
        user: user,
        currentMoisture: Math.round(currentMoisture * 10) / 10,
        totalReadings: totalReadings,
        averageMoisture: Math.round(averageMoisture * 10) / 10,
        moistureLogs: moistureLogs.map(log => ({
          plant_moisture: parseFloat(log.plant_moisture),
          created_at: log.created_at
        }))
      }
    });

  } catch (error) {
    console.error('Error getting user plant moisture:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
  }
};

/**
 * Get moisture predictions for a user (calls Python service)
 * GET /api/user/:username/moisture-predictions
 */
const getUserMoisturePredictions = async (req, res) => {
  try {
    const { username } = req.params;

    // Get user info
    const userQuery = `SELECT telegram_id, username FROM users WHERE username = $1`;
    const userResult = await pool.query(userQuery, [username]);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    const user = userResult.rows[0];
    const { telegram_id } = user;

    // Get latest moisture reading
    const latestMoistureQuery = `
      SELECT plant_moisture 
      FROM plant 
      WHERE telegram_id = $1 
      ORDER BY created_at DESC 
      LIMIT 1
    `;
    const latestMoistureResult = await pool.query(latestMoistureQuery, [telegram_id]);

    if (latestMoistureResult.rows.length === 0) {
      return res.json({
        success: true,
        hasData: false,
        message: 'No moisture data available for predictions',
        data: {
          projections: [],
          watering_alerts: [],
          overall_recommendation: 'No data available'
        }
      });
    }

    const currentMoisture = parseFloat(latestMoistureResult.rows[0].plant_moisture);

    // Generate 30-day predictions using simple model
    // This mimics the Python PlantMoistureProjection logic
    const projections = [];
    const currentDate = new Date();
    
    for (let day = 0; day < 30; day++) {
      const projectionDate = new Date(currentDate);
      projectionDate.setDate(currentDate.getDate() + day);
      
      let projectedMoisture;
      if (day === 0) {
        projectedMoisture = currentMoisture;
      } else {
        // Simple decay model: 3.5% daily loss with some variation
        const dailyLoss = 3.5 + (Math.random() - 0.5) * 2; // 2.5-4.5% range
        projectedMoisture = Math.max(0, currentMoisture - (dailyLoss * day));
      }
      
      // Determine status
      let status;
      if (projectedMoisture < 20) status = 'critical';
      else if (projectedMoisture < 40) status = 'low';
      else if (projectedMoisture < 60) status = 'moderate';
      else status = 'good';
      
      projections.push({
        date: projectionDate.toISOString().split('T')[0],
        day_name: projectionDate.toLocaleDateString('en-US', { weekday: 'long' }),
        moisture_percentage: Math.round(projectedMoisture * 10) / 10,
        status: status
      });
    }

    // Generate watering alerts
    const watering_alerts = projections
      .filter(proj => proj.moisture_percentage < 40)
      .slice(0, 5)
      .map(proj => ({
        date: proj.date,
        day_name: proj.day_name,
        moisture_level: proj.moisture_percentage,
        urgency: proj.status,
        message: `Water needed on ${proj.day_name} - Moisture will be ${proj.moisture_percentage}%`
      }));

    // Overall recommendation
    const criticalDays = projections.filter(p => p.status === 'critical').length;
    const lowDays = projections.filter(p => p.status === 'low').length;
    
    let overall_recommendation;
    if (criticalDays > 0) {
      overall_recommendation = '🚨 Immediate Action Required: Your plant will need water within the next few days.';
    } else if (lowDays > 2) {
      overall_recommendation = '⚠️ Plan Ahead: Schedule watering sessions to maintain healthy moisture levels.';
    } else {
      overall_recommendation = '✅ All Good: Your plant\'s moisture levels look healthy for the week ahead.';
    }

    res.json({
      success: true,
      hasData: true,
      data: {
        current_moisture: currentMoisture,
        projections: projections,
        watering_alerts: watering_alerts,
        overall_recommendation: overall_recommendation
      }
    });

  } catch (error) {
    console.error('Error getting moisture predictions:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
  }
};

/**
 * Get all users with soil EC logs
 * GET /api/soil-ec-users
 */
const getSoilECUsers = async (req, res) => {
  try {
    const query = `
      SELECT DISTINCT u.username, u.telegram_id,
             COUNT(cs.id) as ec_logs_count,
             MAX(cs.created_at) as last_reading_date
      FROM users u
      LEFT JOIN compost_status cs ON u.telegram_id = cs.telegram_id 
        AND cs.ec IS NOT NULL
      GROUP BY u.username, u.telegram_id
      ORDER BY ec_logs_count DESC, u.username ASC
    `;
    
    const result = await executeQuery(query);
    
    const usersWithData = result.rows
      .filter(row => parseInt(row.ec_logs_count) > 0)
      .map(row => ({
        username: row.username,
        telegramId: row.telegram_id,
        ecLogsCount: parseInt(row.ec_logs_count),
        lastReadingDate: row.last_reading_date,
        hasData: true
      }));

    const usersWithoutData = result.rows
      .filter(row => parseInt(row.ec_logs_count) === 0)
      .map(row => ({
        username: row.username,
        telegramId: row.telegram_id,
        ecLogsCount: 0,
        lastReadingDate: null,
        hasData: false
      }));

    res.json({
      success: true,
      data: {
        usersWithData: usersWithData,
        usersWithoutData: usersWithoutData,
        totalUsers: result.rows.length
      }
    });

  } catch (error) {
    console.error('Error getting soil EC users:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
  }
};

/**
 * Get user's soil EC data and statistics
 * GET /api/user/:username/soil-ec
 */
const getUserSoilEC = async (req, res) => {
  try {
    const { username } = req.params;

    // Get user info
    const userQuery = `SELECT telegram_id, username FROM users WHERE username = $1`;
    const userResult = await pool.query(userQuery, [username]);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    const user = userResult.rows[0];
    const { telegram_id } = user;

    // Get EC logs with predictions
    const ecLogsQuery = `
      SELECT ec, moisture, created_at,
             overall_health_score, ec_status, moisture_status,
             readiness_status, estimated_ready_days,
             primary_recommendation, alert_level, alert_message
      FROM compost_status 
      WHERE telegram_id = $1 
        AND ec IS NOT NULL
      ORDER BY created_at DESC
      LIMIT 30
    `;
    const ecLogsResult = await pool.query(ecLogsQuery, [telegram_id]);
    const ecLogs = ecLogsResult.rows;

    if (ecLogs.length === 0) {
      return res.json({
        success: true,
        hasData: false,
        message: 'No soil EC data found',
        data: {
          user: user,
          currentEC: 0,
          currentMoisture: 0,
          totalReadings: 0,
          averageEC: 0,
          averageMoisture: 0,
          averageHealthScore: 0,
          ecLogs: [],
          currentStatus: 'No data',
          readinessStatus: 'Unknown',
          primaryRecommendation: 'Start taking EC readings to get predictions'
        }
      });
    }

    // Calculate statistics
    const currentReading = ecLogs[0];
    const currentEC = parseFloat(currentReading.ec);
    const currentMoisture = parseFloat(currentReading.moisture || 0);
    const totalReadings = ecLogs.length;
    const averageEC = ecLogs.reduce((sum, log) => sum + parseFloat(log.ec), 0) / totalReadings;
    const averageMoisture = ecLogs.reduce((sum, log) => sum + parseFloat(log.moisture || 0), 0) / totalReadings;
    const averageHealthScore = ecLogs.reduce((sum, log) => sum + (parseFloat(log.overall_health_score) || 50), 0) / totalReadings;

    res.json({
      success: true,
      hasData: true,
      data: {
        user: user,
        currentEC: Math.round(currentEC * 100) / 100,
        currentMoisture: Math.round(currentMoisture * 10) / 10,
        totalReadings: totalReadings,
        averageEC: Math.round(averageEC * 100) / 100,
        averageMoisture: Math.round(averageMoisture * 10) / 10,
        averageHealthScore: Math.round(averageHealthScore),
        ecLogs: ecLogs.map(log => ({
          ec: parseFloat(log.ec),
          moisture: parseFloat(log.moisture || 0),
          created_at: log.created_at,
          health_score: parseFloat(log.overall_health_score || 50),
          ec_status: log.ec_status,
          moisture_status: log.moisture_status
        })),
        currentStatus: currentReading.ec_status || 'Unknown',
        readinessStatus: currentReading.readiness_status || 'Unknown',
        estimatedReadyDays: currentReading.estimated_ready_days,
        primaryRecommendation: currentReading.primary_recommendation || 'Continue monitoring',
        alertLevel: currentReading.alert_level || 'none',
        alertMessage: currentReading.alert_message
      }
    });

  } catch (error) {
    console.error('Error getting user soil EC:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
  }
};

/**
 * Get EC predictions for a user
 * GET /api/user/:username/ec-predictions
 */
const getUserECPredictions = async (req, res) => {
  try {
    const { username } = req.params;

    // Get user info
    const userQuery = `SELECT telegram_id, username FROM users WHERE username = $1`;
    const userResult = await pool.query(userQuery, [username]);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    const user = userResult.rows[0];
    const { telegram_id } = user;

    // Get latest prediction data
    const latestPredictionQuery = `
      SELECT ec, moisture, 
             daily_predictions, prediction_dates,
             week_1_prediction, week_2_prediction,
             month_1_prediction, month_2_prediction, month_3_prediction,
             avg_ec_prediction, max_ec_prediction, min_ec_prediction,
             ec_trend, trend_strength, trend_description,
             readiness_status, estimated_ready_days, estimated_ready_date,
             readiness_confidence, current_maturity_stage,
             completion_percentage, quality_score,
             alert_level, alert_message, action_required,
             primary_recommendation, nutrient_recommendation,
             moisture_recommendation, timeline_recommendation,
             created_at
      FROM compost_status 
      WHERE telegram_id = $1 
        AND prediction_generated = true
        AND prediction_success = true
      ORDER BY created_at DESC 
      LIMIT 1
    `;
    const predictionResult = await pool.query(latestPredictionQuery, [telegram_id]);

    if (predictionResult.rows.length === 0) {
      return res.json({
        success: true,
        hasData: false,
        message: 'No prediction data available',
        data: {
          predictions: [],
          forecasts: [],
          timeline: {},
          recommendations: {},
          alerts: [],
          overall_summary: 'No prediction data available - take an EC reading to get forecasts'
        }
      });
    }

    const predData = predictionResult.rows[0];
    
    // Process daily predictions for chart
    let forecasts = [];
    if (predData.daily_predictions && predData.prediction_dates) {
      const predictions = Array.isArray(predData.daily_predictions) ? predData.daily_predictions : JSON.parse(predData.daily_predictions);
      const dates = Array.isArray(predData.prediction_dates) ? predData.prediction_dates : JSON.parse(predData.prediction_dates);
      
      forecasts = predictions.map((pred, index) => ({
        date: dates[index],
        predicted_ec: parseFloat(pred),
        day_number: index + 1,
        status: pred >= 1.5 && pred <= 3.0 ? 'optimal' : (pred < 1.5 ? 'low' : 'high')
      }));
    }

    // Generate key timeline predictions
    const timeline = {
      week_1: parseFloat(predData.week_1_prediction || 0),
      week_2: parseFloat(predData.week_2_prediction || 0),
      month_1: parseFloat(predData.month_1_prediction || 0),
      month_2: parseFloat(predData.month_2_prediction || 0),
      month_3: parseFloat(predData.month_3_prediction || 0),
      average: parseFloat(predData.avg_ec_prediction || 0),
      max_value: parseFloat(predData.max_ec_prediction || 0),
      min_value: parseFloat(predData.min_ec_prediction || 0)
    };

    // Compile recommendations
    const recommendations = {
      primary: predData.primary_recommendation,
      nutrient: predData.nutrient_recommendation,
      moisture: predData.moisture_recommendation,
      timeline: predData.timeline_recommendation,
      trend: predData.trend_description
    };

    // Process alerts
    const alerts = [];
    if (predData.alert_level && predData.alert_level !== 'none') {
      alerts.push({
        level: predData.alert_level,
        message: predData.alert_message,
        action_required: predData.action_required,
        created_at: predData.created_at
      });
    }

    // Generate overall summary
    let overall_summary = '';
    if (predData.readiness_status === 'ready_soon') {
      overall_summary = `🎉 Excellent! Your compost will be ready in ~${predData.estimated_ready_days} days. Continue current management.`;
    } else if (predData.readiness_status === 'short_term') {
      overall_summary = `✅ Good progress! Estimated ready in ~${predData.estimated_ready_days} days. Monitor trends closely.`;
    } else if (predData.readiness_status === 'medium_term') {
      overall_summary = `⏳ Making steady progress. Estimated ready in ~${predData.estimated_ready_days} days. Patience required.`;
    } else if (predData.readiness_status === 'needs_attention') {
      overall_summary = `⚠️ Needs attention. Current conditions may delay readiness. Follow recommendations below.`;
    } else {
      overall_summary = `📊 EC levels being monitored. Continue taking readings for better predictions.`;
    }

    res.json({
      success: true,
      hasData: true,
      data: {
        current_ec: parseFloat(predData.ec),
        current_moisture: parseFloat(predData.moisture || 0),
        predictions: forecasts.slice(0, 30), // Next 30 days for chart
        forecasts: forecasts,
        timeline: timeline,
        trend: {
          direction: predData.ec_trend,
          strength: parseFloat(predData.trend_strength || 0),
          description: predData.trend_description
        },
        readiness: {
          status: predData.readiness_status,
          estimated_days: predData.estimated_ready_days,
          estimated_date: predData.estimated_ready_date,
          confidence: predData.readiness_confidence,
          maturity_stage: predData.current_maturity_stage,
          completion_percentage: parseFloat(predData.completion_percentage || 0)
        },
        quality: {
          score: parseFloat(predData.quality_score || 0),
          description: predData.quality_score > 8 ? 'Excellent' : 
                      predData.quality_score > 6 ? 'Good' : 
                      predData.quality_score > 4 ? 'Fair' : 'Needs Improvement'
        },
        recommendations: recommendations,
        alerts: alerts,
        overall_summary: overall_summary,
        last_updated: predData.created_at
      }
    });

  } catch (error) {
    console.error('Error getting EC predictions:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
  }
};

module.exports = {
  getUsersWithFeedingData,
  getUserCO2Impact,
  getGlobalStats,
  getUserFeedingLogs,
  getDashboardStats,
  getHistoricalData,
  getPredictionData,
  getDevicesWithSensors,
  getPlantMoistureUsers,
  getUserPlantMoisture,
  getUserMoisturePredictions,
  getSoilECUsers,
  getUserSoilEC,
  getUserECPredictions
};