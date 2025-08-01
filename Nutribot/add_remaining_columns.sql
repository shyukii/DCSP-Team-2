-- Add remaining comprehensive prediction columns for compost_status table
-- Run this script to add all missing columns for complete dashboard functionality

-- Add columns for trend analysis (if not already exists)
ALTER TABLE compost_status
ADD COLUMN IF NOT EXISTS ec_trend VARCHAR(20),              -- 'rising', 'declining', 'stable'
ADD COLUMN IF NOT EXISTS trend_strength DECIMAL(4,3),       -- Numerical trend strength
ADD COLUMN IF NOT EXISTS trend_description TEXT;            -- Human-readable trend description

-- Add columns for compost readiness estimation
ALTER TABLE compost_status
ADD COLUMN IF NOT EXISTS readiness_status VARCHAR(30),       -- 'ready_soon', 'short_term', 'medium_term', 'long_term', 'needs_attention'
ADD COLUMN IF NOT EXISTS estimated_ready_days INTEGER,       -- Days until ready (NULL if >90 days)
ADD COLUMN IF NOT EXISTS estimated_ready_date TIMESTAMPTZ,   -- Actual estimated ready date
ADD COLUMN IF NOT EXISTS readiness_confidence VARCHAR(20),   -- 'high', 'medium', 'low'
ADD COLUMN IF NOT EXISTS current_maturity_stage VARCHAR(30); -- 'building_nutrients', 'active_decomposition', 'stabilizing', 'nearly_ready', 'mature'

-- Add columns for condition assessment
ALTER TABLE compost_status
ADD COLUMN IF NOT EXISTS ec_status VARCHAR(20),              -- 'low', 'optimal', 'high', 'very_high'
ADD COLUMN IF NOT EXISTS moisture_status VARCHAR(20),        -- 'low', 'optimal', 'high', 'very_high'
ADD COLUMN IF NOT EXISTS overall_health_score INTEGER,       -- 1-100 score
ADD COLUMN IF NOT EXISTS health_description TEXT;            -- Overall health assessment

-- Add columns for recommendations
ALTER TABLE compost_status
ADD COLUMN IF NOT EXISTS primary_recommendation TEXT,        -- Main action to take
ADD COLUMN IF NOT EXISTS secondary_recommendation TEXT,      -- Additional suggestion
ADD COLUMN IF NOT EXISTS nutrient_recommendation TEXT,       -- Specific nutrient guidance
ADD COLUMN IF NOT EXISTS moisture_recommendation TEXT,       -- Moisture management guidance
ADD COLUMN IF NOT EXISTS timeline_recommendation TEXT;       -- Timeline expectations

-- Add columns for storing complete prediction arrays (JSON format for dashboard charts)
ALTER TABLE compost_status
ADD COLUMN IF NOT EXISTS daily_predictions JSONB,           -- Full 90-day daily predictions array
ADD COLUMN IF NOT EXISTS prediction_dates JSONB,            -- Corresponding dates array
ADD COLUMN IF NOT EXISTS weekly_summaries JSONB,            -- Week-by-week summaries
ADD COLUMN IF NOT EXISTS monthly_summaries JSONB;           -- Month-by-month summaries

-- Add columns for dashboard-specific metrics
ALTER TABLE compost_status
ADD COLUMN IF NOT EXISTS days_since_start INTEGER,          -- How long composting has been running
ADD COLUMN IF NOT EXISTS completion_percentage DECIMAL(5,2), -- Estimated % complete (0-100)
ADD COLUMN IF NOT EXISTS quality_score DECIMAL(4,2),        -- Overall quality score (0-10)
ADD COLUMN IF NOT EXISTS stability_index DECIMAL(4,2),      -- How stable the conditions are (0-10)
ADD COLUMN IF NOT EXISTS optimal_range_days INTEGER;        -- How many of next 30 days will be in optimal range

-- Add columns for historical tracking
ALTER TABLE compost_status
ADD COLUMN IF NOT EXISTS previous_ec DECIMAL(5,2),          -- Previous reading for comparison
ADD COLUMN IF NOT EXISTS ec_change_rate DECIMAL(6,3),       -- Rate of change per day
ADD COLUMN IF NOT EXISTS improvement_trend BOOLEAN,          -- Whether conditions are improving
ADD COLUMN IF NOT EXISTS days_in_optimal_range INTEGER;     -- Consecutive days in optimal range

-- Add columns for alert system
ALTER TABLE compost_status
ADD COLUMN IF NOT EXISTS alert_level VARCHAR(20),           -- 'none', 'info', 'warning', 'critical'
ADD COLUMN IF NOT EXISTS alert_message TEXT,                -- Alert description
ADD COLUMN IF NOT EXISTS action_required BOOLEAN DEFAULT FALSE, -- Whether immediate action needed
ADD COLUMN IF NOT EXISTS next_check_date TIMESTAMPTZ;       -- When to check again

-- Fix the prediction metadata columns (update existing ones if needed)
ALTER TABLE compost_status
ADD COLUMN IF NOT EXISTS prediction_success BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS prediction_error TEXT,
ADD COLUMN IF NOT EXISTS forecast_date TIMESTAMPTZ;

-- Add indexes for better dashboard performance
CREATE INDEX IF NOT EXISTS idx_compost_status_telegram_date ON compost_status(telegram_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_compost_status_prediction_date ON compost_status(forecast_date DESC) WHERE prediction_generated = TRUE;
CREATE INDEX IF NOT EXISTS idx_compost_status_readiness ON compost_status(readiness_status, estimated_ready_days) WHERE prediction_generated = TRUE;
CREATE INDEX IF NOT EXISTS idx_compost_status_health ON compost_status(overall_health_score DESC) WHERE prediction_generated = TRUE;
CREATE INDEX IF NOT EXISTS idx_compost_status_alerts ON compost_status(alert_level, created_at DESC) WHERE alert_level != 'none';

-- Add comments for documentation
COMMENT ON COLUMN compost_status.readiness_status IS 'Overall readiness category: ready_soon, short_term, medium_term, long_term, needs_attention';
COMMENT ON COLUMN compost_status.daily_predictions IS 'JSON array of 90 daily EC predictions for chart visualization';
COMMENT ON COLUMN compost_status.completion_percentage IS 'Estimated completion percentage based on EC trends and timeline';
COMMENT ON COLUMN compost_status.quality_score IS 'Overall compost quality score (0-10) based on EC, moisture, and trends';
COMMENT ON COLUMN compost_status.stability_index IS 'How stable conditions are (0-10), higher = more predictable';
COMMENT ON COLUMN compost_status.alert_level IS 'Alert priority: none, info, warning, critical';

-- Verify the new columns were added
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'compost_status' 
  AND (column_name LIKE '%readiness%' 
     OR column_name LIKE '%recommendation%' 
     OR column_name LIKE '%score%'
     OR column_name LIKE '%alert%'
     OR column_name LIKE '%trend%'
     OR column_name = 'daily_predictions'
     OR column_name = 'completion_percentage')
ORDER BY ordinal_position;
