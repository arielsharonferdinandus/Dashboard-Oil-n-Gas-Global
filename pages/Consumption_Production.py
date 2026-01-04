import streamlit as st
import plotly.express as px
import pandas as pd
from utils.duckdb_conn import get_duckdb_connection

st.set_page_config(page_title="Energy Consumption & Production", layout="wide")
st.title("Energy Consumption & Production – Detail View")

@st.cache_data
def load_energy_data():
    conn = get_duckdb_connection()

    query = """
        SELECT Year, Country, Consumtion, 'Oil' AS Type
        FROM energy.main.oil_cons

        UNION ALL
        SELECT Year, Country, Production AS Consumtion, 'Oil'
        FROM energy.main.oil_prod

        UNION ALL
        SELECT Year, Country, Consumtion, 'Gas'
        FROM energy.main.gas_cons

        UNION ALL
        SELECT Year, Country, Production AS Consumtion, 'Gas'
        FROM energy.main.gas_prod
    """
    df = conn.execute(query).fetchdf()
    conn.close()
    return df


df = load_energy_data()

col1, col2, col3 = st.columns(3)
with col1:
    energy_type = st.selectbox("Energy Type", sorted(df["Type"].unique()))
with col2:
    country = st.selectbox("Country", sorted(df["Country"].unique()))
with col3:
    view = st.selectbox("View Mode", ["Yearly Trend", "Latest Snapshot"])

filtered = df[(df["Type"] == energy_type) & (df["Country"] == country)]

if view == "Yearly Trend":
    fig = px.line(filtered, x="Year", y="Consumtion", height=420)
    st.plotly_chart(fig, use_container_width=True)
else:
    latest = filtered.sort_values("Year").iloc[-1]
    st.dataframe(pd.DataFrame({
        "Metric": ["Year", "Value"],
        "Value": [latest["Year"], latest["Consumtion"]]
    }), use_container_width=True, hide_index=True)

if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")
