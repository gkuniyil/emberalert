# 🔥 EmberAlert

A production-ready wildfire risk prediction system built with a microservices architecture. Given a geographic location, EmberAlert predicts fire risk using a trained XGBoost machine learning model, exposed through a REST API backend.

---

## Architecture

```
┌─────────────────────┐        ┌──────────────────────┐
│   API / Backend     │        │    ML Service         │
│   Spring Boot       │──────▶│    Flask + XGBoost    │
│   Java 17           │        │    Python 3.11        │
└────────┬────────────┘        └──────────────────────┘
         │
    ┌────┴────────┐
    │  PostgreSQL │   Redis (caching)
    └─────────────┘
```

- **Backend Service** — Spring Boot REST API (Java 17). Handles requests, business logic, and data persistence with PostgreSQL. Uses Redis for caching.
- **ML Service** — Flask microservice (Python 3.11) that serves a trained XGBoost model to predict wildfire risk for a given location.
- **CI/CD** — GitHub Actions pipeline with automated testing, Docker image builds, and security scanning via Trivy.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Spring Boot 3, Java 17 |
| ML Service | Flask, XGBoost, scikit-learn |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Security Scanning | Trivy |

---

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Java 17 (for local backend development)
- Python 3.11 (for local ML service development)

### Run with Docker Compose

```bash
git clone https://github.com/gkuniyil/emberalert.git
cd emberalert_official
docker compose -f docker/docker-compose.yml up --build
```

The backend API will be available at `http://localhost:8080` and the ML service at `http://localhost:5000`.

### Run Locally (without Docker)

**Backend:**
```bash
cd backend_service
./mvnw spring-boot:run
```

**ML Service:**
```bash
cd ml_service
pip install -r requirements.txt
python app.py
```

---

## API Endpoints

### Wildfire Risk Prediction

```
POST /api/v1/risk/predict
```

**Request:**
```json
{
  "latitude": 34.05,
  "longitude": -118.24,
  "temperature": 38.5,
  "humidity": 12.0,
  "windSpeed": 25.0
}
```

**Response:**
```json
{
  "riskScore": 0.87,
  "riskLevel": "HIGH",
  "location": {
    "latitude": 34.05,
    "longitude": -118.24
  }
}
```

---

## ML Model

The ML service uses an **XGBoost gradient boosting classifier** trained on historical wildfire and weather data. The model (`fire_risk_xgboost_v1.pkl`) takes environmental features as input and outputs a risk score between 0 and 1.

**Key features used:**
- Temperature
- Relative humidity
- Wind speed
- Geographic coordinates

---

## CI/CD Pipeline

Every push to `main` or `develop` triggers the full pipeline:

1. **Test Spring Boot Backend** — builds with Maven, runs unit tests against a live PostgreSQL and Redis service container
2. **Test ML Service** — installs Python dependencies, runs pytest
3. **Build Docker Images** — builds both `Dockerfile.flask` and `Dockerfile.spring` to verify containerization
4. **Security Scan** — Trivy scans the full repository for vulnerabilities and uploads results to GitHub Security tab

---

## Project Structure

```
emberalert_official/
├── backend_service/         # Spring Boot API
│   ├── src/
│   ├── pom.xml
│   └── mvnw
├── ml_service/              # Flask ML microservice
│   ├── app.py
│   ├── requirements.txt
│   └── saved_models/
├── docker/                  # Dockerfiles and Compose
│   ├── Dockerfile.flask
│   ├── Dockerfile.spring
│   └── docker-compose.yml
└── .github/workflows/
    └── ci.yml
```

---

## Running Tests

**Backend:**
```bash
cd backend_service
./mvnw test
```

**ML Service:**
```bash
cd ml_service
python -m pytest tests/ -v
```

---

