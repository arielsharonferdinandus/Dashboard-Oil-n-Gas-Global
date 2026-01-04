import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

st.set_page_config(page_title="Energy Price – Detail", layout="wide")
st.title("Global Energy Price – Detail")
st.caption("DuckDB-based Data")

@st.cache_data
def load_price():
    conn = duckdb.connect(database="data/energy.duckdb", read_only=True)
    df = conn.execute("""
        SELECT date AS period, price AS value, benchmark, product AS product_name, units
        FROM price ORDER BY date
    """).df()
    df["period"] = pd.to_datetime(df["period"])
    return df

price_df = load_price()

# SELECTORS
col1, col2 = st.columns(2)
with col1:
    selected_benchmark = st.selectbox("Select Benchmark", sorted(price_df["benchmark"].unique()))
with col2:
    selected_product = st.selectbox("Select Product",
                                    sorted(price_df[price_df["benchmark"]==selected_benchmark]["product_name"].dropna().unique()))

filtered_df = price_df[(price_df["benchmark"]==selected_benchmark) & (price_df["product_name"]==selected_product)]

# CHART
st.subheader("Price Time Series")
if not filtered_df.empty:
    fig = px.line(filtered_df, x="period", y="value",
                  labels={"period":"Date","value":f"Price ({filtered_df['units'].iloc[0]})"},
                  height=420)
    st.plotly_chart(fig, use_container_width=True)

# SNAPSHOT
st.subheader("Latest Snapshot")
if not filtered_df.empty:
    latest = filtered_df.iloc[-1]
    st.dataframe(pd.DataFrame({
        "Metric":["Date","Price","Units","Benchmark","Product"],
        "Value":[latest["period"].date(), round(latest["value"],2), latest["units"], latest["benchmark"], latest["product_name"]]
    }), use_container_width=True, hide_index=True)

if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")
