-- Weather observations table
-- Stores real-time weather data from API
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Temperature (Fahrenheit)
    temperature DECIMAL(5, 2),
    humidity INTEGER,  -- Percentage 0-100
    
    -- Wind
    wind_speed DECIMAL(5, 2),  -- mph
    wind_direction INTEGER,    -- degrees
    
    -- Conditions
    conditions VARCHAR(50),
    pressure INTEGER,          -- hPa
    
    -- Indexing for fast queries by location and time
    created_at TIMESTAMP DEFAULT NOW()
);

-- Fire risk predictions table
-- Stores ML model predictions
CREATE TABLE IF NOT EXISTS fire_predictions (
    id SERIAL PRIMARY KEY,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    prediction_time TIMESTAMP NOT NULL,
    
    -- Risk score (0-1, higher = more dangerous)
    risk_score DECIMAL(4, 3) NOT NULL,
    risk_level VARCHAR(20),  -- LOW, MODERATE, HIGH, EXTREME
    
    -- Contributing factors
    temperature_factor DECIMAL(4, 3),
    humidity_factor DECIMAL(4, 3),
    wind_factor DECIMAL(4, 3),
    
    model_version VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Feature store table
-- Caches computed features for ML
CREATE TABLE IF NOT EXISTS feature_store (
    id SERIAL PRIMARY KEY,
    location_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Engineered features (JSON for flexibility)
    features JSONB NOT NULL,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Unique constraint: one feature set per location/time
    UNIQUE(location_id, timestamp)
);

-- Indexes for performance
CREATE INDEX idx_weather_location ON weather_data(latitude, longitude);
CREATE INDEX idx_weather_time ON weather_data(timestamp DESC);
CREATE INDEX idx_predictions_location ON fire_predictions(latitude, longitude);
CREATE INDEX idx_predictions_time ON fire_predictions(prediction_time DESC);