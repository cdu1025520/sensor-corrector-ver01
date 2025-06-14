
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore
import matplotlib.dates as mdates

st.set_page_config(page_title="Sensor Data Corrector", layout="wide")
st.title("📊 Sensor Data Correction Tool (ver.0.1)")
st.markdown("Upload flowmeter (bulk meter) CSV data to detect and correct outliers.")

# Upload CSV
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, parse_dates=["timestamp"])

    # Outlier detection
    df["zscore"] = zscore(df["sensor_value"], nan_policy='omit')
    df["is_outlier"] = df["zscore"].abs() > 3

    # Correction
    df["corrected_value"] = df["sensor_value"].copy()
    df.loc[df["is_outlier"], "corrected_value"] = np.nan
    df["corrected_value"] = df["corrected_value"].fillna(method="ffill")

    # Visualization
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df["timestamp"], df["sensor_value"], label="Raw Sensor Value", alpha=0.5)
    ax.plot(df["timestamp"], df["corrected_value"], label="Corrected Value", linewidth=2)
    ax.scatter(df.loc[df["is_outlier"], "timestamp"],
               df.loc[df["is_outlier"], "sensor_value"],
               color='red', label='Outlier', zorder=5)
    ax.set_title("Sensor Data Correction")
    ax.set_xlabel("Time")
    ax.set_ylabel("Flow Rate")
    ax.legend()
    ax.grid(True)
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
    st.pyplot(fig)

    # Summary
    st.subheader("📌 Correction Summary")
    st.markdown(f"- Number of outliers: **{df['is_outlier'].sum()}**")
    st.markdown(f"- Missing values (original): **{df['sensor_value'].isna().sum()}**")
    st.markdown(f"- Missing after correction: **{df['corrected_value'].isna().sum()}**")

    # Download corrected data
    csv = df[["timestamp", "sensor_value", "corrected_value"]].to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Corrected CSV", data=csv, file_name="corrected_sensor_data.csv", mime="text/csv")
