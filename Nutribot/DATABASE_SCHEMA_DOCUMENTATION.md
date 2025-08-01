# Comprehensive Compost Prediction Database Schema

## Overview
This document outlines all the database columns added to store complete ML prediction data for the dashboard. The enhanced `compost_status` table now captures everything from basic readings to comprehensive analytics.

## Column Categories

### 📊 **Core Data Columns**
- `ec` - EC reading in mS/cm
- `moisture` - Moisture percentage (0-100)
- `created_at` - Timestamp of the reading
- `telegram_id` / `username` - User identification

### 🤖 **Prediction Metadata**
- `prediction_generated` (BOOLEAN) - Whether ML prediction was attempted
- `prediction_success` (BOOLEAN) - Whether ML prediction succeeded
- `prediction_error` (TEXT) - Error message if prediction failed
- `forecast_date` (TIMESTAMPTZ) - When the prediction was generated

### 📅 **Time-Based Predictions**
- `week_1_prediction` (DECIMAL) - EC prediction for day 7
- `week_2_prediction` (DECIMAL) - EC prediction for day 14
- `month_1_prediction` (DECIMAL) - EC prediction for day 30
- `month_2_prediction` (DECIMAL) - EC prediction for day 60
- `month_3_prediction` (DECIMAL) - EC prediction for day 90

### 📈 **Statistical Analysis**
- `avg_ec_prediction` (DECIMAL) - Average EC over 90 days
- `max_ec_prediction` (DECIMAL) - Maximum EC in 90-day period
- `min_ec_prediction` (DECIMAL) - Minimum EC in 90-day period

### 📊 **Trend Analysis**
- `ec_trend` (VARCHAR) - 'rising', 'declining', 'stable'
- `trend_strength` (DECIMAL) - Numerical strength (0-1)
- `trend_description` (TEXT) - Human-readable trend explanation

### 🎯 **Readiness Estimation**
- `readiness_status` (VARCHAR) - 'ready_soon', 'short_term', 'medium_term', 'long_term', 'needs_attention'
- `estimated_ready_days` (INTEGER) - Days until ready (NULL if >90 days)
- `estimated_ready_date` (TIMESTAMPTZ) - Actual estimated completion date
- `readiness_confidence` (VARCHAR) - 'high', 'medium', 'low'
- `current_maturity_stage` (VARCHAR) - Current decomposition stage

### 🔍 **Condition Assessment**
- `ec_status` (VARCHAR) - 'low', 'optimal', 'high', 'very_high'
- `moisture_status` (VARCHAR) - 'low', 'optimal', 'high', 'very_high'
- `overall_health_score` (INTEGER) - Health score 0-100
- `health_description` (TEXT) - Overall health assessment

### 💡 **Recommendations**
- `primary_recommendation` (TEXT) - Main action to take
- `secondary_recommendation` (TEXT) - Additional suggestion
- `nutrient_recommendation` (TEXT) - Nutrient management guidance
- `moisture_recommendation` (TEXT) - Moisture management guidance
- `timeline_recommendation` (TEXT) - Timeline expectations

### 📊 **Chart Data (JSON)**
- `daily_predictions` (JSONB) - 90-day daily EC predictions array
- `prediction_dates` (JSONB) - Corresponding dates array
- `weekly_summaries` (JSONB) - Week-by-week summaries
- `monthly_summaries` (JSONB) - Month-by-month summaries

### 🎛️ **Dashboard Metrics**
- `completion_percentage` (DECIMAL) - Estimated % complete (0-100)
- `quality_score` (DECIMAL) - Overall quality score (0-10)
- `stability_index` (DECIMAL) - Condition stability (0-10)
- `optimal_range_days` (INTEGER) - Days in optimal range (next 30)

### 📊 **Historical Tracking**
- `previous_ec` (DECIMAL) - Previous reading for comparison
- `ec_change_rate` (DECIMAL) - Rate of change per day
- `improvement_trend` (BOOLEAN) - Whether improving
- `days_in_optimal_range` (INTEGER) - Consecutive days optimal

### 🚨 **Alert System**
- `alert_level` (VARCHAR) - 'none', 'info', 'warning', 'critical'
- `alert_message` (TEXT) - Alert description
- `action_required` (BOOLEAN) - Whether immediate action needed
- `next_check_date` (TIMESTAMPTZ) - When to check again

## Dashboard Usage Examples

### 📊 **Main Dashboard Cards**
```sql
SELECT 
    ec, moisture, 
    completion_percentage, 
    quality_score, 
    overall_health_score,
    readiness_status,
    estimated_ready_days
FROM compost_status 
WHERE telegram_id = ? 
ORDER BY created_at DESC 
LIMIT 1;
```

### 📈 **Historical Charts**
```sql
SELECT 
    created_at, 
    ec, 
    moisture,
    overall_health_score
FROM compost_status 
WHERE telegram_id = ? 
  AND created_at >= NOW() - INTERVAL '30 days'
ORDER BY created_at;
```

### 🔮 **Prediction Charts**
```sql
SELECT 
    daily_predictions,
    prediction_dates,
    week_1_prediction,
    month_1_prediction,
    month_3_prediction
FROM compost_status 
WHERE telegram_id = ? 
  AND prediction_generated = true
ORDER BY created_at DESC 
LIMIT 1;
```

### 🎯 **Readiness Timeline**
```sql
SELECT 
    readiness_status,
    estimated_ready_days,
    estimated_ready_date,
    current_maturity_stage,
    completion_percentage
FROM compost_status 
WHERE telegram_id = ? 
  AND prediction_generated = true
ORDER BY created_at DESC 
LIMIT 1;
```

### 🚨 **Active Alerts**
```sql
SELECT 
    alert_level,
    alert_message,
    action_required,
    next_check_date
FROM compost_status 
WHERE telegram_id = ? 
  AND alert_level != 'none'
  AND created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

### 💡 **Current Recommendations**
```sql
SELECT 
    primary_recommendation,
    nutrient_recommendation,
    moisture_recommendation,
    timeline_recommendation
FROM compost_status 
WHERE telegram_id = ? 
ORDER BY created_at DESC 
LIMIT 1;
```

## Implementation Steps

1. **Run SQL Script**: Execute `add_comprehensive_prediction_columns.sql` in Supabase
2. **Database Service**: Updated `create_compost_status_with_predictions()` method
3. **Dashboard API**: Use `get_dashboard_data()` method for comprehensive data
4. **Frontend**: Query specific column sets for different dashboard components

## Data Flow

1. **User Input** → EC and moisture readings
2. **ML Processing** → 90-day predictions and analysis
3. **Database Storage** → All comprehensive data saved
4. **Dashboard Query** → Rich data retrieved for visualization
5. **User Experience** → Complete compost monitoring dashboard

## Key Features Enabled

- ✅ Complete prediction timeline (7-90 days)
- ✅ Readiness estimation with confidence levels
- ✅ Health scoring and trend analysis
- ✅ Actionable recommendations
- ✅ Alert system for issues
- ✅ Historical tracking and comparisons
- ✅ Rich chart data for visualization
- ✅ Performance-optimized queries
