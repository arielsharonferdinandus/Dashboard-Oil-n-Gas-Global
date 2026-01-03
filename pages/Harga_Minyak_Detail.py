import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(layout="wide")

st.title("Global Energy Price – Detail View")

# =============================
# Data Config
# =============================
DATA_DIR = Path("data/csv")

FUEL_FILES = {
    "Crude Oil - WTI (Cushing, OK)": "crude_oil_ching_ok_wti.csv",
    "Crude Oil - Brent (Europe)": "crude_oil_europe_brent.csv",
    "Gasoline - NY Harbor": "gasoline_new_york_harbor.csv",
    "Gasoline - US Gulf Coast": "gasoline_us_gulf_coast.csv",
    "Jet Fuel - US Gulf Coast": "jet_fuel_us_gulf_coast.csv",
    "Propane - Mont Belvieu": "propane_mont_belvieu.csv",
    "RBOB Gasoline - Los Angeles": "rbob_gasoline_los_angeles_reformulated.csv",
}

@st.cache_data
def load_price_file(filename):
    df = pd.read_csv(DATA_DIR / filename, parse_dates=["date"])
    df = df.sort_values("date")

    df["price"] = (
        df["price"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
    )

    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # IMPORTANT: remove rows with invalid prices
    df = df.dropna(subset=["price"])

    return df

# =============================
# Selector
# =============================
st.subheader("Energy Price Explorer")

selected_label = st.selectbox(
    "Select Fuel & Market",
    list(FUEL_FILES.keys())
)

df = load_price_file(FUEL_FILES[selected_label])

# =============================
# Price Chart
# =============================
fig = px.line(
    df,
    x="date",
    y="price",
    title=selected_label,
    labels={
        "date": "Date",
        "price": "USD / Unit"
    }
)
st.plotly_chart(fig, use_container_width=True)

st.caption("Source: U.S. Energy Information Administration (EIA)")

# =============================
# Latest Price Table
# =============================
st.subheader("Latest Price Snapshot")

latest = df.iloc[-1]

price_table = pd.DataFrame({
    "Metric": ["Date", "Price (USD)"],
    "Value": [latest["date"].date(), round(latest["price"], 2)]
})

st.dataframe(price_table, use_container_width=True, hide_index=True)

# =============================
# News Section
# =============================
st.subheader("Global Migas News & Analysis")

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
        st.image(article["image"], width=160)

    with col_text:
        st.markdown(f"**{article['title']}**")
        st.caption(article["source"])
        st.write(article["summary"])

    st.markdown("---")

# =============================
# Back Button
# =============================
if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")
