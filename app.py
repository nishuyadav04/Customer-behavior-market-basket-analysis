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


def show_report(filename, title):
    st.subheader(title)
    data = load_report(filename)

    if data is not None:
        st.dataframe(data, use_container_width=True)
    else:
        st.info(f"{filename} is not available in the deployed repository.")


# Sales overview
st.header("📊 Sales Overview")
show_report("sales_kpis.csv", "Sales KPIs")
show_report("monthly_sales.csv", "Monthly Sales")
show_report("country_sales.csv", "Sales by Country")
show_report("top_products.csv", "Top Products")

# Customer analysis
st.header("👥 Customer Analysis")
show_report("customer_kpis.csv", "Customer KPIs")
show_report("customer_segments.csv", "Customer Segments")
show_report("customer_summary.csv", "Customer Summary")

# Market basket analysis
st.header("🛒 Market Basket Analysis")
show_report("basket_item_support.csv", "Popular Items and Basket Support")

st.caption("Customer Behavior & Market Basket Analysis System")