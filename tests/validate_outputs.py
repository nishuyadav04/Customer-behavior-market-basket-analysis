from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed" / "cleaned_sales.csv"
REPORTS = ROOT / "outputs" / "reports"
FIGURES = ROOT / "outputs" / "figures"

required_files = [
    DATA,
    REPORTS / "sales_kpis.csv",
    REPORTS / "monthly_sales.csv",
    REPORTS / "top_products.csv",
    REPORTS / "country_sales.csv",
    REPORTS / "customer_summary.csv",
    REPORTS / "customer_kpis.csv",
    REPORTS / "customer_segments.csv",
    REPORTS / "basket_item_support.csv",
    REPORTS / "market_basket_rules.csv",
    FIGURES / "monthly_sales.png",
    FIGURES / "top_products.png",
    FIGURES / "country_sales.png",
    FIGURES / "top_customers.png",
    FIGURES / "customer_segments.png",
    FIGURES / "top_product_pairs.png",
]

missing = [str(path.relative_to(ROOT)) for path in required_files
           if not path.exists()]

if missing:
    print("MISSING OUTPUTS:")
    for file in missing:
        print(" -", file)
    raise SystemExit(1)

df = pd.read_csv(
    DATA,
    dtype={"InvoiceNo": "string", "StockCode": "string",
           "CustomerID": "string"},
    low_memory=False,
)

assert len(df) == 524878, f"Unexpected row count: {len(df)}"
assert df["InvoiceNo"].notna().all(), "Missing invoice numbers"
assert df["StockCode"].notna().all(), "Missing stock codes"
assert (df["Quantity"] > 0).all(), "Nonpositive quantity found"
assert (df["UnitPrice"] > 0).all(), "Nonpositive unit price found"
assert pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
).notna().all(), "Invalid dates found"

rules = pd.read_csv(REPORTS / "market_basket_rules.csv")

if not rules.empty:
    assert rules["Support"].between(0, 1).all()
    assert rules["Confidence"].between(0, 1).all()
    assert (rules["Lift"] >= 0).all()

print("VALIDATION PASSED")
print("Cleaned rows:", len(df))
print("Unique invoices:", df["InvoiceNo"].nunique())
print("Identified customers:", df["CustomerID"].nunique())
print("Market basket rules:", len(rules))
print("All required reports and charts exist.")