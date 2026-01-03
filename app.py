import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Global Energy Dashboard",
    layout="wide"
)

st.title("🌍 Global Energy Dashboard")
st.caption("Oil, Gas & Energy Visualization – Prototype")

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_price_data():
    df = pd.read_csv("data/csv/price_timeseries.csv")
    df["period"] = pd.to_datetime(df["period"])
    df = df[df["benchmark"] == "Brent"]
    df = df.sort_values("period").tail(90)
    return df


@st.cache_data
def load_production_oil():
    df = pd.read_csv("data/csv/country_production_oil.csv")
    df = (
        df.groupby("Year", as_index=False)["Production"]
        .sum()
        .sort_values("Year")
    )
    return df


@st.cache_data
def load_consumption_oil():
    df = pd.read_csv("data/csv/country_consumtion_oil.csv")
    df = (
        df.groupby("Year", as_index=False)["Consumtion"]
        .sum()
        .sort_values("Year")
    )
    return df


# =============================
# DUMMY MAP DATA
# =============================
migas_map = pd.DataFrame({
    "Country": ["United States", "Saudi Arabia", "Russia", "China", "India", "Indonesia"],
    "iso3": ["USA", "SAU", "RUS", "CHN", "IND", "IDN"],
    "Production": [18.5, 12.1, 10.8, 4.2, 0.8, 0.7]
})

# =============================
# LOAD ALL
# =============================
price_df = load_price_data()
prod_oil_df = load_production_oil()
cons_oil_df = load_consumption_oil()

# =============================
# LAYOUT ROW 1 (3 COLUMNS)
# =============================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🛢️ Brent Oil Price (Spot)")
    fig = px.line(
        price_df,
        x="period",
        y="value",
        labels={"value": "USD / Barrel", "period": "Date"},
        height=260
    )
    st.plotly_chart(fig, use_container_width=True)


with col2:
    st.subheader("🏭 Global Oil Production")
    fig = px.line(
        prod_oil_df,
        x="Year",
        y="Production",
        labels={"Production": "Total Production"},
        height=260
    )
    st.plotly_chart(fig, use_container_width=True)


with col3:
    st.subheader("⛽ Global Oil Consumption")
    fig = px.line(
        cons_oil_df,
        x="Year",
        y="Consumtion",
        labels={"Consumtion": "Total Consumption"},
        height=260
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================
# LAYOUT ROW 2 (MAP FULL WIDTH)
# =============================
st.subheader("🗺️ Global Energy Production Map (Dummy Data)")

fig = px.choropleth(
    migas_map,
    locations="iso3",
    color="Production",
    hover_name="Country",
    projection="natural earth",
    color_continuous_scale="YlOrRd",
    height=420
)

st.plotly_chart(fig, use_container_width=True)

# =============================
# FOOTER
# =============================
st.caption("Streamlit Energy Dashboard – Dataset-based Prototype")
