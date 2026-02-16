"""
Prediction API endpoints.
"""

from flask import Blueprint, request, jsonify
from app.models.schemas import (
    PredictionRequest,
    BatchPredictionRequest,
    PredictionResponse,
    BatchPredictionResponse
)
from app.services.prediction_service import prediction_service
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

# Create blueprint
prediction_bp = Blueprint('prediction', __name__, url_prefix='/api/v1')

@prediction_bp.route('/predict', methods=['POST'])
def predict():
    """
    Single prediction endpoint.
    
    REQUEST:
        POST /api/v1/predict
        {
            "latitude": 34.05,
            "longitude": -118.25,
            "temperature": 95.0,
            "humidity": 25.0,
            "wind_speed": 20.0
        }
    
    RESPONSE:
        {
            "latitude": 34.05,
            "longitude": -118.25,
            "risk_score": 0.845,
            "risk_level": "EXTREME",
            "timestamp": "2025-01-22T10:30:00",
            "model_version": "v1.0"
        }
    """
    try:
        # Validate request
        data = request.get_json()
        validated = PredictionRequest(**data)
        
        # Make prediction
        result = prediction_service.predict_single(validated.dict())
        
        # Return response
        return jsonify(result), 200
        
    except ValidationError as e:
        # Pydantic validation error
        return jsonify({
            'error': 'Validation error',
            'details': e.errors()
        }), 400
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e)
        }), 500


@prediction_bp.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    Batch prediction endpoint.
    
    REQUEST:
        POST /api/v1/predict/batch
        {
            "predictions": [
                {...}, {...}, {...}
            ]
        }
    
    RESPONSE:
        {
            "predictions": [...],
            "total": 3,
            "model_version": "v1.0"
        }
    """
    try:
        data = request.get_json()
        validated = BatchPredictionRequest(**data)
        
        # Make batch predictions
        requests_list = [p.dict() for p in validated.predictions]
        results = prediction_service.predict_batch(requests_list)
        
        response = {
            'predictions': results,
            'total': len(results),
            'model_version': prediction_service.model_version
        }
        
        return jsonify(response), 200
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error',
            'details': e.errors()
        }), 400
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({
            'error': 'Batch prediction failed',
            'message': str(e)
        }), 500


@prediction_bp.route('/model/info', methods=['GET'])
def model_info():
    """
    Get model information.
    
    RESPONSE:
        {
            "version": "v1.0",
            "model_type": "XGBoost",
            "features": [...]
        }
    """
    return jsonify({
        'version': prediction_service.model_version,
        'model_type': 'XGBoost Regressor',
        'model_loaded': prediction_service.model is not None
    }), 200