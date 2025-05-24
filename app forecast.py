import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pmdarima import auto_arima

st.set_page_config(page_title="7-Day AQI Forecast", layout="centered")
st.title("📈 7-Day AQI Forecast by City")

# Load your historical AQI CSV (must contain 'Date', 'City', 'AQI_Value')
df = pd.read_csv("cleaned_aqi_india_data.csv")
df['Last_Update'] = pd.to_datetime(df['Last_Update'], errors='coerce')
df = df.dropna(subset=['Last_Update', 'AQI_Value', 'City'])

# Select city
city = st.selectbox("Choose a city", sorted(df['City'].dropna().unique()))

# Filter data for selected city
city_df = df[df['City'] == city].sort_values('Last_Update')

# Show current AQI trend
st.subheader(f"Historical AQI Trend – {city}")
st.line_chart(city_df.set_index('Last_Update')['AQI_Value'])

# Forecasting
st.subheader("Predicted AQI for Next 7 Days")

if len(city_df) >= 30:
    # Prepare time series
    ts = city_df.set_index('Last_Update')['AQI_Value'].resample('D').mean().dropna()

    # Fit ARIMA model
    model = auto_arima(ts, seasonal=False, suppress_warnings=True)
    forecast = model.predict(n_periods=7)

    # Create forecast dataframe
    future_dates = pd.date_range(ts.index[-1] + pd.Timedelta(days=1), periods=7)
    forecast_df = pd.DataFrame({'Date': future_dates, 'Predicted_AQI': forecast})

    # Display plot
    fig, ax = plt.subplots()
    ts.plot(ax=ax, label='Historical AQI')
    forecast_df.set_index('Date').plot(ax=ax, label='Forecast AQI', linestyle='--')
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('AQI')
    plt.title(f"AQI Forecast for {city}")
    st.pyplot(fig)

    # Show forecast table
    st.dataframe(forecast_df.set_index('Date'))
else:
    st.warning("Not enough historical data to make a forecast. At least 30 days of data required.")
