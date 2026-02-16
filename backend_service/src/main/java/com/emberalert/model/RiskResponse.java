package com.emberalert.model;

import lombok.Data;
import java.time.LocalDateTime;
import java.util.Map;

@Data
public class RiskResponse {
    
    private Double latitude;
    private Double longitude;
    private Double riskScore;
    private String riskLevel;
    private LocalDateTime timestamp;
    private String modelVersion;
    private Map<String, Double> contributingFactors;
    private Boolean fromCache;
    
    // MANUAL GETTERS 
    public Double getLatitude() { return latitude; }
    public Double getLongitude() { return longitude; }
    public Double getRiskScore() { return riskScore; }
    public String getRiskLevel() { return riskLevel; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public String getModelVersion() { return modelVersion; }
    public Map<String, Double> getContributingFactors() { return contributingFactors; }
    public Boolean getFromCache() { return fromCache; }
}