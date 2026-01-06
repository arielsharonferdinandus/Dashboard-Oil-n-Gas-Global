import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
from pathlib import Path

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Global Energy Production – Map Detail",
    layout="wide"
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Global Energy Production – Map Detail")
st.caption("Country-Level Production & Consumption (DuckDB-based)")

DB_PATH = Path("data/db/energy.duckdb")

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_map_detail(db_path=DB_PATH):
    conn = duckdb.connect(database=str(db_path), read_only=True)

    # ---- OIL ----
    oil_prod = conn.execute("""
        SELECT Country, iso3, Year, Production
        FROM oil_prod
    """).df()
    oil_cons = conn.execute("""
        SELECT Country, iso3, Year, Consumtion
        FROM oil_cons
    """).df()

    oil = pd.merge(
        oil_prod, oil_cons,
        on=["Country", "iso3", "Year"],
        how="left"
    )
    oil["Type"] = "Oil"

    # ---- GAS ----
    gas_prod = conn.execute("""
        SELECT country AS Country,
               iso3,
               production_year AS Year,
               production AS Production
        FROM goget
        WHERE commodity = 'Gas'
    """).df()

    gas_cons = conn.execute("""
        SELECT country AS Country,
               iso3,
               Year,
               Consumtion
        FROM gas_cons
    """).df()

    gas = pd.merge(
        gas_prod, gas_cons,
        on=["Country", "iso3", "Year"],
        how="left"
    )
    gas["Type"] = "Gas"

    df = pd.concat([oil, gas], ignore_index=True)
    df["Consumtion"] = df["Consumtion"].fillna(0)

    return df


df = load_map_detail()

# =============================
# FILTERS
# =============================
st.subheader("Filters")

with st.expander("Map Filters", expanded=True):
    c1, c2, c3 = st.columns(3)

    with c1:
        energy_type = st.selectbox(
            "Energy Type",
            sorted(df["Type"].unique())
        )

    with c2:
        year = st.selectbox(
            "Year",
            sorted(df["Year"].dropna().unique())
        )

    with c3:
        country = st.selectbox(
            "Focus Country (optional)",
            ["All"] + sorted(df["Country"].dropna().unique())
        )

filtered_df = df[
    (df["Type"] == energy_type) &
    (df["Year"] == year)
]

# =============================
# MAP
# =============================
st.subheader(f"{energy_type} Production Map – {year}")

if country != "All":
    map_df = filtered_df[filtered_df["Country"] == country]
else:
    map_df = filtered_df

if not map_df.empty:
    fig = px.choropleth(
        map_df,
        locations="iso3",
        locationmode="ISO-3",
        color="Production",
        hover_name="Country",
        projection="robinson",
        color_continuous_scale="Blues",
        height=940
    )

    if country != "All":
        fig.update_geos(
            fitbounds="locations",
            visible=True
        )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(title="Production")
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for the selected filters.")

# =============================
# COUNTRY DETAIL
# =============================
st.subheader("Country Detail")

if country != "All" and not map_df.empty:
    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Production",
            f"{map_df['Production'].sum():,.0f}"
        )

    with c2:
        st.metric(
            "Consumption",
            f"{map_df['Consumtion'].sum():,.0f}"
        )

    st.line_chart(
        map_df.sort_values("Year").set_index("Year")[["Production", "Consumtion"]]
    )
else:
    st.info("Select a country to see detailed production & consumption trends.")

# =============================
# TOP COUNTRIES
# =============================
st.subheader("Top Producing Countries")

top = (
    filtered_df
    .groupby("Country", as_index=False)["Production"]
    .sum()
    .sort_values("Production", ascending=False)
    .head(10)
)

st.dataframe(top, use_container_width=True)

# =============================
# BACK BUTTON
# =============================
if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")

st.caption("Global Energy Production – Map Detail (DuckDB-based)")
