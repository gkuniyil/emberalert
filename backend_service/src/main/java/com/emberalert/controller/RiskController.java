package com.emberalert.controller;

import com.emberalert.model.RiskRequest;
import com.emberalert.model.RiskResponse;
import com.emberalert.service.RiskService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/risk")
@CrossOrigin(origins = "*")
public class RiskController {
    
    private final RiskService riskService;
    
    public RiskController(RiskService riskService) {
        this.riskService = riskService;
    }
    
    @PostMapping("/predict")
    public ResponseEntity<RiskResponse> predictRisk(@Valid @RequestBody RiskRequest request) {
        System.out.println("Received prediction request for (" + request.getLatitude() + ", " + request.getLongitude() + ")");
        
        RiskResponse response = riskService.assessRisk(request);
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/location")
    public ResponseEntity<RiskResponse> getRiskByLocation(
            @RequestParam Double lat,
            @RequestParam Double lon,
            @RequestParam(defaultValue = "75") Double temp,
            @RequestParam(defaultValue = "50") Double humidity,
            @RequestParam(defaultValue = "10") Double windSpeed) {
        
        RiskRequest request = new RiskRequest();
        request.setLatitude(lat);
        request.setLongitude(lon);
        request.setTemperature(temp);
        request.setHumidity(humidity);
        request.setWindSpeed(windSpeed);
        
        RiskResponse response = riskService.assessRisk(request);
        return ResponseEntity.ok(response);
    }
}
