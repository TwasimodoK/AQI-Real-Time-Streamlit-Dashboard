# 🌫️ Real-Time AQI Dashboard using Streamlit

This is a real-time, interactive dashboard built with **Streamlit** that fetches and displays **Air Quality Index (AQI)** data for major Indian cities using the **AQICN API**. It provides not only the AQI value but also its severity category (e.g., Moderate, Poor) and a live **Plotly gauge-style visualization**.

---

## 🧰 Features

✅ Real-time AQI data fetch using the AQICN API  
✅ City selector (Delhi, Mumbai, Chennai, etc.)  
✅ AQI color-coded by severity:  
- Green = Good  
- Yellow = Satisfactory  
- Orange = Moderate  
- Red = Poor  
- Purple = Very Poor  
- Maroon = Severe  

✅ Dominant pollutant and last updated time  
✅ Live **AQI Gauge Visualization** using Plotly  
✅ Simple UI with Streamlit

---

## 🏗️ Tech Stack

- **Python**
- **Streamlit** – interactive web UI
- **Requests** – to fetch API data
- **Plotly** – for gauge chart visualization

---

## 🔑 API Token

Data is fetched from the [AQICN API](https://aqicn.org/data-platform/token/).  
We’ve included a default API token in `app.py`, but you can use your own:

1. Get a free API token from: [https://aqicn.org/data-platform/token/](https://aqicn.org/data-platform/token/)
2. Replace the `API_KEY` in the Python script:
```python
API_KEY = "2e7eb280bf0879f9214dc0a552335579e56a841c"

