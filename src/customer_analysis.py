from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "processed" / "cleaned_sales.csv"
REPORT_DIR = ROOT / "outputs" / "reports"
FIGURE_DIR = ROOT / "outputs" / "figures"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned data not found: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        dtype={
            "InvoiceNo": "string",
            "CustomerID": "string",
            "StockCode": "string",
        },
        low_memory=False,
    )

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], errors="coerce"
    )
    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )
    df["LineRevenue"] = pd.to_numeric(
        df["LineRevenue"], errors="coerce"
    )

    # Customer analysis requires an identified customer.
    customer_data = df.dropna(
        subset=[
            "CustomerID",
            "InvoiceNo",
            "InvoiceDate",
            "LineRevenue",
            "Quantity",
        ]
    ).copy()

    if customer_data.empty:
        raise ValueError("No valid identified-customer records found.")

    # Calculate one row per customer.
    customers = (
        customer_data.groupby("CustomerID")
        .agg(
            TotalSpend=("LineRevenue", "sum"),
            Orders=("InvoiceNo", "nunique"),
            UnitsPurchased=("Quantity", "sum"),
            FirstPurchase=("InvoiceDate", "min"),
            LastPurchase=("InvoiceDate", "max"),
            ProductLines=("StockCode", "count"),
        )
        .reset_index()
    )

    customers["AverageOrderValue"] = (
        customers["TotalSpend"] / customers["Orders"]
    )

    # Recency measured relative to the latest date in the dataset.
    reference_date = customer_data["InvoiceDate"].max().normalize()
    customers["RecencyDays"] = (
        reference_date - customers["LastPurchase"].dt.normalize()
    ).dt.days

    customers["CustomerType"] = customers["Orders"].apply(
        lambda orders: "Repeat" if orders >= 2 else "One-time"
    )

    # Transparent rule-based segments, not machine learning.
    def assign_segment(row):
        if row["Orders"] >= 5 and row["TotalSpend"] >= customers[
            "TotalSpend"
        ].median():
            return "Frequent High-Value"
        elif row["TotalSpend"] >= customers["TotalSpend"].quantile(0.75):
            return "High-Value"
        elif row["Orders"] >= 2:
            return "Repeat Customer"
        return "Occasional Customer"

    customers["Segment"] = customers.apply(assign_segment, axis=1)

    customers = customers.sort_values(
        "TotalSpend", ascending=False
    )

    customers.to_csv(
        REPORT_DIR / "customer_summary.csv", index=False
    )

    # Repeat-customer summary.
    total_customers = len(customers)
    repeat_customers = int((customers["Orders"] >= 2).sum())
    one_time_customers = int((customers["Orders"] == 1).sum())

    summary = pd.DataFrame({
        "Metric": [
            "Identified customers",
            "Repeat customers",
            "One-time customers",
            "Repeat customer rate (%)",
            "Total identified-customer revenue",
            "Average spend per customer",
            "Median spend per customer",
            "Average orders per customer",
        ],
        "Value": [
            total_customers,
            repeat_customers,
            one_time_customers,
            round(repeat_customers / total_customers * 100, 2),
            round(customers["TotalSpend"].sum(), 2),
            round(customers["TotalSpend"].mean(), 2),
            round(customers["TotalSpend"].median(), 2),
            round(customers["Orders"].mean(), 2),
        ],
    })

    summary.to_csv(
        REPORT_DIR / "customer_kpis.csv", index=False
    )

    segment_summary = (
        customers.groupby("Segment", as_index=False)
        .agg(
            Customers=("CustomerID", "count"),
            Revenue=("TotalSpend", "sum"),
            AverageSpend=("TotalSpend", "mean"),
        )
        .sort_values("Revenue", ascending=False)
    )

    segment_summary.to_csv(
        REPORT_DIR / "customer_segments.csv", index=False
    )

    # Chart 1: Top 10 customers by spend.
    top_customers = customers.head(10).copy()
    top_customers["CustomerID"] = (
        top_customers["CustomerID"].astype(str)
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=top_customers.sort_values("TotalSpend"),
        x="TotalSpend",
        y="CustomerID",
    )
    plt.title("Top 10 Customers by Total Spend")
    plt.xlabel("Total Spend")
    plt.ylabel("Customer ID")
    plt.tight_layout()
    plt.savefig(
        FIGURE_DIR / "top_customers.png", dpi=150
    )
    plt.close()

    # Chart 2: Customers by segment.
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=segment_summary,
        x="Customers",
        y="Segment",
    )
    plt.title("Customer Count by Segment")
    plt.xlabel("Number of Customers")
    plt.ylabel("Segment")
    plt.tight_layout()
    plt.savefig(
        FIGURE_DIR / "customer_segments.png", dpi=150
    )
    plt.close()

    print("\nCUSTOMER ANALYSIS COMPLETE")
    print("\nCUSTOMER KPIs")
    print(summary.to_string(index=False))

    print("\nCUSTOMER SEGMENTS")
    print(segment_summary.to_string(index=False))

    print("\nTOP 10 CUSTOMERS")
    print(
        customers[
            ["CustomerID", "TotalSpend", "Orders", "Segment"]
        ].head(10).to_string(index=False)
    )

    print(f"\nReports saved to: {REPORT_DIR}")
    print(f"Charts saved to: {FIGURE_DIR}")


if __name__ == "__main__":
    main()