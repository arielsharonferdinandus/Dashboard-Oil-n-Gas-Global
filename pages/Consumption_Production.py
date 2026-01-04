import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
from pathlib import Path

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Energy Consumption & Production – Detail View",
    layout="wide"
)

st.title("Energy Consumption & Production – Detail View")
st.caption("Country-Level Oil & Gas Data (DuckDB-based)")

DB_PATH = Path("data/db/energy.duckdb")

# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_energy_data(db_path=DB_PATH):
    if not db_path.exists():
        st.error(f"DuckDB file not found: {db_path}")
        # return empty DataFrames
        return pd.DataFrame(), pd.DataFrame()

    conn = duckdb.connect(database=str(db_path), read_only=True)

    # --- Check existing tables ---
    try:
        tables_df = conn.execute("SHOW TABLES").df()
        table_col = [c for c in tables_df.columns if c.lower() in ("name","table_name")][0]
        tables = tables_df[table_col].tolist()
    except Exception as e:
        st.warning(f"Failed to list tables: {e}")
        tables = []

    # --- Consumption ---
    cons_dfs = []
    if "oil_cons" in tables:
        try:
            cons_oil = conn.execute("""
                SELECT Country, Year, Consumption AS Consumtion, iso3
                FROM oil_cons
            """).df()
            cons_oil["Type"] = "Oil"
            cons_dfs.append(cons_oil)
        except Exception as e:
            st.warning(f"Failed to load oil consumption: {e}")

    if "gas_cons" in tables:
        try:
            cons_gas = conn.execute("""
                SELECT Country, Year, Consumption AS Consumtion, iso3
                FROM gas_cons
            """).df()
            cons_gas["Type"] = "Gas"
            cons_dfs.append(cons_gas)
        except Exception as e:
            st.warning(f"Failed to load gas consumption: {e}")

    if cons_dfs:
        cons = pd.concat(cons_dfs, ignore_index=True)
    else:
        cons = pd.DataFrame(columns=["Country","Year","Consumtion","iso3","Type"])

    # --- Production ---
    prod_dfs = []
    if "oil_prod" in tables:
        try:
            prod_oil = conn.execute("""
                SELECT Country, Year, Production, iso3
                FROM oil_prod
            """).df()
            prod_oil["Type"] = "Oil"
            prod_dfs.append(prod_oil)
        except Exception as e:
            st.warning(f"Failed to load oil production: {e}")

    if "goget" in tables:
        try:
            prod_gas = conn.execute("""
                SELECT country AS Country,
                       production_year AS Year,
                       production AS Production,
                       iso3
                FROM goget
                WHERE commodity='Gas'
            """).df()
            prod_gas["Type"] = "Gas"
            prod_dfs.append(prod_gas)
        except Exception as e:
            st.warning(f"Failed to load gas production: {e}")

    if prod_dfs:
        prod = pd.concat(prod_dfs, ignore_index=True)
    else:
        prod = pd.DataFrame(columns=["Country","Year","Production","iso3","Type"])

    return cons, prod

# =============================
# LOAD DATA
# =============================
cons_df, prod_df = load_energy_data()

# =============================
# SELECTORS
# =============================
st.subheader("Energy Data Explorer")

col1, col2, col3 = st.columns(3)

with col1:
    selected_type = st.selectbox(
        "Energy Type",
        sorted(cons_df["Type"].unique()) if not cons_df.empty else []
    )

with col2:
    selected_country = st.selectbox(
        "Country",
        sorted(cons_df["Country"].dropna().unique()) if not cons_df.empty else []
    )

with col3:
    view_mode = st.selectbox(
        "View Mode",
        ["Yearly Trend", "Latest Snapshot"]
    )

# =============================
# FILTER DATA
# =============================
if not cons_df.empty and not prod_df.empty:
    cons_filtered = cons_df[
        (cons_df["Type"] == selected_type) &
        (cons_df["Country"] == selected_country)
    ]

    prod_filtered = prod_df[
        (prod_df["Type"] == selected_type) &
        (prod_df["Country"] == selected_country)
    ]

    merged_df = pd.merge(
        cons_filtered[["Year", "Consumtion"]],
        prod_filtered[["Year", "Production"]],
        on="Year",
        how="outer"
    ).sort_values("Year")
else:
    merged_df = pd.DataFrame(columns=["Year","Consumtion","Production"])

# =============================
# YEARLY TREND
# =============================
if view_mode == "Yearly Trend":
    st.subheader(f"{selected_country} – {selected_type} Consumption vs Production")
    if not merged_df.empty:
        fig = px.line(
            merged_df,
            x="Year",
            y=["Consumtion", "Production"],
            labels={"value": "Volume", "variable": "Metric"},
            height=420
        )
        fig.update_traces(opacity=0.45)
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available to display.")

# =============================
# LATEST SNAPSHOT
# =============================
else:
    st.subheader(f"{selected_country} – Latest {selected_type} Snapshot")
    if not merged_df.dropna().empty:
        latest_row = merged_df.dropna().iloc[-1]
        snapshot = pd.DataFrame({
            "Metric": ["Year", "Consumtion", "Production", "Energy Type", "Country"],
            "Value": [
                int(latest_row["Year"]),
                round(latest_row["Consumtion"], 2),
                round(latest_row["Production"], 2),
                selected_type,
                selected_country
            ]
        })
        st.dataframe(snapshot, use_container_width=True, hide_index=True)
    else:
        st.info("No data available for the selected country/type.")

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
    col_img, col_text = st.columns([1, 4])
    with col_img: st.image(article["image"], width=150)
    with col_text:
        st.markdown(f"**{article['title']}**")
        st.caption(article["source"])
        st.write(article["summary"])
    st.markdown("---")

# =============================
# BACK BUTTON
# =============================
if st.button("⬅ Back to Dashboard"):
    st.switch_page("app.py")

st.caption("Energy Consumption & Production – Detail View (DuckDB-based)")
