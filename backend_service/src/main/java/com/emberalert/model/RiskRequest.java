package com.emberalert.model;

import jakarta.validation.constraints.*;

public class RiskRequest {
    
    @NotNull(message = "Latitude is required")
    @Min(value = -90, message = "Latitude must be >= -90")
    @Max(value = 90, message = "Latitude must be <= 90")
    private Double latitude;
    
    @NotNull(message = "Longitude is required")
    @Min(value = -180, message = "Longitude must be >= -180")
    @Max(value = 180, message = "Longitude must be <= 180")
    private Double longitude;
    
    @NotNull(message = "Temperature is required")
    private Double temperature;
    
    @NotNull(message = "Humidity is required")
    @Min(value = 0, message = "Humidity must be >= 0")
    @Max(value = 100, message = "Humidity must be <= 100")
    private Double humidity;
    
    @NotNull(message = "Wind speed is required")
    @Min(value = 0, message = "Wind speed must be >= 0")
    private Double windSpeed;
    
    private Double windDirection = 0.0;
    private Double pressure = 1013.0;
    
    // Getters
    public Double getLatitude() { return latitude; }
    public Double getLongitude() { return longitude; }
    public Double getTemperature() { return temperature; }
    public Double getHumidity() { return humidity; }
    public Double getWindSpeed() { return windSpeed; }
    public Double getWindDirection() { return windDirection; }
    public Double getPressure() { return pressure; }
    
    // Setters
    public void setLatitude(Double latitude) { this.latitude = latitude; }
    public void setLongitude(Double longitude) { this.longitude = longitude; }
    public void setTemperature(Double temperature) { this.temperature = temperature; }
    public void setHumidity(Double humidity) { this.humidity = humidity; }
    public void setWindSpeed(Double windSpeed) { this.windSpeed = windSpeed; }
    public void setWindDirection(Double windDirection) { this.windDirection = windDirection; }
    public void setPressure(Double pressure) { this.pressure = pressure; }
}
