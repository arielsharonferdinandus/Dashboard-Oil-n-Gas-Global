import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Energy Consumption & Production",
    layout="wide"
)

st.title("⚡ Energy Consumption & Production")
st.caption("Country-Level Oil & Gas Data – Aggregated Analysis")

DATA_DIR = Path("data/csv")

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_consumption():
    oil = pd.read_csv(DATA_DIR / "country_consumtion_oil.csv")
    gas = pd.read_csv(DATA_DIR / "country_consumtion_gas.csv")
    oil["Type"] = "Oil"
    gas["Type"] = "Gas"
    df = pd.concat([oil, gas], ignore_index=True)
    return df


@st.cache_data
def load_production():
    oil = pd.read_csv(DATA_DIR / "country_production_oil.csv")
    gas = pd.read_csv(DATA_DIR / "country_production_gas.csv")
    oil["Type"] = "Oil"
    gas["Type"] = "Gas"
    df = pd.concat([oil, gas], ignore_index=True)
    return df


cons_df = load_consumption()
prod_df = load_production()

# =============================
# SELECTORS
# =============================
st.subheader("Data Filters")

col1, col2, col3 = st.columns(3)

with col1:
    selected_type = st.selectbox(
        "Energy Type",
        ["Oil", "Gas"]
    )

with col2:
    selected_country = st.selectbox(
        "Country",
        sorted(cons_df["Country"].unique())
    )

with col3:
    selected_metric = st.selectbox(
        "View Mode",
        ["Yearly Trend", "Latest Snapshot"]
    )

# =============================
# FILTER DATA
# =============================
cons_filtered = cons_df[
    (cons_df["Type"] == selected_type) &
    (cons_df["Country"] == selected_country)
]

prod_filtered = prod_df[
    (prod_df["Type"] == selected_type) &
    (prod_df["Country"] == selected_country)
]

# =============================
# VISUALIZATION
# =============================
if selected_metric == "Yearly Trend":
    st.subheader(f"{selected_country} – {selected_type} Consumption vs Production")

    fig = px.line(
        pd.merge(
            cons_filtered[["Year", "Consumtion"]],
            prod_filtered[["Year", "Production"]],
            on="Year",
            how="outer"
        ),
        x="Year",
        y=["Consumtion", "Production"],
        labels={
            "value": "Volume",
            "variable": "Metric"
        },
        height=420
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.subheader(f"{selected_country} – Latest {selected_type} Snapshot")

    latest_cons = cons_filtered.sort_values("Year").iloc[-1]
    latest_prod = prod_filtered.sort_values("Year").iloc[-1]

    snapshot = pd.DataFrame({
        "Metric": [
            "Latest Year",
            "Consumption",
            "Production",
            "Unit",
            "Source"
        ],
        "Value": [
            latest_cons["Year"],
            round(latest_cons["Consumtion"], 2),
            round(latest_prod["Production"], 2),
            latest_cons["Unit"],
            latest_cons["Source"]
        ]
    )

    st.dataframe(snapshot, use_container_width=True, hide_index=True)

# =============================
# GLOBAL MAP (DUMMY)
# =============================
st.subheader("🗺️ Global Energy Production Map (Dummy)")

dummy_map = pd.DataFrame({
    "Country": ["United States", "Saudi Arabia", "Russia", "China", "India", "Indonesia"],
    "iso3": ["USA", "SAU", "RUS", "CHN", "IND", "IDN"],
    "Production": [18.5, 12.1, 10.8, 4.2, 0.8, 0.7]
})

fig = px.choropleth(
    dummy_map,
    locations="iso3",
    color="Production",
    hover_name="Country",
    projection="natural earth",
    color_continuous_scale="Blues",
    height=420
)

st.plotly_chart(fig, use_container_width=True)

# =============================
# BACK BUTTON
# =============================
if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")

st.caption("Energy Consumption & Production – Dataset-based Analysis")
