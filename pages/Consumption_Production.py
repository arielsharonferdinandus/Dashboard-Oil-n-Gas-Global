import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Energy Consumption & Production – Detail View",
    layout="wide"
)

st.title("⚡ Energy Consumption & Production – Detail View")
st.caption("Country-Level Oil & Gas Data (Dataset-based)")

DATA_DIR = Path("data/csv")

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_energy_data():
    # Consumption
    cons_oil = pd.read_csv(DATA_DIR / "country_consumtion_oil.csv")
    cons_gas = pd.read_csv(DATA_DIR / "country_consumtion_gas.csv")

    cons_oil["Type"] = "Oil"
    cons_gas["Type"] = "Gas"

    cons = pd.concat([cons_oil, cons_gas], ignore_index=True)

    # Production
    prod_oil = pd.read_csv(DATA_DIR / "country_production_oil.csv")
    prod_gas = pd.read_csv(DATA_DIR / "country_production_gas.csv")

    prod_oil["Type"] = "Oil"
    prod_gas["Type"] = "Gas"

    prod = pd.concat([prod_oil, prod_gas], ignore_index=True)

    return cons, prod


cons_df, prod_df = load_energy_data()

# =============================
# SELECTORS
# =============================
st.subheader("Energy Data Explorer")

col1, col2, col3 = st.columns(3)

with col1:
    selected_type = st.selectbox(
        "Energy Type",
        sorted(cons_df["Type"].unique())
    )

with col2:
    selected_country = st.selectbox(
        "Country",
        sorted(cons_df["Country"].dropna().unique())
    )

with col3:
    view_mode = st.selectbox(
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

merged_df = pd.merge(
    cons_filtered[["Year", "Consumtion"]],
    prod_filtered[["Year", "Production"]],
    on="Year",
    how="outer"
).sort_values("Year")

# =============================
# YEARLY TREND
# =============================
if view_mode == "Yearly Trend":
    st.subheader(f"{selected_country} – {selected_type} Consumption vs Production")

    fig = px.line(
        merged_df,
        x="Year",
        y=["Consumtion", "Production"],
        labels={
            "value": "Volume",
            "variable": "Metric"
        },
        height=420
    )

    fig.update_traces(opacity=0.45)
    fig.update_layout(hovermode="x unified")

    st.plotly_chart(fig, use_container_width=True)

# =============================
# LATEST SNAPSHOT
# =============================
else:
    st.subheader(f"{selected_country} – Latest {selected_type} Snapshot")

    latest_row = merged_df.dropna().iloc[-1]

    snapshot = pd.DataFrame({
        "Metric": [
            "Year",
            "Consumption",
            "Production",
            "Energy Type",
            "Country"
        ],
        "Value": [
            int(latest_row["Year"]),
            round(latest_row["Consumtion"], 2),
            round(latest_row["Production"], 2),
            selected_type,
            selected_country
        ]
    })

    st.dataframe(snapshot, use_container_width=True, hide_index=True)

# =============================
# BACK BUTTON
# =============================
if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")

st.caption("Energy Consumption & Production – Detail View")
