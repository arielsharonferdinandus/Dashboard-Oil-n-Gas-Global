import streamlit as st
import plotly.express as px
from utils.duckdb_conn import get_duckdb_connection
import pandas as pd

st.set_page_config(page_title="Global Energy Price – Detail View", layout="wide")
st.title("Global Energy Price – Detail View")

@st.cache_data
def load_price_timeseries():
    conn = get_duckdb_connection()

    query = """
        SELECT period, benchmark, product_name, value, units
        FROM energy.main.price
        ORDER BY period
    """
    df = conn.execute(query).fetchdf()
    conn.close()

    df["period"] = pd.to_datetime(df["period"])
    return df


price_df = load_price_timeseries()

st.subheader("Energy Price Explorer")

col1, col2 = st.columns(2)
with col1:
    selected_benchmark = st.selectbox(
        "Select Benchmark",
        sorted(price_df["benchmark"].unique())
    )

with col2:
    selected_product = st.selectbox(
        "Select Product",
        sorted(
            price_df[price_df["benchmark"] == selected_benchmark]["product_name"].unique()
        )
    )

filtered_df = price_df[
    (price_df["benchmark"] == selected_benchmark) &
    (price_df["product_name"] == selected_product)
]

fig = px.line(filtered_df, x="period", y="value", height=420)
st.plotly_chart(fig, use_container_width=True)

latest = filtered_df.iloc[-1]
st.dataframe(pd.DataFrame({
    "Metric": ["Date", "Price", "Unit"],
    "Value": [latest["period"].date(), latest["value"], latest["units"]]
}), use_container_width=True, hide_index=True)

if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")
