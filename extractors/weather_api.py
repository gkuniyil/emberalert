"""
Weather data extraction from OpenWeatherMap API.
Handles API calls, rate limiting, and error handling.
"""

import requests
import time
from typing import Dict, Optional
from datetime import datetime
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class WeatherExtractor:
    """Fetch weather data from OpenWeatherMap"""
    
    def __init__(self):
        self.api_key = settings.weather.api_key
        self.base_url = settings.weather.base_url
        self.last_call = 0
        self.min_interval = 1.0  # 1 second between calls
    
    def _rate_limit(self):
        """Simple rate limiting"""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()
    
    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch current weather for location.
        
        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
        
        Returns:
            Dict with weather data or None on error
        """
        self._rate_limit()
        
        url = f"{self.base_url}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'imperial'  # Fahrenheit
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raise error for 4xx/5xx
            
            data = response.json()
            
            # Transform API response to our format
            return {
                'latitude': lat,
                'longitude': lon,
                'timestamp': datetime.fromtimestamp(data['dt']),
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'conditions': data['weather'][0]['main'],
                'pressure': data['main']['pressure']
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error for ({lat}, {lon}): {e}")
            return None
    
    def save_to_db(self, weather_data: Dict):
        """Save weather data to PostgreSQL"""
        from database.connection import db
        
        query = """
        INSERT INTO weather_data 
        (latitude, longitude, timestamp, temperature, humidity, 
         wind_speed, wind_direction, conditions, pressure)
        VALUES 
        (:latitude, :longitude, :timestamp, :temperature, :humidity,
         :wind_speed, :wind_direction, :conditions, :pressure)
        """
        
        db.execute_query(query, weather_data)
        logger.info(f"Saved weather data for ({weather_data['latitude']}, {weather_data['longitude']})")