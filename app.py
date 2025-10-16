# app.py
import os
import streamlit as st
import requests

# Streamlit setup
st.set_page_config(page_title="Real-Time AQI Dashboard", layout="centered")
st.title("🌫️ Real-Time AQI Dashboard")

# --------------------------------
# 1️⃣ Get API Key (from secrets or env variable)
# --------------------------------
API_KEY = os.environ.get("AQICN_TOKEN", "")
if API_KEY == "":
    st.error("⚠️ API key not found. Please add it to Streamlit Secrets as 'AQICN_TOKEN'.")
    st.stop()

# --------------------------------
# 2️⃣ City Selection
# --------------------------------
cities = [
    "delhi", "mumbai", "kolkata", "chennai",
    "lucknow", "bangalore", "hyderabad",
    "ahmedabad", "pune"
]
city = st.selectbox("Select a City", cities)

# --------------------------------
# 3️⃣ Fetch AQI Function
# --------------------------------
def fetch_aqi(city_name, token):
    """Fetch latest AQI data from AQICN API"""
    url = f"https://api.waqi.info/feed/{city_name}/?token={token}"
    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return {"error": f"Network/API error: {e}"}
    
    if data.get("status") != "ok" or "data" not in data:
        return {"error": f"API error: {data.get('data', 'Invalid response')}"}
    
    d = data["data"]
    return {
        "city": city_name.capitalize(),
        "aqi": d.get("aqi"),
        "dominant": d.get("dominentpol"),
        "time": d.get("time", {}).get("s"),
    }

# --------------------------------
# 4️⃣ AQI Category & Color
# --------------------------------
def classify_aqi(aqi):
    """Return category name and color"""
    try:
        aqi = float(aqi)
    except Exception:
        return "Unknown", "gray"
    if aqi <= 50:
        return "Good", "green"
    elif aqi <= 100:
        return "Satisfactory", "yellow"
    elif aqi <= 200:
        return "Moderate", "orange"
    elif aqi <= 300:
        return "Poor", "red"
    elif aqi <= 400:
        return "Very Poor", "purple"
    else:
        return "Severe", "maroon"

# --------------------------------
# 5️⃣ Main Action - Fetch and Display AQI
# --------------------------------
if st.button("Fetch Latest AQI"):
    with st.spinner("Fetching data..."):
        result = fetch_aqi(city, API_KEY)

    if "error" in result:
        st.error(result["error"])
    else:
        aqi = result["aqi"]
        category, color = classify_aqi(aqi)

        st.metric("City", result["city"])
        st.metric("AQI Value", aqi)
        st.metric("Dominant Pollutant", result["dominant"])
        st.write("Last Updated:", result["time"])
        st.markdown(f"### AQI Category: <span style='color:{color};font-weight:bold'>{category}</span>", unsafe_allow_html=True)


