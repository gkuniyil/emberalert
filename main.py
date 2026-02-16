"""
Main ETL pipeline orchestrator.
Extracts weather data, transforms to features, loads to database.
"""

import logging
from datetime import datetime
from database.connection import db
from extractors.weather_api import WeatherExtractor
from transformers.feature_engineering import FeatureEngineer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# High-risk California locations
LOCATIONS = [
    (34.05, -118.25, "Los Angeles"),
    (37.77, -122.42, "San Francisco"),
    (38.58, -121.49, "Sacramento"),
    (32.72, -117.16, "San Diego"),
    (36.74, -119.78, "Fresno"),
]

def run_pipeline():
    """Execute full ETL pipeline"""
    
    logger.info("=== EmberAlert ETL Pipeline Started ===")
    
    # Initialize components
    db.init_schema()
    extractor = WeatherExtractor()
    engineer = FeatureEngineer()
    
    for lat, lon, name in LOCATIONS:
        logger.info(f"Processing: {name}")
        
        # EXTRACT: Get weather data
        weather = extractor.get_current_weather(lat, lon)
        if not weather:
            logger.warning(f"Skipping {name} - no data")
            continue
        
        # TRANSFORM: Create features
        features = engineer.create_features(weather)
        risk_level = engineer.create_risk_label(features['composite_risk'])
        
        logger.info(
            f"{name}: {weather['temperature']}°F, "
            f"{weather['humidity']}% humidity, "
            f"Risk: {risk_level} ({features['composite_risk']:.2f})"
        )
        
        # LOAD: Save to database
        extractor.save_to_db(weather)
        
        # Save prediction
        prediction_data = {
            'latitude': lat,
            'longitude': lon,
            'prediction_time': datetime.now(),
            'risk_score': features['composite_risk'],
            'risk_level': risk_level,
            'temperature_factor': features['temp_risk'],
            'humidity_factor': features['humidity_risk'],
            'wind_factor': features['wind_risk'],
            'model_version': 'v1.0'
        }
        
        query = """
        INSERT INTO fire_predictions
        (latitude, longitude, prediction_time, risk_score, risk_level,
         temperature_factor, humidity_factor, wind_factor, model_version)
        VALUES
        (:latitude, :longitude, :prediction_time, :risk_score, :risk_level,
         :temperature_factor, :humidity_factor, :wind_factor, :model_version)
        """
        
        db.execute_query(query, prediction_data)
    
    logger.info("=== Pipeline Completed ===")

if __name__ == "__main__":
    run_pipeline()