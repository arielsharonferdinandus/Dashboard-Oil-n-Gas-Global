import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Global Energy Dashboard",
    layout="wide"
)

st.title("Global Energy Dashboard")
st.caption("Oil, Gas & Energy Visualization – Prototype")

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_price_data():
    df = pd.read_csv("data/csv/price_timeseries.csv")
    df["period"] = pd.to_datetime(df["period"])

    df = df[df["benchmark"].isin(["Brent", "WTI", "Henry Hub"])]
    df = df.sort_values("period")

    return df


@st.cache_data
def load_prod_cons_oil():
    prod = pd.read_csv("data/csv/country_production_oil.csv")
    cons = pd.read_csv("data/csv/country_consumtion_oil.csv")

    prod = prod.groupby("Year", as_index=False)["Production"].sum()
    cons = cons.groupby("Year", as_index=False)["Consumtion"].sum()

    df = pd.merge(prod, cons, on="Year", how="inner")
    return df


price_df = load_price_data()
prod_cons_df = load_prod_cons_oil()

# =============================
# DUMMY MAP DATA
# =============================
migas_map = pd.DataFrame({
    "Country": ["United States", "Saudi Arabia", "Russia", "China", "India", "Indonesia"],
    "iso3": ["USA", "SAU", "RUS", "CHN", "IND", "IDN"],
    "Production": [18.5, 12.1, 10.8, 4.2, 0.8, 0.7]
})

# =============================
# DUMMY SUBSIDY vs GDP
# =============================
subsidy_gdp = pd.DataFrame({
    "Country": ["Indonesia", "India", "China", "United States", "Saudi Arabia"],
    "Fuel Subsidy (% GDP)": [2.1, 1.8, 0.9, 0.4, 3.2],
    "GDP (Trillion USD)": [1.4, 3.4, 17.7, 26.9, 1.1]
})

# =============================
# ROW 1 (3 COLUMNS)
# =============================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🛢️ Global Oil Price Comparison")

    fig = px.line(
        price_df,
        x="period",
        y="value",
        color="benchmark",
        labels={
            "value": "USD / Barrel",
            "period": "Date",
            "benchmark": "Oil Type"
        },
        height=260
    )

    # Make non-selected lines slightly transparent
    fig.update_traces(opacity=0.45)
    fig.update_layout(
        legend_title_text="Click to focus / hide",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    if st.button("View more..."):
        st.switch_page("pages/Harga_Minyak_Detail.py")


with col2:
    st.subheader("Global Oil Production vs Consumption")
    fig = px.line(
        prod_cons_df,
        x="Year",
        y=["Production", "Consumtion"],
        labels={"value": "Volume", "variable": "Metric"},
        height=260
    )
    st.plotly_chart(fig, use_container_width=True)

    if st.button("View more..."):
        st.switch_page("pages/Consumption_Production.py")

with col3:
    st.subheader("Fuel Subsidy vs GDP (Dummy)")
    fig = px.scatter(
        subsidy_gdp,
        x="GDP (Trillion USD)",
        y="Fuel Subsidy (% GDP)",
        size="Fuel Subsidy (% GDP)",
        hover_name="Country",
        height=260
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================
# ROW 2 – MAP
# =============================
st.subheader("🗺️ Global Energy Production Map (Dummy Data)")

fig = px.choropleth(
    migas_map,
    locations="iso3",
    color="Production",
    hover_name="Country",
    projection="natural earth",
    color_continuous_scale="YlOrRd",
    height=420
)

st.plotly_chart(fig, use_container_width=True)

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

# =============================
# FOOTER
# =============================
st.caption("Streamlit Energy Dashboard – Dataset-based Prototype")
