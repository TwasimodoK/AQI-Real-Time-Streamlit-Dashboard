import streamlit as st
import requests

API_KEY = "2e7eb280bf0879f9214dc0a552335579e56a841c"
cities = ["delhi", "mumbai", "kolkata", "chennai", "lucknow", "bangalore", "hyderabad", "ahmedabad","pune"]

st.set_page_config(page_title="Real-Time AQI Dashboard", layout="centered")
st.title("🌫️ Real-Time AQI Dashboard")

city = st.selectbox("Choose a City", cities)

def get_aqi_data(city):
    url = f"https://api.waqi.info/feed/{city}/?token={API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "ok":
        return {
            "City": city.capitalize(),
            "AQI": data["data"]["aqi"],
            "Time": data["data"]["time"]["s"],
            "Dominant Pollutant": data["data"]["dominentpol"]
        }
    else:
        return None

if st.button("Fetch Latest AQI"):
    aqi_data = get_aqi_data(city)
    if aqi_data:
        st.success("✅ Data Fetched Successfully!")
        st.metric("City", aqi_data["City"])
        st.metric("AQI", aqi_data["AQI"])
        st.metric("Dominant Pollutant", aqi_data["Dominant Pollutant"])
        st.write("Last Updated:", aqi_data["Time"])
    else:
        st.error("❌ Failed to fetch data. Try again later.")
