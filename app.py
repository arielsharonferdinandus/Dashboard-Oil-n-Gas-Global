import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Global Energy Dashboard",
    layout="wide"
)

st.title("Global Energy Dashboard")
st.caption("Oil, Gas & Energy Visualization – DuckDB-based Prototype")

# =============================
# LOAD DATA FROM DUCKDB
# =============================
@st.cache_data
def load_price_data():
    conn = duckdb.connect(database="data/energy.duckdb", read_only=True)
    df = conn.execute("""
        SELECT date AS period, price AS value, benchmark, product AS product_name, units
        FROM price
        WHERE benchmark IN ('Brent','WTI','Henry Hub')
        ORDER BY date
    """).df()
    df["period"] = pd.to_datetime(df["period"])
    return df

@st.cache_data
def load_prod_cons_data():
    conn = duckdb.connect(database="data/energy.duckdb", read_only=True)

    # --- Oil ---
    prod_oil = conn.execute("SELECT Country, Year, Production, iso3 FROM oil_prod").df()
    cons_oil = conn.execute("SELECT Country, Year, Consumtion, iso3 FROM oil_cons").df()
    prod_oil["Energy"] = "Oil"
    cons_oil["Energy"] = "Oil"
    oil = pd.merge(prod_oil, cons_oil, on=["Country","Year"], how="outer")

    # --- Gas ---
    prod_gas = conn.execute("""
        SELECT country AS Country, production_year AS Year, production AS Production, iso3
        FROM goget WHERE commodity='Gas'
    """).df()
    cons_gas = pd.DataFrame(columns=["Country","Year","Consumtion","iso3"])  # placeholder
    prod_gas["Energy"] = "Gas"
    cons_gas["Energy"] = "Gas"
    gas = pd.merge(prod_gas, cons_gas, on=["Country","Year"], how="outer")

    df = pd.concat([oil, gas], ignore_index=True).fillna(0).sort_values("Year")
    return df

@st.cache_data
def load_map_data():
    conn = duckdb.connect(database="data/energy.duckdb", read_only=True)
    oil_prod = conn.execute("SELECT Country, iso3, Year, Production FROM oil_prod").df()
    oil_prod["Type"] = "Oil"
    gas_prod = conn.execute("""
        SELECT country AS Country, iso3, production_year AS Year, production AS Production
        FROM goget WHERE commodity='Gas'
    """).df()
    gas_prod["Type"] = "Gas"
    df = pd.concat([oil_prod, gas_prod], ignore_index=True)
    return df

price_df = load_price_data()
prod_cons_df = load_prod_cons_data()
map_df = load_map_data()

# =============================
# ROW 1 (3 COLUMNS)
# =============================
col1, col2, col3 = st.columns(3)

# --- Column 1: Price ---
with col1:
    st.subheader("Global Oil Price Comparison")
    fig = px.line(price_df, x="period", y="value", color="benchmark",
                  labels={"value":"USD/Barrel","period":"Date","benchmark":"Oil Type"}, height=260)
    fig.update_traces(opacity=0.45)
    fig.update_layout(legend_title_text="Click to focus / hide", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("View Price Detail..."):
        st.switch_page("pages/price_detail.py")

# --- Column 2: Production vs Consumption ---
with col2:
    st.subheader("Global Production vs Consumption")

    if "energy_type" not in st.session_state:
        st.session_state.energy_type = "Oil"

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛢️ Oil", type="primary" if st.session_state.energy_type=="Oil" else "secondary"):
            st.session_state.energy_type = "Oil"
    with c2:
        if st.button("🔥 Gas", type="primary" if st.session_state.energy_type=="Gas" else "secondary"):
            st.session_state.energy_type = "Gas"

    energy_type = st.session_state.energy_type
    filtered_df = prod_cons_df[prod_cons_df["Energy"]==energy_type]

    fig = px.line(filtered_df, x="Year", y=["Production","Consumtion"],
                  labels={"value":"Volume","variable":"Metric"}, height=260)
    fig.update_traces(opacity=0.45)
    fig.update_layout(legend_title_text="Click to focus / hide", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    if st.button("View Production Detail..."):
        st.switch_page("pages/map_detail.py")

# --- Column 3: Subsidy vs GDP (dummy) ---
with col3:
    st.subheader("Fuel Subsidy vs GDP (Dummy)")
    subsidy_gdp = pd.DataFrame({
        "Country": ["Indonesia", "India", "China", "United States", "Saudi Arabia"],
        "Fuel Subsidy (% GDP)": [2.1,1.8,0.9,0.4,3.2],
        "GDP (Trillion USD)":[1.4,3.4,17.7,26.9,1.1]
    })
    fig = px.scatter(subsidy_gdp, x="GDP (Trillion USD)", y="Fuel Subsidy (% GDP)",
                     size="Fuel Subsidy (% GDP)", hover_name="Country", height=260)
    st.plotly_chart(fig, use_container_width=True)

# =============================
# ROW 2 – MAP
# =============================
st.subheader("Global Energy Production Map (Dummy Data)")
fig = px.choropleth(map_df[map_df["Type"]=="Oil"], locations="iso3", color="Production",
                    hover_name="Country", projection="natural earth",
                    color_continuous_scale="YlOrRd", height=420)
st.plotly_chart(fig, use_container_width=True)
