# 🔥 EmberAlert

EmberAlert is a full-stack wildfire risk prediction system built with a microservices architecture. Given a geographic location and weather conditions, EmberAlert predicts wildfire risk using a trained XGBoost model exposed through a Flask API. The project also includes a React dashboard for interacting with the model in real time and visualizing prediction results.

---

## Features

- Predict wildfire risk from:
  - latitude
  - longitude
  - temperature
  - humidity
  - wind speed
- Return:
  - risk score
  - risk level
  - contributing factor breakdown
  - cache status
- Redis-based caching for repeated requests
- React frontend dashboard for live interaction
- Dockerized local development workflow
- CI/CD pipeline with GitHub Actions and Trivy scanning

---

## Architecture

```text
┌─────────────────────┐        ┌──────────────────────┐
│   Frontend          │        │    ML Service        │
│   React + Vite      │──────▶│    Flask + XGBoost   │
│   Port 5173         │        │    Port 5000 in ctr  │
└─────────────────────┘        └──────────┬───────────┘
                                          │
                               ┌──────────┴───────────┐
                               │      Redis Cache     │
                               │      PostgreSQL      │
                               └──────────────────────┘