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
st.caption("Country-Level Oil & Gas Production and Consumption")

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
    oil["Energy"] = "Oil"

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
    gas["Energy"] = "Gas"

    df = pd.concat([oil, gas], ignore_index=True)
    df["Consumtion"] = df["Consumtion"].fillna(0)

    return df


df = load_map_detail()

# =============================
# FILTERS (MAP ONLY)
# =============================
st.subheader("Map Filters")

c1, c2, c3 = st.columns(3)

with c1:
    energy_type = st.selectbox(
        "Energy Type (Map)",
        ["Oil", "Gas"]
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

map_df = df[
    (df["Energy"] == energy_type) &
    (df["Year"] == year)
]

if country != "All":
    map_df = map_df[map_df["Country"] == country]

# =============================
# MAP
# =============================
st.subheader(f"{energy_type} Production Map – {year}")

if not map_df.empty:
    fig = px.choropleth(
        map_df,
        locations="iso3",
        locationmode="ISO-3",
        color="Production",
        hover_name="Country",
        projection="robinson",
        color_continuous_scale="Blues",
        height=900
    )

    if country != "All":
        fig.update_geos(fitbounds="locations", visible=True)

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for selected filters.")

# =============================
# COUNTRY DETAIL (OIL + GAS)
# =============================
st.subheader("Country Detail – Oil & Gas")

if country != "All":
    country_df = df[df["Country"] == country]

    if not country_df.empty:
        # ---- TABLE ----
        st.markdown("### Detailed Data Table")
        st.dataframe(
            country_df.sort_values(["Energy", "Year"]),
            use_container_width=True
        )

        # ---- BAR CHARTS ----
        col1, col2 = st.columns(2)

        for energy, col in zip(["Oil", "Gas"], [col1, col2]):
            with col:
                energy_df = (
                    country_df[country_df["Energy"] == energy]
                    .groupby("Energy", as_index=False)[["Production", "Consumtion"]]
                    .sum()
                )

                if not energy_df.empty:
                    fig_bar = px.bar(
                        energy_df.melt(
                            id_vars="Energy",
                            value_vars=["Production", "Consumtion"],
                            var_name="Metric",
                            value_name="Value"
                        ),
                        x="Metric",
                        y="Value",
                        color="Metric",
                        title=f"{energy}: Production vs Consumption",
                        height=360
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info(f"No {energy} data for this country.")
    else:
        st.warning("No data available for selected country.")
else:
    st.info("Select a country to see Oil & Gas details.")

# =============================
# BACK
# =============================
if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")

st.caption("Global Energy Production – Map Detail")
