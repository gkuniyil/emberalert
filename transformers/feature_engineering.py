"""
Feature engineering for fire risk prediction.
Transforms raw weather data into ML-ready features.
"""

import pandas as pd
import numpy as np
from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Create features from weather data"""
    
    # Fire danger thresholds (based on NWCG standards)
    TEMP_HIGH = 85.0      # Fahrenheit
    HUMIDITY_LOW = 30.0   # Percent
    WIND_HIGH = 15.0      # mph
    
    def create_features(self, weather_data: Dict) -> Dict:
        """
        Engineer features from weather observation.
        
        Features created:
        1. Individual risk factors (0-1 normalized)
        2. Composite risk score
        3. Temporal features (season, time of day)
        4. Interaction features
        
        Args:
            weather_data: Raw weather dictionary
        
        Returns:
            Dictionary of features
        """
        
        features = {}
        
        # === TEMPERATURE FEATURES ===
        # Higher temp = higher risk
        temp = weather_data['temperature']
        features['temperature'] = temp
        features['temp_risk'] = self._normalize_risk(
            temp, 
            threshold=self.TEMP_HIGH,
            higher_is_riskier=True
        )
        
        # === HUMIDITY FEATURES ===
        # Lower humidity = higher risk (dry vegetation)
        humidity = weather_data['humidity']
        features['humidity'] = humidity
        features['humidity_risk'] = self._normalize_risk(
            humidity,
            threshold=self.HUMIDITY_LOW,
            higher_is_riskier=False  # Low humidity is bad
        )
        
        # === WIND FEATURES ===
        # Higher wind = spreads fire faster
        wind_speed = weather_data['wind_speed']
        features['wind_speed'] = wind_speed
        features['wind_risk'] = self._normalize_risk(
            wind_speed,
            threshold=self.WIND_HIGH,
            higher_is_riskier=True
        )
        
        # === COMPOSITE RISK SCORE ===
        # Weighted average of individual risks
        features['composite_risk'] = (
            0.4 * features['temp_risk'] +
            0.3 * features['humidity_risk'] +
            0.3 * features['wind_risk']
        )
        
        # === TEMPORAL FEATURES ===
        timestamp = weather_data['timestamp']
        features['month'] = timestamp.month
        features['hour'] = timestamp.hour
        features['day_of_year'] = timestamp.timetuple().tm_yday
        
        # Fire season (June-October is peak in California)
        features['is_fire_season'] = 1 if 6 <= timestamp.month <= 10 else 0
        
        # === INTERACTION FEATURES ===
        # Combine multiple factors
        # Hot + dry + windy = extremely dangerous
        features['temp_humidity_interaction'] = (
            features['temp_risk'] * features['humidity_risk']
        )
        
        features['wind_temp_interaction'] = (
            features['wind_risk'] * features['temp_risk']
        )
        
        # === CATEGORICAL ENCODING ===
        # Convert conditions to numeric
        condition_map = {
            'Clear': 0.8,      # High risk (no clouds)
            'Clouds': 0.5,
            'Rain': 0.1,       # Low risk
            'Drizzle': 0.2,
            'Thunderstorm': 0.3,
            'Snow': 0.0
        }
        features['condition_risk'] = condition_map.get(
            weather_data.get('conditions', 'Clear'),
            0.5
        )
        
        return features
    
    def _normalize_risk(
        self, 
        value: float, 
        threshold: float,
        higher_is_riskier: bool = True
    ) -> float:
        """
        Normalize value to 0-1 risk score.
        
        Uses sigmoid function for smooth scaling:
        - Values near threshold → 0.5
        - Values far from threshold → approach 0 or 1
        
        Args:
            value: Measurement value
            threshold: Danger threshold
            higher_is_riskier: True if high values = high risk
        
        Returns:
            Risk score between 0 and 1
        """
        # Sigmoid function: 1 / (1 + e^(-x))
        # Gives S-shaped curve for smooth transitions
        
        if higher_is_riskier:
            # High values are dangerous
            normalized = (value - threshold) / threshold
        else:
            # Low values are dangerous
            normalized = (threshold - value) / threshold
        
        # Apply sigmoid
        risk = 1 / (1 + np.exp(-5 * normalized))
        
        return float(np.clip(risk, 0, 1))  # Ensure 0-1 range
    
    def create_risk_label(self, risk_score: float) -> str:
        """
        Convert numeric risk to categorical label.
        
        Risk levels:
        - LOW: 0.0-0.3
        - MODERATE: 0.3-0.6
        - HIGH: 0.6-0.8
        - EXTREME: 0.8-1.0
        """
        if risk_score < 0.3:
            return 'LOW'
        elif risk_score < 0.6:
            return 'MODERATE'
        elif risk_score < 0.8:
            return 'HIGH'
        else:
            return 'EXTREME'