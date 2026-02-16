"""
API Configuration.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """API configuration"""
    
    # Flask
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('API_HOST', '0.0.0.0')
    PORT = int(os.getenv('API_PORT', '5002'))
    
    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour
    
    # Model
    MODEL_PATH = os.getenv('MODEL_PATH', '../ml_service/saved_models/fire_risk_xgboost_v1.pkl')
    MODEL_VERSION = 'v1.0'
    
    # API Settings
    MAX_BATCH_SIZE = 100  # Max predictions per request
    RATE_LIMIT = 100  # Requests per minute

config = Config()