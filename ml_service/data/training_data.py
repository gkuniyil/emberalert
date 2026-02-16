"""
Training data preparation for EmberAlert.
Generates synthetic fire risk data for model training.
"""

import pandas as pd
import numpy as np 
from sklearn.model_selection import train_test_split  # Split data into train/test
import logging #good for printing messages 

logger = logging.getLogger(__name__)

class TrainingDataLoader():
  """load and prepare the training data"""

  def create_synthetic_data(self, n_samples: int = 5000) ->pd.DataFrame:
    """
    generates fire risk data 
    Features: 
     temperature: 50-110°F
        - humidity: 10-90%
        - wind_speed: 0-40 mph
        - wind_direction: 0-360 degrees
        - pressure: 990-1030 hPa
        - month, hour, day_of_year: temporal features
        
    Target:
      - Fire risk score 0-1
    """

    np.random.seed(42)
    data = {
      # normal dist: 75°F avg, 15°F spread, clip to realistic CA range
      'temperature':np.random.normal(75, 15, n_samples).clip(50, 110), 
      'humidity': np.random.normal(50, 20, n_samples).clip(10, 90),
      'wind_speed': np.random.exponential(8, n_samples).clip(0, 40),
      'wind_direction': np.random.uniform(0, 360, n_samples),
      'pressure': np.random.normal(1013, 10, n_samples),
      'month': np.random.randint(1, 13, n_samples),
      'hour': np.random.randint(0, 24, n_samples),
      'day_of_year': np.random.randint(1, 366, n_samples),
    }

    #turns dictionary(data) into a table with 8 columns 
    df = pd.DataFrame(data)

    # Create target: high temp + low humidity + high wind = high risk
    #target is the answer the model learns to predict 
    df['target'] = (
      0.4 * ((df['temperature'] - 50) / 60) +
            0.3 * (1 - df['humidity'] / 100) +
            0.3 * (df['wind_speed'] / 40)
        ).clip(0, 1)
    
    # Fire season boost (June-October), so add more risk since fire season months 
    fire_season = ((df['month'] >= 6) & (df['month'] <= 10)).astype(float)
    df['target'] = (df['target'] + 0.2 * fire_season).clip(0, 1)

    #noise to help model learn variations 
    # Add ±5% random noise to prevent overfitting (model learns pattern, not formula)
    df['target']+= np.random.normal(0, 0.05, n_samples)
    df['target'] = df['target'].clip(0, 1)

    #logger that states whether functionality ran and how much data used 
    logger.info(f"Generated {n_samples} synthetic samples")
    return df
  
  def prepare_data(self, df:pd.DataFrame, test_size: float = .2):
    #defines the features 
    feature_cols = [
          'temperature', 'humidity', 'wind_speed', 'wind_direction',
            'pressure', 'month', 'hour', 'day_of_year'
      ]
    X = df[feature_cols]  # Features: what model uses to predict
    y = df['target']      # Target: what model tries to predict

    #model does not see test data during training which prevents cheating 
    #80% training and 20% testing 
    X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
      
    logger.info(f"Train: {len(X_train)} samples, Test: {len(X_test)} samples")
    return X_train, X_test, y_train, y_test 
    
      



    


    
