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

    tables_df = conn.execute("SHOW TABLES").df()
    table_col = [c for c in tables_df.columns if c.lower() in ("name","table_name")][0]
    tables = tables_df[table_col].tolist()

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
        # --- Production ---
        if "gas_prod" in tables:
            gas_prod = conn.execute("""
                SELECT Year, SUM(Production) AS Production
                FROM gas_prod
                GROUP BY Year
            """).df()
        elif "goget" in tables:
            gas_prod = conn.execute("""
                SELECT production_year AS Year,
                       SUM(production) AS Production
                FROM goget
                WHERE commodity = 'Gas'
                GROUP BY production_year
            """).df()
        else:
            gas_prod = pd.DataFrame(columns=["Year", "Production"])
    
        # --- Consumption ---
        if "gas_cons" in tables:
            gas_cons = conn.execute("""
                SELECT Year, SUM(Consumtion) AS Consumtion
                FROM gas_cons
                GROUP BY Year
            """).df()
        else:
            gas_cons = pd.DataFrame(columns=["Year", "Consumtion"])

        gas = pd.merge(gas_prod, gas_cons, on="Year", how="outer").fillna(0)
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
        
def filter_by_timespan(df, date_col, span):
    if df.empty:
        return df

    max_date = df[date_col].max()

    if span == "1Y":
        cutoff = max_date - pd.DateOffset(years=1)
    elif span == "3Y":
        cutoff = max_date - pd.DateOffset(years=3)
    elif span == "10Y":
        cutoff = max_date - pd.DateOffset(years=10)
    else:
        return df

    return df[df[date_col] >= cutoff]

# =============================
# LOAD DATA
# =============================
price_df = load_price_data()
prod_cons_df = load_prod_cons()
migas_map = load_map_data()

# =============================
# DUMMY SUBSIDY vs GDP
# =============================
# subsidy_gdp = pd.DataFrame({
#     "Country": ["Indonesia", "India", "China", "United States", "Saudi Arabia"],
#     "Fuel Subsidy (% GDP)": [2.1, 1.8, 0.9, 0.4, 3.2],
#     "GDP (Trillion USD)": [1.4, 3.4, 17.7, 26.9, 1.1]
# })

# =============================
# ROW 1 (3 COLUMNS)
# =============================
col1, col2= st.columns(3)

with col1:
    st.subheader("Global Oil Price Comparison")

    span_price = st.radio(
        "Time span",
        ["1Y", "3Y", "10Y"],
        horizontal=True,
        key="price_span"
    )

    price_filtered = filter_by_timespan(
        price_df,
        "period",
        span_price
    )
    
    fig = px.line(price_filtered, x="period", y="value", color="benchmark",
                  labels={"value": "USD / Barrel", "period": "Date", "benchmark": "Oil Type"},
                  height=260)
    fig.update_traces(opacity=0.45)
    fig.update_layout(legend_title_text="Click to focus / hide", hovermode="x unified")
    st.plotly_chart(fig)

    if st.button("View more..."):
        st.switch_page("pages/Harga_Minyak_Detail.py")

with col2:
    st.subheader("Global Production vs Consumption")
    energy_type = st.radio(
        "Energy Type",
        ["Oil", "Gas"],
        horizontal=True,
        key="energy_type"
    )

    # span_energy = st.radio(
    #     "Time span",
    #     ["1Y", "3Y", "10Y"],
    #     horizontal=True,
    #     key="energy_span"
    # )

    filtered_df = prod_cons_df[prod_cons_df["Energy"] == energy_type]
    
    fig = px.line(
        filtered_df,
        x="Year",
        y=["Production", "Consumtion"],
        labels={"value": "Volume", "variable": "Metric"},
        height=260
    )
    st.plotly_chart(fig, use_container_width=True)


    if st.button("View more.."):
        st.switch_page("pages/Consumption_Production.py")

# with col3:
#     st.subheader("Fuel Subsidy vs GDP")
    
#     fig = px.bar(
#         subsidy_gdp,
#         x="Fuel Subsidy (% GDP)",
#         y="Country",
#         orientation="h",
#         height=260
#     )
    
#     st.plotly_chart(fig, use_container_width=True)

# =============================
# ROW 2 – MAP
# =============================
st.subheader("Global Energy Production Map")

selected_country = st.selectbox(
    "Focus on country (optional)",
    ["All"] + sorted(migas_map["Country"].dropna().unique())
)

fig = px.choropleth(
    migas_map,
    locations="iso3",
    color="Production",
    hover_name="Country",
    projection="robinson",
    color_continuous_scale="Blues",
    height=820
)

if selected_country != "All":
    country_row = migas_map[migas_map["Country"] == selected_country]

    if not country_row.empty:
        fig.update_geos(
            fitbounds="locations",
            visible=True
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
