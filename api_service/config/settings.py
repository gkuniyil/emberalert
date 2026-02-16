"""
Configuration management using environment variables.
Keeps secrets out of code and allows different configs for dev/prod.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    """PostgreSQL connection settings"""
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', '5432'))
    database: str = os.getenv('DB_NAME', 'emberalert')
    user: str = os.getenv('DB_USER', 'postgres')
    password: str = os.getenv('DB_PASSWORD', 'password')
    
    def get_url(self) -> str:
        """SQLAlchemy connection string"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class RedisConfig:
    """Redis caching configuration"""
    host: str = os.getenv('REDIS_HOST', 'localhost')
    port: int = int(os.getenv('REDIS_PORT', '6379'))
    ttl: int = 3600  # Cache for 1 hour

@dataclass
class WeatherAPIConfig:
    """OpenWeatherMap API settings"""
    api_key: str = os.getenv('OPENWEATHER_API_KEY', '')
    base_url: str = 'https://api.openweathermap.org/data/2.5'

class Settings:
    """Main settings object"""
    def __init__(self):
        self.db = DatabaseConfig()
        self.redis = RedisConfig()
        self.weather = WeatherAPIConfig()
        self.data_dir = os.getenv('DATA_DIR', './data')

settings = Settings()