
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "data" / "processed" / "cleaned_sales.csv"
REPORT_DIR = ROOT / "outputs" / "reports"
FIGURE_DIR = ROOT / "outputs" / "figures"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

def load_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found: {INPUT_FILE}\n"
            "Run src/clean_data.py first."
        )

    df = pd.read_csv(
        INPUT_FILE,
        dtype={
            "InvoiceNo": "string",
            "StockCode": "string",
            "CustomerID": "string",
        },
        low_memory=False,
    )

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], errors="coerce"
    )
    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )
    df["UnitPrice"] = pd.to_numeric(
        df["UnitPrice"], errors="coerce"
    )
    df["LineRevenue"] = pd.to_numeric(
        df["LineRevenue"], errors="coerce"
    )

    df = df.dropna(
        subset=["InvoiceNo", "StockCode", "InvoiceDate",
                "Quantity", "UnitPrice", "LineRevenue"]
    )

    return df


# --------------------------------------------------
# 3. OVERALL SALES KPIs
# --------------------------------------------------

def create_kpis(df):
    kpis = pd.DataFrame({
        "Metric": [
            "Sales lines",
            "Unique invoices",
            "Unique products",
            "Unique identified customers",
            "Countries served",
            "Total line revenue",
            "Average revenue per invoice",
            "Average units per sales line",
        ],
        "Value": [
            len(df),
            df["InvoiceNo"].nunique(),
            df["StockCode"].nunique(),
            df["CustomerID"].nunique(),
            df["Country"].nunique(),
            round(df["LineRevenue"].sum(), 2),
            round(
                df.groupby("InvoiceNo")["LineRevenue"].sum().mean(), 2
            ),
            round(df["Quantity"].mean(), 2),
        ],
    })

    kpis.to_csv(REPORT_DIR / "sales_kpis.csv", index=False)

    return kpis


# --------------------------------------------------
# 4. MONTHLY SALES TREND
# --------------------------------------------------

def monthly_sales(df):
    data = df.copy()
    data["Month"] = (
        data["InvoiceDate"].dt.to_period("M").astype(str)
    )

    result = (
        data.groupby("Month", as_index=False)
        .agg(
            Revenue=("LineRevenue", "sum"),
            Invoices=("InvoiceNo", "nunique"),
            Units=("Quantity", "sum"),
        )
        .sort_values("Month")
    )

    result.to_csv(
        REPORT_DIR / "monthly_sales.csv", index=False
    )

    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=result, x="Month", y="Revenue",
        marker="o"
    )
    plt.title("Monthly Sales Revenue")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(
        FIGURE_DIR / "monthly_sales.png", dpi=150
    )
    plt.close()

    return result


# --------------------------------------------------
# 5. TOP PRODUCTS
# --------------------------------------------------

def top_products(df):
    result = (
        df.groupby("StockCode", as_index=False)
        .agg(
            Description=("Description", "first"),
            UnitsSold=("Quantity", "sum"),
            Revenue=("LineRevenue", "sum"),
            InvoiceCount=("InvoiceNo", "nunique"),
        )
        .sort_values("Revenue", ascending=False)
        .head(15)
    )

    result.to_csv(
        REPORT_DIR / "top_products.csv", index=False
    )

    plot_data = result.copy()
    plot_data["Product"] = (
        plot_data["StockCode"].astype(str)
        + " - "
        + plot_data["Description"].fillna("Unknown")
        .astype(str).str.slice(0, 28)
    )

    plt.figure(figsize=(12, 7))
    sns.barplot(
        data=plot_data,
        x="Revenue",
        y="Product",
    )
    plt.title("Top 15 Products by Revenue")
    plt.xlabel("Revenue")
    plt.ylabel("Product")
    plt.tight_layout()
    plt.savefig(
        FIGURE_DIR / "top_products.png", dpi=150
    )
    plt.close()

    return result


# --------------------------------------------------
# 6. TOP COUNTRIES
# --------------------------------------------------

def country_sales(df):
    result = (
        df.groupby("Country", as_index=False)
        .agg(
            Revenue=("LineRevenue", "sum"),
            Invoices=("InvoiceNo", "nunique"),
            UnitsSold=("Quantity", "sum"),
        )
        .sort_values("Revenue", ascending=False)
    )

    result.to_csv(
        REPORT_DIR / "country_sales.csv", index=False
    )

    plot_data = result.head(10).sort_values("Revenue")

    plt.figure(figsize=(11, 6))
    sns.barplot(
        data=plot_data,
        x="Revenue",
        y="Country",
    )
    plt.title("Top 10 Countries by Revenue")
    plt.xlabel("Revenue")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.savefig(
        FIGURE_DIR / "country_sales.png", dpi=150
    )
    plt.close()

    return result


# --------------------------------------------------
# 7. RUN ANALYSIS
# --------------------------------------------------

def main():
    print("Loading cleaned sales data...")
    df = load_data()

    if df.empty:
        raise ValueError("No valid sales records found.")

    print("Generating sales KPIs...")
    kpis = create_kpis(df)

    print("Analyzing monthly sales...")
    monthly = monthly_sales(df)

    print("Finding top products...")
    products = top_products(df)

    print("Analyzing country sales...")
    countries = country_sales(df)

    print("\n========== SALES ANALYSIS COMPLETE ==========")
    print("\nSALES KPIs")
    print(kpis.to_string(index=False))

    print("\nTOP 5 PRODUCTS BY REVENUE")
    print(products.head(5).to_string(index=False))

    print("\nTOP 5 COUNTRIES BY REVENUE")
    print(countries.head(5).to_string(index=False))

    print("\nMONTHLY SALES")
    print(monthly.to_string(index=False))

    print(f"\nReports saved to: {REPORT_DIR}")
    print(f"Charts saved to: {FIGURE_DIR}")


if __name__ == "__main__":
    main()