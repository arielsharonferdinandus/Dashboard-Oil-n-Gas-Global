import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Global Energy Production – Map Detail",
    layout="wide"
)

st.title("Global Energy Production – Map Detail")
st.caption("Country-Level Production Data (DuckDB-based)")

# =============================
# DUCKDB CONNECTION
# =============================
@st.cache_data
def get_duckdb_connection(db_path="data/energy.duckdb"):
    conn = duckdb.connect(database=db_path, read_only=True)
    return conn

conn = get_duckdb_connection()

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_map_data():
    # Oil production
    oil_prod = conn.execute("""
        SELECT Country, iso3, Year, Production
        FROM oil_prod
    """).df()
    oil_prod["Type"] = "Oil"

    # Gas production from goget
    gas_prod = conn.execute("""
        SELECT country AS Country,
               iso3,
               production_year AS Year,
               production AS Production
        FROM goget
        WHERE commodity='Gas'
    """).df()
    gas_prod["Type"] = "Gas"

    df = pd.concat([oil_prod, gas_prod], ignore_index=True)
    return df

map_df = load_map_data()

# =============================
# SELECTORS
# =============================
st.subheader("Energy Production Explorer")

col1, col2 = st.columns(2)

with col1:
    selected_type = st.selectbox(
        "Energy Type",
        sorted(map_df["Type"].unique())
    )

with col2:
    selected_year = st.selectbox(
        "Year",
        sorted(map_df["Year"].dropna().unique())
    )

# =============================
# FILTER DATA
# =============================
filtered_df = map_df[
    (map_df["Type"] == selected_type) &
    (map_df["Year"] == selected_year)
]

# =============================
# CHOROPLETH MAP
# =============================
st.subheader(f"Global {selected_type} Production – {selected_year}")

if not filtered_df.empty:
    fig = px.choropleth(
        filtered_df,
        locations="iso3",
        color="Production",
        hover_name="Country",
        color_continuous_scale="YlOrRd",
        projection="natural earth",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No production data available for the selected type/year.")

# =============================
# LATEST SNAPSHOT TABLE
# =============================
st.subheader(f"Top Production Countries – {selected_type} {selected_year}")

if not filtered_df.empty:
    top_countries = filtered_df.sort_values("Production", ascending=False).head(10)
    st.dataframe(
        top_countries[["Country", "Production", "iso3"]],
        use_container_width=True
    )
else:
    st.info("No data available to display top countries.")

# =============================
# BACK BUTTON
# =============================
if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")

st.caption("Global Energy Production – Map Detail (DuckDB-based)")
