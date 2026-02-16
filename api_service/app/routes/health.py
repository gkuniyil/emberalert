"""
Health check and monitoring endpoints.
"""

from flask import Blueprint, jsonify
from app.services.prediction_service import prediction_service
from app.services.cache_service import cache_service
from app.config import config
from datetime import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check.
    
    Used by:
    - Load balancers
    - Kubernetes
    - Monitoring systems
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': config.MODEL_VERSION
    }), 200


@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health():
    """
    Detailed health check with component status.
    """
    model_loaded = prediction_service.model is not None
    cache_stats = cache_service.get_stats()
    
    status = 'healthy' if model_loaded and cache_stats.get('connected') else 'degraded'
    
    return jsonify({
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'components': {
            'model': {
                'loaded': model_loaded,
                'version': config.MODEL_VERSION
            },
            'cache': cache_stats
        }
    }), 200


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    Prometheus-style metrics endpoint.
    """
    cache_stats = cache_service.get_stats()
    
    return jsonify({
        'cache_hits': cache_stats.get('hits', 0),
        'cache_misses': cache_stats.get('misses', 0),
        'cache_hit_rate': cache_stats.get('hit_rate', 0),
        'total_cached_keys': cache_stats.get('total_keys', 0)
    }), 200

"""
Health check and monitoring endpoints.
"""

from flask import Blueprint, jsonify
from app.services.prediction_service import prediction_service
from app.services.cache_service import cache_service
from app.config import config
from datetime import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check.
    
    Used by:
    - Load balancers
    - Kubernetes
    - Monitoring systems
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': config.MODEL_VERSION
    }), 200


@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health():
    """
    Detailed health check with component status.
    """
    model_loaded = prediction_service.model is not None
    cache_stats = cache_service.get_stats()
    
    status = 'healthy' if model_loaded and cache_stats.get('connected') else 'degraded'
    
    return jsonify({
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'components': {
            'model': {
                'loaded': model_loaded,
                'version': config.MODEL_VERSION
            },
            'cache': cache_stats
        }
    }), 200


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    Prometheus-style metrics endpoint.
    """
    cache_stats = cache_service.get_stats()
    
    return jsonify({
        'cache_hits': cache_stats.get('hits', 0),
        'cache_misses': cache_stats.get('misses', 0),
        'cache_hit_rate': cache_stats.get('hit_rate', 0),
        'total_cached_keys': cache_stats.get('total_keys', 0)
    }), 200