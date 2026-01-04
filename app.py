import streamlit as st
import pandas as pd
import plotly.express as px
from utils.duckdb_conn import get_duckdb_connection

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="Global Energy Dashboard", layout="wide")
st.title("Global Energy Dashboard")
st.caption("Oil, Gas & Energy Visualization – Prototype")

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_price_data():
    conn = get_duckdb_connection()

    query = """
        SELECT period, benchmark, value
        FROM energy.main.price
        WHERE benchmark IN ('Brent', 'WTI', 'Henry Hub')
        ORDER BY period
    """
    df = conn.execute(query).fetchdf()
    conn.close()

    df["period"] = pd.to_datetime(df["period"])
    return df


@st.cache_data
def load_prod_cons():
    conn = get_duckdb_connection()

    query = """
        SELECT Year, Energy,
               SUM(Production) AS Production,
               SUM(Consumtion) AS Consumtion
        FROM (
            SELECT Year, 'Oil' AS Energy, Production, 0::DOUBLE AS Consumtion
            FROM energy.main.oil_prod

            UNION ALL
            SELECT Year, 'Oil', 0::DOUBLE, Consumtion
            FROM energy.main.oil_cons

            UNION ALL
            SELECT Year, 'Gas', Production, 0::DOUBLE
            FROM energy.main.gas_prod

            UNION ALL
            SELECT Year, 'Gas', 0::DOUBLE, Consumtion
            FROM energy.main.gas_cons
        )
        GROUP BY Year, Energy
        ORDER BY Year
    """
    df = conn.execute(query).fetchdf()
    conn.close()
    return df


price_df = load_price_data()
prod_cons_df = load_prod_cons()

# =============================
# ROW 1
# =============================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Global Oil Price Comparison")
    fig = px.line(
        price_df,
        x="period",
        y="value",
        color="benchmark",
        height=260
    )
    fig.update_traces(opacity=0.45)
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("View more..."):
        st.switch_page("pages/Harga_Minyak_Detail.py")


with col2:
    st.subheader("Global Production vs Consumption")

    if "energy_type" not in st.session_state:
        st.session_state.energy_type = "Oil"

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Oil", type="primary" if st.session_state.energy_type == "Oil" else "secondary"):
            st.session_state.energy_type = "Oil"
    with c2:
        if st.button("Gas", type="primary" if st.session_state.energy_type == "Gas" else "secondary"):
            st.session_state.energy_type = "Gas"

    filtered_df = prod_cons_df[prod_cons_df["Energy"] == st.session_state.energy_type]

    fig = px.line(
        filtered_df,
        x="Year",
        y=["Production", "Consumtion"],
        height=260
    )
    fig.update_traces(opacity=0.45)
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("View more.."):
        st.switch_page("pages/Consumption_Production.py")


with col3:
    st.subheader("Fuel Subsidy vs GDP (Dummy)")
    st.info("Dummy visualization – not from DuckDB")

# =============================
# FOOTER
# =============================
st.caption("Streamlit Energy Dashboard – DuckDB Powered")
