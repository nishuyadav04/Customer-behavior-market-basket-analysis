
from pathlib import Path

import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "Online Retail.xlsx"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports"

CLEANED_FILE = PROCESSED_DIR / "cleaned_sales.csv"
AUDIT_FILE = PROCESSED_DIR / "cleaning_audit.csv"
SUMMARY_FILE = REPORT_DIR / "cleaning_summary.txt"

EXPECTED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]

MANDATORY_FIELDS = [
    "InvoiceNo",
    "StockCode",
    "InvoiceDate",
    "Country",
]


def main():
    # Check that the source dataset exists
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_FILE}\n"
            "Please check that Online Retail.xlsx is inside data/raw/."
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading source dataset...")

    df = pd.read_excel(
        RAW_FILE,
        dtype={
            "InvoiceNo": "string",
            "StockCode": "string",
            "CustomerID": "string",
        },
        engine="openpyxl",
    )

    missing_columns = sorted(set(EXPECTED_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(
            f"Dataset is missing expected columns: {missing_columns}"
        )

    original_rows = len(df)

    # Normalize text fields before checking missing values and duplicates.
    for column in [
        "InvoiceNo",
        "StockCode",
        "Description",
        "CustomerID",
        "Country",
    ]:
        df[column] = df[column].astype("string").str.strip()
        df[column] = df[column].replace("", pd.NA)

    # Convert numeric and date columns safely.
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"], errors="coerce"
    )

    print("Applying data-quality checks...")

    # Keep every original record in the audit output, with exclusion flags.
    flags = pd.DataFrame(index=df.index)

    flags["exact_duplicate"] = df.duplicated(keep="first")
    flags["missing_mandatory_field"] = df[MANDATORY_FIELDS].isna().any(
        axis=1
    )
    flags["missing_description"] = df["Description"].isna()
    flags["missing_customer_id"] = df["CustomerID"].isna()
    flags["invalid_quantity"] = df["Quantity"].isna()
    flags["nonpositive_quantity"] = df["Quantity"].le(0).fillna(False)
    flags["invalid_unit_price"] = df["UnitPrice"].isna()
    flags["nonpositive_unit_price"] = df["UnitPrice"].le(0).fillna(False)
    flags["cancellation_invoice"] = (
        df["InvoiceNo"].str.upper().str.startswith("C", na=False)
    )

    # Initial policy: exclude duplicate rows, cancellation invoices,
    # and records with missing mandatory fields or invalid/nonpositive
    # quantity or unit price. Retain missing customer IDs in sales data.
    exclusion_reasons = [
        "exact_duplicate",
        "missing_mandatory_field",
        "invalid_quantity",
        "nonpositive_quantity",
        "invalid_unit_price",
        "nonpositive_unit_price",
        "cancellation_invoice",
    ]

    flags["excluded_from_sales"] = flags[exclusion_reasons].any(axis=1)

    # Save the audit dataset before filtering so excluded records remain
    # available for review.
    audit = df.copy()
    audit["LineRevenue"] = audit["Quantity"] * audit["UnitPrice"]

    for column in flags.columns:
        audit[column] = flags[column]

    audit["included_in_sales"] = ~flags["excluded_from_sales"]

    audit.to_csv(AUDIT_FILE, index=False)

    # Create the clean sales dataset.
    sales = df.loc[~flags["excluded_from_sales"]].copy()
    sales["LineRevenue"] = sales["Quantity"] * sales["UnitPrice"]

    sales.to_csv(CLEANED_FILE, index=False)

    # Generate a summary from the actual processing results.
    summary_lines = [
        "CUSTOMER BEHAVIOR & MARKET BASKET ANALYSIS",
        "DATA CLEANING SUMMARY",
        "=" * 50,
        f"Source file: {RAW_FILE}",
        f"Original rows: {original_rows:,}",
        f"Rows retained for sales analysis: {len(sales):,}",
        f"Rows excluded from sales analysis: "
        f"{int(flags['excluded_from_sales'].sum()):,}",
        "",
        "Quality flag counts (flags can overlap):",
    ]

    for column in flags.columns:
        summary_lines.append(
            f"{column}: {int(flags[column].sum()):,}"
        )

    summary_lines.extend(
        [
            "",
            f"Missing CustomerID in retained sales: "
            f"{int(sales['CustomerID'].isna().sum()):,}",
            f"Retained sales line revenue: "
            f"{sales['LineRevenue'].sum():,.2f}",
            "",
            "Policy notes:",
            "- Cancellation invoices are excluded from sales analysis.",
            "- Nonpositive quantities and unit prices are excluded.",
            "- Exact duplicate rows after normalization are excluded.",
            "- Missing CustomerID is allowed in sales data.",
            "- All input rows and quality flags are preserved in the audit.",
        ]
    )

    SUMMARY_FILE.write_text(
        "\n".join(summary_lines) + "\n",
        encoding="utf-8",
    )

    print("\nCleaning completed.")
    print(f"Original rows: {original_rows:,}")
    print(f"Retained rows: {len(sales):,}")
    print(f"Excluded rows: {int(flags['excluded_from_sales'].sum()):,}")
    print(f"\nCleaned data: {CLEANED_FILE}")
    print(f"Audit data:   {AUDIT_FILE}")
    print(f"Summary:      {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
