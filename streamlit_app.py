import streamlit as st
import pandas as pd
import xgboost as xgb
import joblib

# 1. Setup the Page
st.set_page_config(page_title="EmberAlert", page_icon="🔥")
st.title("🔥 EmberAlert: Wildfire Risk Predictor")
st.markdown("Enter weather conditions to calculate the probability of a wildfire.")

# 2. Load the Model (Explain this in interviews!)
@st.cache_resource
def load_model():
    # Update this path to where your .joblib or .json model is
    return joblib.load('models/wildfire_model.joblib')

model = load_model()

# 3. Create the Input Form
with st.sidebar:
    st.header("Weather Parameters")
    temp = st.slider("Temperature (°C)", -10, 50, 25)
    humidity = st.slider("Humidity (%)", 0, 100, 40)
    wind_speed = st.slider("Wind Speed (km/h)", 0, 100, 15)
    precipitation = st.number_input("Precipitation (mm)", 0.0, 50.0, 0.0)

# 4. Run Prediction
if st.button("Calculate Risk"):
    input_data = pd.DataFrame([[temp, humidity, wind_speed, precipitation]], 
                               columns=['temp', 'humidity', 'wind', 'rain'])
    
    prediction = model.predict_proba(input_data)[0][1] # Get probability
    
    # 5. Show Results
    st.metric("Wildfire Probability", f"{prediction*100:.1f}%")
    
    if prediction > 0.7:
        st.error("HIGH RISK: Extreme caution advised.")
    elif prediction > 0.4:
        st.warning("MODERATE RISK: Stay alert.")
    else:
        st.success("LOW RISK: Conditions are stable.")