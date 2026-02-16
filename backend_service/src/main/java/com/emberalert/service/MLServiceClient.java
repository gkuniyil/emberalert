package com.emberalert.service;

import com.emberalert.model.RiskRequest;
import com.emberalert.model.RiskResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
public class MLServiceClient {
    
    private final WebClient webClient;
    
    public MLServiceClient(@Value("${ml.service.url}") String mlServiceUrl) {
        this.webClient = WebClient.builder()
                .baseUrl(mlServiceUrl)
                .build();
        System.out.println("ML Service client created for URL: " + mlServiceUrl);
    }
    
    public RiskResponse getPrediction(RiskRequest request) {
        System.out.println("Calling ML service for (" + request.getLatitude() + ", " + request.getLongitude() + ")");
        
        try {
            RiskResponse response = webClient.post()
                    .uri("/api/v1/predict")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(RiskResponse.class)
                    .block();
            
            if (response != null) {
                System.out.println("Received: risk=" + response.getRiskScore() + ", level=" + response.getRiskLevel());
            }
            
            return response;
            
        } catch (Exception e) {
            System.err.println("ML service failed: " + e.getMessage());
            throw new RuntimeException("Prediction service unavailable", e);
        }
    }
}
