import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
from pathlib import Path

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Global Oil Production – Map Detail",
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

st.title("Global Oil Production – Map Detail")
st.caption("Country-Level Oil Production & Consumption")

DB_PATH = Path("data/db/energy.duckdb")

# =============================
# LOAD DATA (OIL ONLY)
# =============================
@st.cache_data
def load_oil_data(db_path=DB_PATH):
    conn = duckdb.connect(database=str(db_path), read_only=True)

    oil_prod = conn.execute("""
        SELECT Country, iso3, Year, Production
        FROM oil_prod
    """).df()

    oil_cons = conn.execute("""
        SELECT Country, iso3, Year, Consumtion
        FROM oil_cons
    """).df()

    oil = pd.merge(
        oil_prod,
        oil_cons,
        on=["Country", "iso3", "Year"],
        how="left"
    )

    oil["Consumtion"] = oil["Consumtion"].fillna(0)
    return oil


df = load_oil_data()

# =============================
# YEAR DEFAULT = 2023
# =============================
available_years = sorted(df["Year"].dropna().unique())
default_year = 2023 if 2023 in available_years else max(available_years)

# =============================
# MAP FILTERS
# =============================
st.subheader("Map Filters")

c1, c2 = st.columns(2)

with c1:
    year = st.selectbox(
        "Year",
        available_years,
        index=available_years.index(default_year)
    )

with c2:
    country = st.selectbox(
        "Focus Country",
        ["All"] + sorted(df["Country"].dropna().unique())
    )

metric = st.radio(
    "Metric",
    ["Production", "Consumtion"],
    horizontal=True
)

map_df = df[df["Year"] == year]

if country != "All":
    map_df = map_df[map_df["Country"] == country]

# =============================
# MAP
# =============================
st.subheader(f"Oil {metric} Map – {year}")

fig = px.choropleth(
    map_df,
    locations="iso3",
    locationmode="ISO-3",
    color=metric,
    hover_name="Country",
    projection="robinson",
    color_continuous_scale="Blues",
    height=860
)

if country != "All":
    fig.update_geos(fitbounds="locations", visible=True)

fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig, use_container_width=True)

# =============================
# COUNTRY DETAIL (LATEST DATA)
# =============================
st.subheader("Country Detail – Latest Available Data")

if country != "All":
    country_df = df[df["Country"] == country]

    if not country_df.empty:
        latest = (
            country_df
            .sort_values("Year")
            .iloc[-1]
        )

        detail = pd.DataFrame({
            "Field": [
                "Country",
                "ISO3 Code",
                "Latest Year",
                "Oil Production",
                "Oil Consumption"
            ],
            "Value": [
                latest["Country"],
                latest["iso3"],
                int(latest["Year"]),
                round(latest["Production"], 2),
                round(latest["Consumtion"], 2)
            ]
        })

        st.dataframe(detail, use_container_width=True, hide_index=True)
    else:
        st.info("No data available for this country.")
else:
    st.info("Select a country to view detailed information.")

# =============================
# TOP 10 COUNTRIES
# =============================
st.subheader(f"Top 10 Oil {metric} Countries – {year}")

top10 = (
    df[df["Year"] == year]
    .groupby(["Country", "iso3"], as_index=False)[metric]
    .sum()
    .sort_values(metric, ascending=False)
    .head(10)
)

st.dataframe(top10, use_container_width=True)

# =============================
# BACK
# =============================
if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")

st.caption("Global Oil Production – Map Detail")
