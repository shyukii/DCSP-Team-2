-- Create table for storing EC predictions
CREATE TABLE ec_predictions (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    username VARCHAR(255),
    prediction_date TIMESTAMPTZ NOT NULL,
    predicted_ec NUMERIC(5,2) NOT NULL,
    day_number INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Foreign key constraint (optional, if you want to ensure referential integrity)
    CONSTRAINT fk_telegram_id FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
);

-- Create indexes for better performance
CREATE INDEX idx_ec_predictions_telegram_id ON ec_predictions(telegram_id);
CREATE INDEX idx_ec_predictions_prediction_date ON ec_predictions(prediction_date);
CREATE INDEX idx_ec_predictions_created_at ON ec_predictions(created_at);

-- Enable Row Level Security (RLS) if needed
ALTER TABLE ec_predictions ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow users to see only their own predictions (optional)
CREATE POLICY "Users can view own predictions" ON ec_predictions
    FOR SELECT USING (auth.uid()::text = telegram_id::text);

-- Create a policy to allow inserts (optional, adjust based on your auth setup)
CREATE POLICY "Allow prediction inserts" ON ec_predictions
    FOR INSERT WITH CHECK (true);
