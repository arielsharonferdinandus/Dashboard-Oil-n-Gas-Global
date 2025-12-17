import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def load_crude_oil_summary():
    wti = pd.read_csv(
        "data/csv/crude_oil_ching_ok_wti.csv",
        parse_dates=["date"]
    )
    brent = pd.read_csv(
        "data/csv/crude_oil_europe_brent.csv",
        parse_dates=["date"]
    )

    wti = wti.rename(columns={"price": "WTI"})
    brent = brent.rename(columns={"price": "Brent"})

    df = pd.merge(brent, wti, on="date", how="inner")
    df = df.sort_values("date").tail(90)

    return df

st.set_page_config(page_title="Global Energy Dashboard", layout="wide")

st.title("Global Energy Dashboard")
st.caption("Oil, Gas & Energy Visualization – Prototype")

years = list(range(2015, 2031))
subsidy_df = pd.DataFrame({
    "Year": years,
    "Explicit": np.random.uniform(4, 6, len(years)),
    "Implicit": np.random.uniform(3, 5, len(years))
})
subsidy_df["Total"] = subsidy_df["Explicit"] + subsidy_df["Implicit"]

years_pc = list(range(1965, 2022))
prod_cons_df = pd.DataFrame({
    "Year": years_pc,
    "Production": np.linspace(30, 85, len(years_pc)) + np.random.randn(len(years_pc)) * 3,
    "Consumption": np.linspace(5, 75, len(years_pc)) + np.random.randn(len(years_pc)) * 3
})

transparency_df = pd.DataFrame({
    "Year": list(range(2000, 2022)),
    "Index": np.random.normal(0.5, 0.6, 22)
})

migas_map = pd.DataFrame({
    "Country": ["United States", "Saudi Arabia", "Russia", "China", "India", "Indonesia"],
    "ISO": ["USA", "SAU", "RUS", "CHN", "IND", "IDN"],
    "Production": [18.5, 12.1, 10.8, 4.2, 0.8, 0.7]
})

dates = pd.date_range("2024-01-01", periods=180)
oil_price = pd.DataFrame({
    "Date": dates,
    "Price": np.random.uniform(60, 90, len(dates))
})

price_table = pd.DataFrame({
    "Commodity": ["Brent", "WTI", "Gas Alam", "Bensin", "Solar"],
    "Price": np.random.uniform(1, 100, 5),
    "Daily %": np.random.uniform(-2, 2, 5),
    "Monthly %": np.random.uniform(-10, 10, 5)
})

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
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Harga Minyak Global")

    oil_price = load_crude_oil_summary()

    fig = px.line(
        oil_price,
        x="date",
        y=["Brent", "WTI"],
        height=200
    )
    st.plotly_chart(fig, use_container_width=True)

    if st.button("View more..."):
        st.switch_page("pages/Harga_Minyak_Detail.py")

with col2:
    st.subheader("Produksi & Konsumsi Minyak Global")
    fig = px.line(prod_cons_df, x="Year", y=["Production", "Consumption"], height=300)
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.subheader("Pendapatan & Transparansi Industri Ekstraktif")
    fig = px.scatter(transparency_df, x="Year", y="Index", height=300)
    fig.add_hline(y=0, line_dash="dash")
    st.plotly_chart(fig, use_container_width=True)

col4, col5 = st.columns([2, 1])

with col4:
    st.subheader("Peta Persebaran Energi Global")
    fig = px.choropleth(
        migas_map,
        locations="ISO",
        color="Production",
        hover_name="Country",
        projection="natural earth",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

with col5:
    st.subheader("Subsidi Energi")
    fig = go.Figure()
    fig.add_bar(x=subsidy_df["Year"], y=subsidy_df["Explicit"], name="Explicit")
    fig.add_bar(x=subsidy_df["Year"], y=subsidy_df["Implicit"], name="Implicit")
    fig.add_trace(go.Scatter(
        x=subsidy_df["Year"], y=subsidy_df["Total"],
        mode="lines+markers", name="Total"
    ))
    fig.update_layout(barmode="stack", height=300)
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# News Section
# -----------------------------
st.subheader("Global Migas News & Analysis")

for article in news:
    col_img, col_text = st.columns([1, 4])

    with col_img:
        st.image(article["image"], width=200)

    with col_text:
        st.markdown(f"**{article['title']}**")
        st.caption(article["source"])
        st.write(article["summary"])

st.caption("Streamlit Prototype")
