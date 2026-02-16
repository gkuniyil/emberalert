"""
Load and prepare training data from database.
Creates train/test splits for model training.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from database.connection import db
import logging

logger = logging.getLogger(__name__)

class TrainingDataLoader:
    """Load data from PostgreSQL for ML training"""
    
    def load_historical_data(self, limit: int = 10000) -> pd.DataFrame:
        """
        Load historical weather and risk data.
        
        In production, you'd load actual historical fire events.
        For this demo, we use recent predictions as training data.
        
        Args:
            limit: Max rows to load
        
        Returns:
            DataFrame with features and target
        """
        query = """
        SELECT 
            w.temperature,
            w.humidity,
            w.wind_speed,
            w.wind_direction,
            w.pressure,
            EXTRACT(MONTH FROM w.timestamp) as month,
            EXTRACT(HOUR FROM w.timestamp) as hour,
            EXTRACT(DOY FROM w.timestamp) as day_of_year,
            p.risk_score as target
        FROM weather_data w
        JOIN fire_predictions p 
            ON w.latitude = p.latitude 
            AND w.longitude = p.longitude
            AND w.timestamp = p.prediction_time
        ORDER BY w.timestamp DESC
        LIMIT :limit
        """
        
        df = pd.read_sql(query, db.engine, params={'limit': limit})
        logger.info(f"Loaded {len(df)} training samples")
        
        return df
    
    def create_synthetic_data(self, n_samples: int = 5000) -> pd.DataFrame:
        """
        Create synthetic training data for demonstration.
        
        In real project, use actual historical fire data.
        This generates realistic weather patterns.
        
        Args:
            n_samples: Number of samples to generate
        
        Returns:
            DataFrame with synthetic features and labels
        """
        np.random.seed(42)
        
        # Generate realistic weather patterns
        data = {
            # Temperature: 50-110°F, summer peak
            'temperature': np.random.normal(75, 15, n_samples).clip(50, 110),
            
            # Humidity: 10-90%, inversely correlated with temp
            'humidity': np.random.normal(50, 20, n_samples).clip(10, 90),
            
            # Wind: 0-40 mph, mostly calm
            'wind_speed': np.random.exponential(8, n_samples).clip(0, 40),
            
            # Wind direction: 0-360 degrees
            'wind_direction': np.random.uniform(0, 360, n_samples),
            
            # Pressure: 990-1030 hPa
            'pressure': np.random.normal(1013, 10, n_samples),
            
            # Month: 1-12
            'month': np.random.randint(1, 13, n_samples),
            
            # Hour: 0-23
            'hour': np.random.randint(0, 24, n_samples),
            
            # Day of year: 1-365
            'day_of_year': np.random.randint(1, 366, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Create target based on fire risk formula
        # High temp + low humidity + high wind = high risk
        df['target'] = (
            0.4 * ((df['temperature'] - 50) / 60) +  # Normalize to 0-1
            0.3 * (1 - df['humidity'] / 100) +
            0.3 * (df['wind_speed'] / 40)
        ).clip(0, 1)
        
        # Add fire season boost (June-Oct)
        fire_season = ((df['month'] >= 6) & (df['month'] <= 10)).astype(float)
        df['target'] = (df['target'] + 0.5 * fire_season).clip(0, 1)
        
        # Add some noise
        df['target'] += np.random.normal(0, 0.05, n_samples)
        df['target'] = df['target'].clip(0, 1)
        
        logger.info(f"Generated {n_samples} synthetic samples")
        return df
    
    def prepare_data(self, df: pd.DataFrame, test_size: float = 0.2):
        """
        Split data into train/test sets.
        
        Args:
            df: Full dataset
            test_size: Fraction for testing (0.2 = 20%)
        
        Returns:
            X_train, X_test, y_train, y_test
        """
        # Separate features (X) and target (y)
        feature_cols = [
            'temperature', 'humidity', 'wind_speed', 'wind_direction',
            'pressure', 'month', 'hour', 'day_of_year'
        ]
        
        X = df[feature_cols]
        y = df['target']
        
        # Train/test split
        # random_state=42 makes it reproducible
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=test_size,
            random_state=42
        )
        
        logger.info(
            f"Train: {len(X_train)} samples, "
            f"Test: {len(X_test)} samples"
        )
        
        return X_train, X_test, y_train, y_test