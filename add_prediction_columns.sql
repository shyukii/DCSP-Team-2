-- Add prediction columns to existing compost_status table
-- Run this in your Supabase SQL editor

ALTER TABLE compost_status 
ADD COLUMN prediction_generated BOOLEAN DEFAULT FALSE;

ALTER TABLE compost_status 
ADD COLUMN week_1_prediction NUMERIC(5,2);

ALTER TABLE compost_status 
ADD COLUMN week_2_prediction NUMERIC(5,2);

ALTER TABLE compost_status 
ADD COLUMN month_1_prediction NUMERIC(5,2);

ALTER TABLE compost_status 
ADD COLUMN month_2_prediction NUMERIC(5,2);

ALTER TABLE compost_status 
ADD COLUMN month_3_prediction NUMERIC(5,2);

ALTER TABLE compost_status 
ADD COLUMN avg_ec_prediction NUMERIC(5,2);

ALTER TABLE compost_status 
ADD COLUMN max_ec_prediction NUMERIC(5,2);

ALTER TABLE compost_status 
ADD COLUMN min_ec_prediction NUMERIC(5,2);

ALTER TABLE compost_status 
ADD COLUMN prediction_date TIMESTAMPTZ;

-- Add comment to document the new columns
COMMENT ON COLUMN compost_status.prediction_generated IS 'Whether ML predictions were generated for this reading';
COMMENT ON COLUMN compost_status.week_1_prediction IS 'Predicted EC value at day 7';
COMMENT ON COLUMN compost_status.week_2_prediction IS 'Predicted EC value at day 14';
COMMENT ON COLUMN compost_status.month_1_prediction IS 'Predicted EC value at day 30';
COMMENT ON COLUMN compost_status.month_2_prediction IS 'Predicted EC value at day 60';
COMMENT ON COLUMN compost_status.month_3_prediction IS 'Predicted EC value at day 90';
COMMENT ON COLUMN compost_status.avg_ec_prediction IS 'Average EC over 90-day prediction period';
COMMENT ON COLUMN compost_status.max_ec_prediction IS 'Maximum EC over 90-day prediction period';
COMMENT ON COLUMN compost_status.min_ec_prediction IS 'Minimum EC over 90-day prediction period';
COMMENT ON COLUMN compost_status.prediction_date IS 'When the prediction was generated';

-- Optional: Create index for better query performance
CREATE INDEX idx_compost_status_prediction_date ON compost_status(prediction_date);
CREATE INDEX idx_compost_status_prediction_generated ON compost_status(prediction_generated);
