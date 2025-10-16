# app.py
import os
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import plotly.graph_objects as go

st.set_page_config(page_title="Real-Time AQI Dashboard", layout="centered")
st.title("🌫️ Real-Time AQI Dashboard")

# API token via Streamlit secrets or env var
API_KEY = None
if "AQICN_TOKEN" in st.secrets:
    API_KEY = st.secrets["AQICN_TOKEN"]
else:
    API_KEY = os.environ.get("AQICN_TOKEN")

if not API_KEY:
    st.error(
        "API token not found. Set 'AQICN_TOKEN' in Streamlit Cloud Secrets or as environment variable."
    )
    st.stop()

cities = ["delhi", "mumbai", "kolkata", "chennai",
          "lucknow", "bangalore", "hyderabad",
          "ahmedabad", "pune"]

city = st.selectbox("Choose a City", cities)

def get_aqi_data(city, token):
    try:
        url = f"https://api.waqi.info/feed/{city}/?token={token}"
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Network/API error: {e}"}
    except ValueError:
        return {"error": "Invalid JSON response from API."}

    if data.get("status") != "ok" or "data" not in data:
        msg = data.get("data") or data.get("status") or "Unknown API error"
        return {"error": f"API returned error: {msg}"}

    d = data["data"]
    return {
        "City": city.capitalize(),
        "AQI": d.get("aqi"),
        "Time": d.get("time", {}).get("s"),
        "Dominant Pollutant": d.get("dominentpol"),
        "raw": d
    }

def aqi_category(aqi):
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

# Section: Live fetch
st.header("Live AQI Data")
if st.button("Fetch Latest AQI"):
    with st.spinner("Fetching latest AQI..."):
        res = get_aqi_data(city, API_KEY)

    if "error" in res:
        st.error(res["error"])
    else:
        aqi_value = res["AQI"]
        category, color = aqi_category(aqi_value)

        st.metric("City", res["City"])
        st.metric("AQI Value", aqi_value if aqi_value is not None else "N/A")
        st.metric("Dominant Pollutant", res.get("Dominant Pollutant", "N/A"))
        st.write("Last Updated:", res.get("Time", "N/A"))
        st.markdown(f"### AQI Category: <span style='color:{color}'>{category}</span>", unsafe_allow_html=True)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=aqi_value if aqi_value is not None else 0,
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

        with st.expander("Raw API response (debug)"):
            st.json(res.get("raw", {}))

# Section: 7-day forecast using historical CSV (if available)
st.header("7-Day AQI Forecast (Historical data required)")
st.markdown("Upload a historical CSV (columns: City, Last_Update, AQI_Value) or skip if not available.")

uploaded = st.file_uploader("Upload cleaned_aqi_india_data.csv (optional)", type=["csv"])
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        df['Last_Update'] = pd.to_datetime(df['Last_Update'], errors='coerce')
        df = df.dropna(subset=['Last_Update','AQI_Value','City'])
        st.success("Historical data loaded.")
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        df = None
else:
    df = None

if df is not None:
    city_df = df[df['City'].str.lower() == city.lower()].sort_values('Last_Update')
    if len(city_df) < 30:
        st.warning("Not enough historical daily data for forecasting (need ~30+ days).")
    else:
        # daily resample
        ts = city_df.set_index('Last_Update')['AQI_Value'].resample('D').mean().dropna()
        if len(ts) < 30:
            st.warning("After resampling to daily mean, insufficient data for forecasting.")
        else:
            try:
                model = ARIMA(ts, order=(1,1,1))
                model_fit = model.fit()
                forecast = model_fit.forecast(steps=7)
            except Exception as e:
                st.error(f"ARIMA model error: {e}")
                forecast = None

            if forecast is not None:
                future_dates = pd.date_range(start=ts.index[-1] + pd.Timedelta(days=1), periods=7)
                forecast_df = pd.DataFrame({'Date': future_dates, 'Predicted_AQI': forecast})
                fig2, ax = plt.subplots()
                ts.plot(ax=ax, label='Historical AQI')
                forecast_df.set_index('Date').plot(ax=ax, label='7-day Forecast', linestyle='--', color='red')
                ax.legend()
                ax.set_xlabel("Date")
                ax.set_ylabel("AQI")
                st.pyplot(fig2)
                st.dataframe(forecast_df.set_index('Date'))
else:
    st.info("Upload historical data to enable 7-day forecasting.")


