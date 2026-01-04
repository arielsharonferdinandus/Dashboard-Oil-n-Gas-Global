import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

st.set_page_config(page_title="Energy Map – Detail", layout="wide")
st.title("Global Energy Production – Map Detail")
st.caption("DuckDB-based Data")

@st.cache_data
def load_map():
    conn = duckdb.connect(database="data/energy.duckdb", read_only=True)
    oil_prod = conn.execute("SELECT Country, iso3, Year, Production FROM oil_prod").df()
    oil_prod["Type"]="Oil"
    gas_prod = conn.execute("SELECT country AS Country, iso3, production_year AS Year, production AS Production FROM goget WHERE commodity='Gas'").df()
    gas_prod["Type"]="Gas"
    return pd.concat([oil_prod, gas_prod], ignore_index=True)

map_df = load_map()

# SELECTORS
col1, col2 = st.columns(2)
with col1:
    selected_type = st.selectbox("Energy Type", sorted(map_df["Type"].unique()))
with col2:
    selected_year = st.selectbox("Year", sorted(map_df["Year"].dropna().unique()))

filtered_df = map_df[(map_df["Type"]==selected_type) & (map_df["Year"]==selected_year)]

# MAP
st.subheader(f"{selected_type} Production – {selected_year}")
if not filtered_df.empty:
    fig = px.choropleth(filtered_df, locations="iso3", color="Production",
                        hover_name="Country", color_continuous_scale="YlOrRd",
                        projection="natural earth", height=500)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data for this selection.")

# TOP 10 TABLE
st.subheader(f"Top Production Countries – {selected_type} {selected_year}")
if not filtered_df.empty:
    st.dataframe(filtered_df.sort_values("Production", ascending=False).head(10), use_container_width=True)
else:
    st.info("No data to display.")

if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")
