import streamlit as st
import requests
import plotly.graph_objects as go

# API Key
API_KEY = "2e7eb280bf0879f9214dc0a552335579e56a841c"

# Supported Cities
cities = ["delhi", "mumbai", "kolkata", "chennai", "lucknow", "bangalore", "hyderabad", "ahmedabad"]

# Streamlit page config
st.set_page_config(page_title="Real-Time AQI Dashboard", layout="centered")
st.title("🌫️ Real-Time AQI Dashboard")

# City selector
city = st.selectbox("Choose a City", cities)

# Function to fetch AQI data
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

# Determine AQI category and color
def aqi_category(aqi):
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

# Button to fetch data
if st.button("Fetch Latest AQI"):
    aqi_data = get_aqi_data(city)
    if aqi_data:
        aqi_value = aqi_data["AQI"]
        category, color = aqi_category(aqi_value)

        st.success("✅ Data Fetched Successfully!")
        st.metric("City", aqi_data["City"])
        st.metric("AQI Value", aqi_value)
        st.metric("Dominant Pollutant", aqi_data["Dominant Pollutant"])
        st.write("Last Updated:", aqi_data["Time"])

        st.markdown(f"### AQI Category: :{color}[{category}]")

        # Plotly gauge-style bar
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=aqi_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"AQI Status: {category}"},
            gauge={
                'axis': {'range': [0, 500]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 50], 'color': 'green'},
                    {'range': [51, 100], 'color': 'yellow'},
                    {'range': [101, 200], 'color': 'orange'},
                    {'range': [201, 300], 'color': 'red'},
                    {'range': [301, 400], 'color': 'purple'},
                    {'range': [401, 500], 'color': 'maroon'}
                ],
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("❌ Failed to fetch data. Please try again.")

