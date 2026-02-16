"""
Main Flask application.
"""

from flask import Flask
from flask_cors import CORS
from app.config import config
from app.routes.prediction import prediction_bp
from app.routes.health import health_bp
from app.middleware.error_handler import register_error_handlers
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(name)s - %(message)s'
)

def create_app():
    """Application factory pattern"""
    
    app = Flask(__name__)
    
    # Enable CORS (allows frontend to call API)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(prediction_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    @app.route('/')
    def index():
        """Root endpoint"""
        return {
            'service': 'EmberAlert API',
            'version': config.MODEL_VERSION,
            'endpoints': {
                'health': '/health',
                'predict': '/api/v1/predict',
                'batch_predict': '/api/v1/predict/batch'
            }
        }
    
    return app