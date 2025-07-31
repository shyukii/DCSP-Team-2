const pool = require('../config/database');

/**
 * CO2 Emissions Calculator Class
 * Matches your Python EmissionsCalculator logic
 */
class EmissionsCalculator {
  static STP_AIR_CONCENTRATION_PERCENT = 21.0;
  static STP_CO2_PPM = 415.0;
  static FOOD_WASTE_CO2_FACTOR = 2.5;
  static COMPOST_REDUCTION_FACTOR = 0.8;
  static TREE_CO2_ABSORPTION = 21.9;
  static PETROL_CO2_FACTOR = 2.33;
  static CAR_CO2_FACTOR = 0.454;

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
      SELECT greens, browns, water, created_at 
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

    // Calculate total food waste (greens + browns) in kg
    const totalFoodWasteGrams = feedingLogs.reduce((sum, log) => 
      sum + (parseFloat(log.greens) || 0) + (parseFloat(log.browns) || 0), 0
    );
    const totalFoodWasteKg = totalFoodWasteGrams / 1000;

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

    // Get all feeding logs for global calculation
    const globalLogsQuery = `
      SELECT greens, browns, water, created_at 
      FROM feeding_logs 
      ORDER BY created_at DESC
    `;
    const globalLogsResult = await pool.query(globalLogsQuery);
    const allFeedingLogs = globalLogsResult.rows;

    if (allFeedingLogs.length === 0) {
      return res.json({
        success: true,
        data: {
          totalUsers: totalUsers,
          globalFoodWaste: 0,
          globalCO2Saved: 0,
          treesPlanted: 0,
          avgPerUser: 0,
          petrolSaved: 0,
          carMilesOffset: 0
        }
      });
    }

    // Calculate global food waste
    const globalFoodWasteGrams = allFeedingLogs.reduce((sum, log) => 
      sum + (parseFloat(log.greens) || 0) + (parseFloat(log.browns) || 0), 0
    );
    const globalFoodWasteKg = globalFoodWasteGrams / 1000;

    // For global CO2 calculation, use average tank/soil volumes
    // You might want to calculate actual averages from user profiles
    const avgTankVolume = 50;  // Default average
    const avgSoilVolume = 20;  // Default average

    // Or calculate actual averages:
    const avgVolumesQuery = `
      SELECT 
        AVG(tank_volume) as avg_tank_volume,
        AVG(soil_volume) as avg_soil_volume 
      FROM users 
      WHERE tank_volume IS NOT NULL AND soil_volume IS NOT NULL
    `;
    const avgVolumesResult = await pool.query(avgVolumesQuery);
    const actualAvgTankVolume = parseFloat(avgVolumesResult.rows[0].avg_tank_volume) || avgTankVolume;
    const actualAvgSoilVolume = parseFloat(avgVolumesResult.rows[0].avg_soil_volume) || avgSoilVolume;

    // Calculate global CO2 savings
    const globalCO2Result = EmissionsCalculator.calculateCO2SavedFromFoodWaste(
      globalFoodWasteKg, 
      actualAvgTankVolume, 
      actualAvgSoilVolume
    );

    // Get global environmental impact
    const globalImpact = EmissionsCalculator.getEnvironmentalImpactSummary(globalCO2Result.totalCO2SavedKg);

    res.json({
      success: true,
      data: {
        totalUsers: totalUsers,
        globalFoodWaste: globalFoodWasteKg,
        globalCO2Saved: globalCO2Result.totalCO2SavedKg,
        treesPlanted: globalImpact.treesEquivalent,
        avgPerUser: totalUsers > 0 ? globalCO2Result.totalCO2SavedKg / totalUsers : 0,
        petrolSaved: globalImpact.petrolLitresEquivalent,
        carMilesOffset: globalImpact.carMilesEquivalent,
        totalFeedingLogs: allFeedingLogs.length,
        avgTankVolume: actualAvgTankVolume,
        avgSoilVolume: actualAvgSoilVolume
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
      SELECT greens, browns, water, created_at 
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

module.exports = {
  getUsersWithFeedingData,
  getUserCO2Impact,
  getGlobalStats,
  getUserFeedingLogs,
  getDashboardStats,
  getHistoricalData,
  getPredictionData,
  getDevicesWithSensors
};