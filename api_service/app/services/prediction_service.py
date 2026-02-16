"""
ML prediction service.
Loads model and makes predictions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List
import joblib
from pathlib import Path
from datetime import datetime
from app.config import config
from app.services.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    """Fire risk prediction service"""
    
    def __init__(self):
        """Load ML model"""
        self.model = None
        self.model_version = config.MODEL_VERSION
        self.load_model()
    
    def load_model(self):
        """Load saved XGBoost model"""
        try:
            model_path = Path(config.MODEL_PATH)
            
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found: {model_path}")
            
            # Load model using joblib
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            
            logger.info(f"Model loaded: {model_path}")
            
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            raise
    
    def predict_single(self, request_data: Dict) -> Dict:
        """
        Make single prediction.
        
        FLOW:
        1. Check cache
        2. If miss, make prediction
        3. Cache result
        4. Return
        
        Args:
            request_data: Input features
        
        Returns:
            Prediction with risk score and level
        """
        
        # Try cache first
        cached = cache_service.get(request_data)
        if cached:
            cached['from_cache'] = True
            return cached
        
        # Prepare features
        features = self._prepare_features(request_data)
        
        # Make prediction
        risk_score = self.model.predict(features)[0]
        risk_score = float(np.clip(risk_score, 0, 1))
        
        # Determine risk level
        risk_level = self._get_risk_level(risk_score)
        
        # Calculate contributing factors
        factors = self._calculate_factors(request_data)
        
        # Build response
        prediction = {
            'latitude': request_data['latitude'],
            'longitude': request_data['longitude'],
            'risk_score': round(risk_score, 3),
            'risk_level': risk_level,
            'timestamp': datetime.now().isoformat(),
            'model_version': self.model_version,
            'contributing_factors': factors,
            'from_cache': False
        }
        
        # Cache result
        cache_service.set(request_data, prediction)
        
        return prediction
    
    def predict_batch(self, requests: List[Dict]) -> List[Dict]:
        """
        Batch predictions for efficiency.
        
        WHY BATCHING:
        - Processes multiple requests at once
        - More efficient than looping
        - Better model inference performance
        
        Args:
            requests: List of request dictionaries
        
        Returns:
            List of predictions
        """
        predictions = []
        
        # Separate cached and uncached
        uncached_requests = []
        uncached_indices = []
        
        for i, req in enumerate(requests):
            cached = cache_service.get(req)
            if cached:
                cached['from_cache'] = True
                predictions.append(cached)
            else:
                uncached_requests.append(req)
                uncached_indices.append(i)
                predictions.append(None)  # Placeholder
        
        # Batch predict uncached
        if uncached_requests:
            features_batch = pd.DataFrame([
                self._prepare_features(req) for req in uncached_requests
            ])
            
            risk_scores = self.model.predict(features_batch)
            
            # Build responses
            for i, (req, score) in enumerate(zip(uncached_requests, risk_scores)):
                score = float(np.clip(score, 0, 1))
                
                prediction = {
                    'latitude': req['latitude'],
                    'longitude': req['longitude'],
                    'risk_score': round(score, 3),
                    'risk_level': self._get_risk_level(score),
                    'timestamp': datetime.now().isoformat(),
                    'model_version': self.model_version,
                    'contributing_factors': self._calculate_factors(req),
                    'from_cache': False
                }
                
                # Cache it
                cache_service.set(req, prediction)
                
                # Insert at correct position
                original_idx = uncached_indices[i]
                predictions[original_idx] = prediction
        
        return predictions
    
    def _prepare_features(self, request_data: Dict) -> pd.DataFrame:
        """
        Convert request to model input format.
        
        Must match training data format exactly!
        """
        # Extract current time features
        now = datetime.now()
        
        features = {
            'temperature': request_data['temperature'],
            'humidity': request_data['humidity'],
            'wind_speed': request_data['wind_speed'],
            'wind_direction': request_data.get('wind_direction', 0),
            'pressure': request_data.get('pressure', 1013),
            'month': now.month,
            'hour': now.hour,
            'day_of_year': now.timetuple().tm_yday
        }
        
        return pd.DataFrame([features])
    
    def _get_risk_level(self, risk_score: float) -> str:
        """
        Convert numeric score to category.
        
        THRESHOLDS (same as training):
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
    
    def _calculate_factors(self, request_data: Dict) -> Dict:
        """
        Calculate individual risk factors.
        
        Helps explain prediction to users.
        """
        temp = request_data['temperature']
        humidity = request_data['humidity']
        wind = request_data['wind_speed']
        
        return {
            'temperature_factor': round(max(0, (temp - 70) / 40), 3),
            'humidity_factor': round(max(0, (50 - humidity) / 50), 3),
            'wind_factor': round(min(1, wind / 20), 3)
        }

# Global prediction service
prediction_service = PredictionService()