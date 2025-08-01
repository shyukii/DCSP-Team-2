-- Comprehensive prediction columns for compost_status table
-- This script adds all columns needed to store complete ML prediction data for dashboard use

-- Add columns for prediction metadata
ALTER TABLE compost_status 
ADD COLUMN prediction_generated BOOLEAN DEFAULT FALSE,
ADD COLUMN prediction_success BOOLEAN DEFAULT FALSE,
ADD COLUMN prediction_error TEXT,
ADD COLUMN forecast_date TIMESTAMPTZ;

-- Add columns for key time-based predictions
ALTER TABLE compost_status
ADD COLUMN week_1_prediction DECIMAL(5,2),    -- Day 7 prediction
ADD COLUMN week_2_prediction DECIMAL(5,2),    -- Day 14 prediction  
ADD COLUMN month_1_prediction DECIMAL(5,2),   -- Day 30 prediction
ADD COLUMN month_2_prediction DECIMAL(5,2),   -- Day 60 prediction
ADD COLUMN month_3_prediction DECIMAL(5,2);   -- Day 90 prediction

-- Add columns for 90-day statistics
ALTER TABLE compost_status
ADD COLUMN avg_ec_prediction DECIMAL(5,2),    -- Average EC over 90 days
ADD COLUMN max_ec_prediction DECIMAL(5,2),    -- Maximum EC over 90 days
ADD COLUMN min_ec_prediction DECIMAL(5,2);    -- Minimum EC over 90 days

-- Add columns for trend analysis
ALTER TABLE compost_status
ADD COLUMN ec_trend VARCHAR(20),              -- 'rising', 'declining', 'stable'
ADD COLUMN trend_strength DECIMAL(4,3),       -- Numerical trend strength
ADD COLUMN trend_description TEXT;            -- Human-readable trend description

-- Add columns for compost readiness estimation
ALTER TABLE compost_status
ADD COLUMN readiness_status VARCHAR(30),       -- 'ready_soon', 'short_term', 'medium_term', 'long_term', 'needs_attention'
ADD COLUMN estimated_ready_days INTEGER,       -- Days until ready (NULL if >90 days)
ADD COLUMN estimated_ready_date TIMESTAMPTZ,   -- Actual estimated ready date
ADD COLUMN readiness_confidence VARCHAR(20),   -- 'high', 'medium', 'low'
ADD COLUMN current_maturity_stage VARCHAR(30); -- 'building_nutrients', 'active_decomposition', 'stabilizing', 'nearly_ready', 'mature'

-- Add columns for condition assessment
ALTER TABLE compost_status
ADD COLUMN ec_status VARCHAR(20),              -- 'low', 'optimal', 'high', 'very_high'
ADD COLUMN moisture_status VARCHAR(20),        -- 'low', 'optimal', 'high', 'very_high'
ADD COLUMN overall_health_score INTEGER,       -- 1-100 score
ADD COLUMN health_description TEXT;            -- Overall health assessment

-- Add columns for recommendations
ALTER TABLE compost_status
ADD COLUMN primary_recommendation TEXT,        -- Main action to take
ADD COLUMN secondary_recommendation TEXT,      -- Additional suggestion
ADD COLUMN nutrient_recommendation TEXT,       -- Specific nutrient guidance
ADD COLUMN moisture_recommendation TEXT,       -- Moisture management guidance
ADD COLUMN timeline_recommendation TEXT;       -- Timeline expectations

-- Add columns for storing complete prediction arrays (JSON format for dashboard charts)
ALTER TABLE compost_status
ADD COLUMN daily_predictions JSONB,           -- Full 90-day daily predictions array
ADD COLUMN prediction_dates JSONB,            -- Corresponding dates array
ADD COLUMN weekly_summaries JSONB,            -- Week-by-week summaries
ADD COLUMN monthly_summaries JSONB;           -- Month-by-month summaries

-- Add columns for dashboard-specific metrics
ALTER TABLE compost_status
ADD COLUMN days_since_start INTEGER,          -- How long composting has been running
ADD COLUMN completion_percentage DECIMAL(5,2), -- Estimated % complete (0-100)
ADD COLUMN quality_score DECIMAL(4,2),        -- Overall quality score (0-10)
ADD COLUMN stability_index DECIMAL(4,2),      -- How stable the conditions are (0-10)
ADD COLUMN optimal_range_days INTEGER;        -- How many of next 30 days will be in optimal range

-- Add columns for historical tracking
ALTER TABLE compost_status
ADD COLUMN previous_ec DECIMAL(5,2),          -- Previous reading for comparison
ADD COLUMN ec_change_rate DECIMAL(6,3),       -- Rate of change per day
ADD COLUMN improvement_trend BOOLEAN,          -- Whether conditions are improving
ADD COLUMN days_in_optimal_range INTEGER;     -- Consecutive days in optimal range

-- Add columns for alert system
ALTER TABLE compost_status
ADD COLUMN alert_level VARCHAR(20),           -- 'none', 'info', 'warning', 'critical'
ADD COLUMN alert_message TEXT,                -- Alert description
ADD COLUMN action_required BOOLEAN DEFAULT FALSE, -- Whether immediate action needed
ADD COLUMN next_check_date TIMESTAMPTZ;       -- When to check again

-- Add indexes for better dashboard performance
CREATE INDEX IF NOT EXISTS idx_compost_status_user_date ON compost_status(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_compost_status_prediction_date ON compost_status(forecast_date DESC) WHERE prediction_generated = TRUE;
CREATE INDEX IF NOT EXISTS idx_compost_status_readiness ON compost_status(readiness_status, estimated_ready_days) WHERE prediction_generated = TRUE;
CREATE INDEX IF NOT EXISTS idx_compost_status_health ON compost_status(overall_health_score DESC) WHERE prediction_generated = TRUE;

-- Add comments for documentation
COMMENT ON COLUMN compost_status.prediction_generated IS 'Whether ML prediction was generated for this reading';
COMMENT ON COLUMN compost_status.readiness_status IS 'Overall readiness category: ready_soon, short_term, medium_term, long_term, needs_attention';
COMMENT ON COLUMN compost_status.daily_predictions IS 'JSON array of 90 daily EC predictions for chart visualization';
COMMENT ON COLUMN compost_status.completion_percentage IS 'Estimated completion percentage based on EC trends and timeline';
COMMENT ON COLUMN compost_status.quality_score IS 'Overall compost quality score (0-10) based on EC, moisture, and trends';
COMMENT ON COLUMN compost_status.stability_index IS 'How stable conditions are (0-10), higher = more predictable';
COMMENT ON COLUMN compost_status.alert_level IS 'Alert priority: none, info, warning, critical';

-- Verify the changes
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'compost_status' 
  AND column_name LIKE '%prediction%' 
     OR column_name LIKE '%readiness%' 
     OR column_name LIKE '%trend%'
     OR column_name LIKE '%score%'
ORDER BY ordinal_position;
