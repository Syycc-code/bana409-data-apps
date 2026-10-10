from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="California Housing", page_icon="🏠", layout="wide")
st.title("California Housing Data (1990) by Sun Chengyu")
df = pd.read_csv(Path(__file__).with_name("housing.csv"))
price_filter = st.slider("Minimal Median House Value", 0, 500001, 200000)
st.subheader("See more filters in the sidebar:")
location_options = df["ocean_proximity"].unique().tolist()
location_filter = st.sidebar.multiselect("Choose the location type", location_options, default=location_options)
income_level = st.sidebar.radio("Choose income level", ["Low", "Medium", "High"])

df = df[(df["median_house_value"] >= price_filter) & df["ocean_proximity"].isin(location_filter)]
if income_level == "Low":
    df = df[df["median_income"] <= 2.5]
elif income_level == "Medium":
    df = df[(df["median_income"] > 2.5) & (df["median_income"] < 4.5)]
else:
    df = df[df["median_income"] >= 4.5]

st.caption(f"{len(df):,} districts match your filters. Income is measured in tens of thousands of US dollars.")
if df.empty:
    st.info("No districts match these filters. Lower the price threshold or change the sidebar filters.")
else:
    st.map(df[["latitude", "longitude"]].dropna())
st.subheader("Median House Value Distribution")
if not df.empty:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df["median_house_value"], bins=30, color="#3478b8", edgecolor="white")
    ax.set_xlabel("Median house value (USD)")
    ax.set_ylabel("Number of districts")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
