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
st.caption("Country-Level Oil & Gas – Production & Consumption")

DB_PATH = Path("data/db/energy.duckdb")

# =============================
# LOAD DATA (MATCH app.py LOGIC)
# =============================
@st.cache_data
def load_map_detail(db_path=DB_PATH):
    conn = duckdb.connect(database=str(db_path), read_only=True)

    # ---------- OIL ----------
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

    # ---------- GAS (IMPORTANT FIX) ----------
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
# MAP FILTERS
# =============================
st.subheader("Map Filters")

c1, c2, c3 = st.columns(3)

with c1:
    energy_type = st.selectbox("Energy Type", ["Oil", "Gas"])

with c2:
    year = st.selectbox(
        "Year",
        sorted(df[df["Energy"] == energy_type]["Year"].dropna().unique())
    )

with c3:
    country = st.selectbox(
        "Focus Country",
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

fig = px.choropleth(
    map_df,
    locations="iso3",
    locationmode="ISO-3",
    color="Production",
    hover_name="Country",
    projection="robinson",
    color_continuous_scale="Blues",
    height=880
)

if country != "All":
    fig.update_geos(fitbounds="locations", visible=True)

fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig, use_container_width=True)

# =============================
# TOP 10 COUNTRIES (RESTORED)
# =============================
st.subheader(f"Top 10 {energy_type} Producing Countries – {year}")

top10 = (
    df[(df["Energy"] == energy_type) & (df["Year"] == year)]
    .groupby(["Country", "iso3"], as_index=False)["Production"]
    .sum()
    .sort_values("Production", ascending=False)
    .head(10)
)

st.dataframe(top10, use_container_width=True)

# =============================
# COUNTRY DETAIL (LATEST DATA)
# =============================
st.subheader("Country Detailed Information (Latest Available Data)")

if country != "All":
    country_df = df[df["Country"] == country]

    if not country_df.empty:
        # Latest per energy
        latest = (
            country_df
            .sort_values("Year")
            .groupby("Energy")
            .tail(1)
        )

        st.markdown("### Country Metadata")
        meta = latest[["Country", "iso3", "Energy", "Year"]]
        st.dataframe(meta, use_container_width=True)

        st.markdown("### Latest Production & Consumption")

        summary = latest[[
            "Energy", "Year", "Production", "Consumtion"
        ]]

        st.dataframe(summary, use_container_width=True)

        # ---------- BAR COMPARISON ----------
        col1, col2 = st.columns(2)

        for energy, col in zip(["Oil", "Gas"], [col1, col2]):
            with col:
                e_df = summary[summary["Energy"] == energy]
                if not e_df.empty:
                    fig_bar = px.bar(
                        e_df.melt(
                            id_vars=["Energy", "Year"],
                            value_vars=["Production", "Consumtion"],
                            var_name="Metric",
                            value_name="Value"
                        ),
                        x="Metric",
                        y="Value",
                        color="Metric",
                        title=f"{energy} – Latest Production vs Consumption",
                        height=360
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info(f"No {energy} data available.")
else:
    st.info("Select a country to view detailed information.")

# =============================
# BACK
# =============================
if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")

st.caption("Global Energy Production – Map Detail")
