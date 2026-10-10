from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="World Cities", page_icon="🌍", layout="wide")
st.title("World Cities")
st.caption("Explore cities with more than one million residents.")

df = pd.read_csv(Path(__file__).with_name("worldcities.csv"))
# A readable option makes cities with missing capital labels selectable.
df["capital"] = df["capital"].fillna("Not a capital")
population_filter = st.slider("Minimal Population (Millions):", 0.0, 40.0, 3.6)
capital_options = df["capital"].unique().tolist()
capital_filter = st.sidebar.multiselect("Capital Selector", capital_options, default=capital_options)
with st.sidebar.form("country_form"):
    country_filter = st.text_input("Country Name (enter ALL to reset)", "ALL")
    st.form_submit_button("Apply")

df = df[(df["population"] >= population_filter) & df["capital"].isin(capital_filter)]
country_filter = country_filter.strip()
if country_filter.upper() != "ALL":
    df = df[df["country"].str.casefold() == country_filter.casefold()]

st.caption(f"{len(df):,} cities match your filters.")
if df.empty:
    st.info("No cities match these filters. Lower the population threshold or change the sidebar filters.")
else:
    st.map(df[["lat", "lon"]].dropna())
st.subheader("City Details:")
st.dataframe(df[["city", "country", "population"]], hide_index=True, width="stretch")
st.subheader("Total Population By Country")
if not df.empty:
    fig, ax = plt.subplots(figsize=(16, 5))
    df.groupby("country")["population"].sum().sort_values(ascending=False).plot.bar(ax=ax)
    ax.set_xlabel("Country")
    ax.set_ylabel("Population (millions)")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
