import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://localhost:5001/api/v1/predict";
const HEALTH_URL = "http://localhost:5001/health";

function getRiskColor(level) {
  switch (level) {
    case "LOW":
      return "#22c55e";
    case "MODERATE":
      return "#eab308";
    case "HIGH":
      return "#f97316";
    case "EXTREME":
      return "#ef4444";
    default:
      return "#94a3b8";
  }
}

export default function App() {
  const [formData, setFormData] = useState({
    latitude: "34.05",
    longitude: "-118.25",
    temperature: "85",
    humidity: "20",
    wind_speed: "10",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [apiStatus, setApiStatus] = useState("checking...");

  useEffect(() => {
    async function checkHealth() {
      try {
        const response = await fetch(HEALTH_URL);
        if (!response.ok) {
          throw new Error("Health check failed");
        }
        setApiStatus("online");
      } catch {
        setApiStatus("offline");
      }
    }

    checkHealth();
  }, []);

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  function handleReset() {
    setFormData({
      latitude: "34.05",
      longitude: "-118.25",
      temperature: "85",
      humidity: "20",
      wind_speed: "10",
    });
    setResult(null);
    setError("");
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const payload = {
        latitude: Number(formData.latitude),
        longitude: Number(formData.longitude),
        temperature: Number(formData.temperature),
        humidity: Number(formData.humidity),
        wind_speed: Number(formData.wind_speed),
      };

      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Prediction request failed");
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  const riskColor = getRiskColor(result?.risk_level);

  return (
    <div className="page">
      <div className="container">
        <header className="hero">
          <h1>EmberAlert</h1>
          <p>
            Wildfire risk prediction dashboard powered by Flask, XGBoost, Redis,
            and Docker.
          </p>
          <p className="status-text">
            API Status:{" "}
            <span
              className={
                apiStatus === "online" ? "status-online" : "status-offline"
              }
            >
              {apiStatus}
            </span>
          </p>
        </header>

        <div className="grid">
          <section className="card">
            <h2>Input Conditions</h2>
            <form onSubmit={handleSubmit} className="form">
              <label>
                Latitude
                <input
                  name="latitude"
                  value={formData.latitude}
                  onChange={handleChange}
                />
              </label>

              <label>
                Longitude
                <input
                  name="longitude"
                  value={formData.longitude}
                  onChange={handleChange}
                />
              </label>

              <label>
                Temperature (F)
                <input
                  name="temperature"
                  value={formData.temperature}
                  onChange={handleChange}
                />
              </label>

              <label>
                Humidity (%)
                <input
                  name="humidity"
                  value={formData.humidity}
                  onChange={handleChange}
                />
              </label>

              <label>
                Wind Speed (mph)
                <input
                  name="wind_speed"
                  value={formData.wind_speed}
                  onChange={handleChange}
                />
              </label>

              <div className="button-row">
                <button type="submit" disabled={loading}>
                  {loading ? "Predicting..." : "Predict Risk"}
                </button>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={handleReset}
                  disabled={loading}
                >
                  Reset
                </button>
              </div>
            </form>
          </section>

          <section className="card">
            <h2>Prediction Result</h2>

            {loading && <div className="loading">Running model prediction...</div>}

            {!result && !error && !loading && (
              <div className="placeholder">
                Submit weather and location data to see wildfire risk.
              </div>
            )}

            {error && <div className="error">{error}</div>}

            {result && (
              <div className="result">
                <div className="risk-header">
                  <div>
                    <p className="muted">Risk Score</p>
                    <h3>{Number(result.risk_score).toFixed(3)}</h3>
                  </div>
                  <span
                    className="badge"
                    style={{ backgroundColor: riskColor }}
                  >
                    {result.risk_level}
                  </span>
                </div>

                <div className="progress-track">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${Math.min(Number(result.risk_score) * 100, 100)}%`,
                      backgroundColor: riskColor,
                    }}
                  />
                </div>

                <div className="meta">
                  <div>
                    <span className="muted">Latitude:</span> {result.latitude}
                  </div>
                  <div>
                    <span className="muted">Longitude:</span> {result.longitude}
                  </div>
                  <div>
                    <span className="muted">Model Version:</span>{" "}
                    {result.model_version}
                  </div>
                  <div>
                    <span className="muted">From Cache:</span>{" "}
                    {result.from_cache ? "Yes" : "No"}
                  </div>
                </div>

                <div className="factors">
                  <h4>Contributing Factors</h4>

                  <FactorBar
                    label="Temperature"
                    value={result.contributing_factors?.temperature_factor ?? 0}
                  />
                  <FactorBar
                    label="Humidity"
                    value={result.contributing_factors?.humidity_factor ?? 0}
                  />
                  <FactorBar
                    label="Wind"
                    value={result.contributing_factors?.wind_factor ?? 0}
                  />
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

function FactorBar({ label, value }) {
  return (
    <div className="factor-row">
      <div className="factor-top">
        <span>{label}</span>
        <span>{Number(value).toFixed(3)}</span>
      </div>
      <div className="factor-track">
        <div
          className="factor-fill"
          style={{ width: `${Math.min(Number(value) * 100, 100)}%` }}
        />
      </div>
    </div>
  );
}