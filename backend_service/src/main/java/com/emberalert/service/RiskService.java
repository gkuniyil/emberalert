package com.emberalert.service;

import com.emberalert.model.RiskRequest;
import com.emberalert.model.RiskResponse;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

@Service
public class RiskService {
    
    private final MLServiceClient mlServiceClient;
    
    public RiskService(MLServiceClient mlServiceClient) {
        this.mlServiceClient = mlServiceClient;
    }
    
    @Cacheable(value = "predictions", key = "#request.latitude + '-' + #request.longitude")
    public RiskResponse assessRisk(RiskRequest request) {
        System.out.println("Assessing risk for location (" + request.getLatitude() + ", " + request.getLongitude() + ")");
        
        RiskResponse response = mlServiceClient.getPrediction(request);
        
        if (response != null && "EXTREME".equals(response.getRiskLevel())) {
            System.out.println("WARNING: EXTREME risk detected at (" + request.getLatitude() + ", " + request.getLongitude() + ")");
        }
        
        return response;
    }
}
