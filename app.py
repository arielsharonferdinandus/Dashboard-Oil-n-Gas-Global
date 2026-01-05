import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
from pathlib import Path

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Global Energy Dashboard",
    layout="wide"
)
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Global Energy Dashboard")
st.caption("Oil, Gas & Energy Visualization – DuckDB-based Prototype")

# =============================
# LOAD DATA FUNCTIONS
# =============================
DB_PATH = Path("data/db/energy.duckdb")

@st.cache_data
def load_price_data(db_path=DB_PATH):
    if not db_path.exists():
        st.error(f"DuckDB file not found: {db_path}")
        return pd.DataFrame(columns=["period","value","benchmark"])
    conn = duckdb.connect(database=str(db_path), read_only=True)
    try:
        df = conn.execute("""
            SELECT date AS period, price AS value, benchmark
            FROM price
            WHERE benchmark IN ('Brent', 'WTI', 'Henry Hub')
            ORDER BY date
        """).df()
        df["period"] = pd.to_datetime(df["period"])
        return df
    except Exception as e:
        st.warning(f"Failed to load price data: {e}")
        return pd.DataFrame(columns=["period","value","benchmark"])

@st.cache_data
def load_prod_cons(db_path=DB_PATH):
    if not db_path.exists():
        st.error(f"DuckDB file not found: {db_path}")
        return pd.DataFrame(columns=["Year","Production","Consumtion","Energy"])
    conn = duckdb.connect(database=str(db_path), read_only=True)
    dfs = []

    # OIL
    try:
        oil_prod = conn.execute("SELECT Year, SUM(Production) AS Production FROM oil_prod GROUP BY Year").df()
        oil_cons = conn.execute("SELECT Year, SUM(Consumtion) AS Consumtion FROM oil_cons GROUP BY Year").df()
        oil = pd.merge(oil_prod, oil_cons, on="Year", how="outer").fillna(0)
        oil["Energy"] = "Oil"
        dfs.append(oil)
    except Exception as e:
        st.warning(f"Failed to load oil data: {e}")

    # GAS
    try:
        gas_prod = conn.execute("""
            SELECT Year AS Year, SUM(production) AS Production
            FROM gas_prod
            WHERE commodity='Gas'
            GROUP BY Year
        """).df()
        gas_cons = conn.execute("""
            SELECT Year, SUM(Consumtion) AS Consumtion
            FROM gas_cons
            GROUP BY Year
        """).df()
        gas = pd.merge(gas_prod, gas_cons, on="Year", how="outer")
        gas["Energy"] = "Gas"
        dfs.append(gas)
    except Exception as e:
        st.warning(f"Failed to load gas data: {e}")

    if dfs:
        df = pd.concat(dfs, ignore_index=True).sort_values("Year")
        return df
    else:
        return pd.DataFrame(columns=["Year","Production","Consumtion","Energy"])

@st.cache_data
def load_map_data(db_path=DB_PATH):
    if not db_path.exists():
        st.error(f"DuckDB file not found: {db_path}")
        return pd.DataFrame(columns=["Country","iso3","Production"])
    conn = duckdb.connect(database=str(db_path), read_only=True)
    try:
        df = conn.execute("""
            SELECT country AS Country, iso3, SUM(production) AS Production
            FROM goget
            GROUP BY country, iso3
        """).df()
        return df
    except Exception as e:
        st.warning(f"Failed to load map data: {e}")
        return pd.DataFrame(columns=["Country","iso3","Production"])

# =============================
# LOAD DATA
# =============================
price_df = load_price_data()
prod_cons_df = load_prod_cons()
migas_map = load_map_data()

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
    st.subheader("Global Oil Price Comparison")
    fig = px.line(price_df, x="period", y="value", color="benchmark",
                  labels={"value": "USD / Barrel", "period": "Date", "benchmark": "Oil Type"},
                  height=260)
    fig.update_traces(opacity=0.45)
    fig.update_layout(legend_title_text="Click to focus / hide", hovermode="x unified")
    st.plotly_chart(fig)

    if st.button("View more..."):
        st.switch_page("pages/Harga_Minyak_Detail.py")

with col2:
    st.subheader("Global Production vs Consumption")

    if "energy_type" not in st.session_state:
        st.session_state.energy_type = "Oil"

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Oil", type="primary" if st.session_state.energy_type=="Oil" else "secondary"):
            st.session_state.energy_type = "Oil"
    with c2:
        if st.button("Gas", type="primary" if st.session_state.energy_type=="Gas" else "secondary"):
            st.session_state.energy_type = "Gas"

    energy_type = st.session_state.energy_type
    st.caption(f"Selected energy type: **{energy_type}**")

    filtered_df = prod_cons_df[prod_cons_df["Energy"]==energy_type]
    fig = px.line(filtered_df, x="Year", y=["Production","Consumtion"],
                  labels={"value":"Volume","variable":"Metric"}, height=260)
    fig.update_traces(opacity=0.45)
    fig.update_layout(legend_title_text="Click to focus / hide", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("View more.."):
        st.switch_page("pages/Consumption_Production.py")

with col3:
    st.subheader("Fuel Subsidy vs GDP")
    fig = px.scatter(subsidy_gdp, x="GDP (Trillion USD)", y="Fuel Subsidy (% GDP)",
                     size="Fuel Subsidy (% GDP)", hover_name="Country", height=260)
    st.plotly_chart(fig, use_container_width=True)

# =============================
# ROW 2 – MAP
# =============================
st.subheader("Global Energy Production Map")
fig = px.choropleth(
    migas_map,
    locations="iso3",
    color="Production",
    hover_name="Country",
    projection="robinson",
    color_continuous_scale="Blues",
    height=820
)

st.plotly_chart(fig, use_container_width=True)

if st.button("Map Detail..."):
    st.switch_page("pages/Map_Detail.py")

# =============================
# NEWS SECTION
# =============================
st.subheader("Global Migas News & Analysis")
news = [
    {"title": "OPEC+ Considers Production Cut", "source": "Reuters",
     "summary": "OPEC+ members are discussing potential production cuts amid weakening global demand.",
     "image": "images/download.jpeg"},
    {"title": "Middle East Tensions Push Oil Prices Higher", "source": "Bloomberg",
     "summary": "Escalating geopolitical risks in the Middle East have increased volatility in oil markets.",
     "image": "images/download (1).jpeg"},
    {"title": "Global Energy Transition Impacts Oil Demand", "source": "IEA",
     "summary": "The shift towards renewable energy continues to reshape long-term oil demand outlook.",
     "image": "images/download (2).jpeg"}
]
for article in news:
    col_img, col_text = st.columns([1,4])
    with col_img: st.image(article["image"], width=150)
    with col_text:
        st.markdown(f"**{article['title']}**")
        st.caption(article["source"])
        st.write(article["summary"])
    st.markdown("---")

st.caption("Streamlit Energy Dashboard – DuckDB-based Prototype")
