import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Global Energy Price – Detail View",
    layout="wide"
)

st.title("📈 Global Energy Price – Detail View")
st.caption("Based on International Energy Price Time Series")

DATA_DIR = Path("data/csv")

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_price_timeseries():
    df = pd.read_csv(DATA_DIR / "price_timeseries.csv")
    df["period"] = pd.to_datetime(df["period"])
    df = df.sort_values("period")
    return df


price_df = load_price_timeseries()

# =============================
# SELECTORS
# =============================
st.subheader("Energy Price Explorer")

col1, col2 = st.columns(2)

with col1:
    selected_benchmark = st.selectbox(
        "Select Benchmark",
        sorted(price_df["benchmark"].dropna().unique())
    )

with col2:
    filtered_products = (
        price_df[price_df["benchmark"] == selected_benchmark]
        ["product-name"]
        .dropna()
        .unique()
    )

    selected_product = st.selectbox(
        "Select Product",
        sorted(filtered_products)
    )

# =============================
# FILTER DATA
# =============================
filtered_df = price_df[
    (price_df["benchmark"] == selected_benchmark) &
    (price_df["product-name"] == selected_product)
]

# =============================
# PRICE CHART
# =============================
st.subheader("Price Time Series")

fig = px.line(
    filtered_df,
    x="period",
    y="value",
    labels={
        "period": "Date",
        "value": f"Price ({filtered_df['units'].iloc[0]})"
    },
    height=420
)

st.plotly_chart(fig, use_container_width=True)

# =============================
# ACTION BUTTONS
# =============================
col_btn1, col_btn2 = st.columns([1, 1])

with col_btn1:
    if st.button("⬅ Back to Dashboard"):
        st.switch_page("app.py")

with col_btn2:
    if st.button("📊 View Production vs Consumption"):
        st.switch_page("pages/Consumption_Production.py")

# =============================
# LATEST SNAPSHOT
# =============================
st.subheader("Latest Price Snapshot")

latest = filtered_df.iloc[-1]

snapshot = pd.DataFrame({
    "Metric": [
        "Date",
        "Price",
        "Units",
        "Benchmark",
        "Product"
    ],
    "Value": [
        latest["period"].date(),
        round(latest["value"], 2),
        latest["units"],
        latest["benchmark"],
        latest["product-name"]
    ]
})

st.dataframe(snapshot, use_container_width=True, hide_index=True)

# =============================
# NEWS SECTION
# =============================
st.subheader("📰 Global Migas News & Analysis")

news = [
    {
        "title": "OPEC+ Considers Production Cut",
        "source": "Reuters",
        "summary": "OPEC+ members are discussing potential production cuts amid weakening global demand.",
        "image": "images/download.jpeg"
    },
    {
        "title": "Middle East Tensions Push Oil Prices Higher",
        "source": "Bloomberg",
        "summary": "Escalating geopolitical risks in the Middle East have increased volatility in oil markets.",
        "image": "images/download (1).jpeg"
    },
    {
        "title": "Global Energy Transition Impacts Oil Demand",
        "source": "IEA",
        "summary": "The shift towards renewable energy continues to reshape long-term oil demand outlook.",
        "image": "images/download (2).jpeg"
    }
]

for article in news:
    col_img, col_text = st.columns([1, 4])

    with col_img:
        st.image(article["image"], width=150)

    with col_text:
        st.markdown(f"**{article['title']}**")
        st.caption(article["source"])
        st.write(article["summary"])

    st.markdown("---")

st.caption("Energy Price Dashboard – Detail View (Dataset-based)")
