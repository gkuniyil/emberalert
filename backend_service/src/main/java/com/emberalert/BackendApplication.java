package com.emberalert;  // File location: com/emberalert folder

import org.springframework.boot.SpringApplication;  // Starts the app
import org.springframework.boot.autoconfigure.SpringBootApplication;  // Enables auto-config

@SpringBootApplication  // Auto-config + component scan
public class BackendApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(BackendApplication.class, args);  // Launch Spring Boot
        
        System.out.println("""
            ╔══════════════════════════════════════════════╗
            ║     EmberAlert Backend Service               ║
            ║     http://localhost:8080                    ║
            ╚══════════════════════════════════════════════╝
            """);  // Startup banner
    }
}