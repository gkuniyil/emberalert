"""
Pydantic models for request/response validation.

PYDANTIC:
- Automatic validation
- Type checking at runtime
- Clear error messages
- Auto-generated documentation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class PredictionRequest(BaseModel):
    """
    Single prediction request.
    
    VALIDATION:
    - Ensures all required fields present
    - Checks value ranges
    - Type conversion
    """
    
    latitude: float = Field(
        ...,  # ... means required
        ge=-90,  # Greater than or equal to -90
        le=90,   # Less than or equal to 90
        description="Latitude coordinate"
    )
    
    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude coordinate"
    )
    
    temperature: float = Field(
        ...,
        ge=-50,
        le=150,
        description="Temperature in Fahrenheit"
    )
    
    humidity: float = Field(
        ...,
        ge=0,
        le=100,
        description="Relative humidity percentage"
    )
    
    wind_speed: float = Field(
        ...,
        ge=0,
        le=200,
        description="Wind speed in mph"
    )
    
    wind_direction: Optional[float] = Field(
        0,
        ge=0,
        le=360,
        description="Wind direction in degrees"
    )
    
    pressure: Optional[float] = Field(
        1013,
        ge=900,
        le=1100,
        description="Atmospheric pressure in hPa"
    )
    
    @validator('temperature')
    def validate_temperature(cls, v):
        """
        Custom validation for temperature.
        
        WHY: Add business logic beyond simple ranges
        """
        if v < -50 or v > 150:
            raise ValueError('Temperature out of realistic range')
        return v
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "latitude": 34.05,
                "longitude": -118.25,
                "temperature": 95.0,
                "humidity": 25.0,
                "wind_speed": 20.0,
                "wind_direction": 180.0,
                "pressure": 1010.0
            }
        }


class BatchPredictionRequest(BaseModel):
    """Multiple predictions in one request"""
    
    predictions: List[PredictionRequest] = Field(
        ...,
        max_length=100,  # Limit batch size
        description="List of prediction requests"
    )


class PredictionResponse(BaseModel):
    """Single prediction response"""
    
    latitude: float
    longitude: float
    risk_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Fire risk score (0-1)"
    )
    risk_level: str = Field(
        ...,
        description="Risk category: LOW, MODERATE, HIGH, EXTREME"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Prediction timestamp"
    )
    model_version: str
    
    # Additional metadata
    contributing_factors: Optional[dict] = None
    confidence: Optional[float] = None


class BatchPredictionResponse(BaseModel):
    """Batch prediction response"""
    
    predictions: List[PredictionResponse]
    total: int
    model_version: str
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    model_loaded: bool
    cache_connected: bool
    version: str