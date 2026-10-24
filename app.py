import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Customer Behavior & Market Basket Analysis",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Customer Behavior & Market Basket Analysis")
st.write("Explore sales performance, customer behavior, and market basket insights.")

REPORTS_DIR = Path("outputs/reports")

@st.cache_data
def load_report(filename):
    path = REPORTS_DIR / filename
    if path.exists():
        return pd.read_csv(path)
    return None

# Sales overview
st.header("📊 Sales Overview")

sales = load_report("sales_summary.csv")

if sales is not None:
    st.dataframe(sales, use_container_width=True)
else:
    st.info("Sales summary report was not found.")

# Customer analysis
st.header("👥 Customer Analysis")

customers = load_report("customer_segments.csv")

if customers is not None:
    st.dataframe(customers, use_container_width=True)
else:
    st.info("Customer segment report was not found.")

# Market basket analysis
st.header("🛍️ Market Basket Analysis")

rules = load_report("market_basket_rules.csv")

if rules is not None:
    st.dataframe(rules.head(100), use_container_width=True)
else:
    st.info("Market basket rules are not available in the deployed repository yet.")

st.caption("Customer Behavior & Market Basket Analysis System")