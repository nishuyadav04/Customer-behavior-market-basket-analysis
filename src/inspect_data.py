
from pathlib import Path

import pandas as pd


# Project paths: this script lives in the project's src folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "raw" / "Online Retail.xlsx"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports"
REPORT_FILE = REPORT_DIR / "dataset_inspection.txt"

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


def inspect_dataset() -> None:
    """Load the original Excel workbook and save an inspection report."""

    if not DATA_FILE.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}\n"
            "Place Online Retail.xlsx inside data/raw/."
        )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading the original dataset...")
    print(f"File: {DATA_FILE}")

    # Keep identifiers as strings; do not alter the source workbook.
    df = pd.read_excel(
        DATA_FILE,
        dtype={
            "InvoiceNo": "string",
            "StockCode": "string",
            "CustomerID": "string",
        },
        engine="openpyxl",
    )

    if df.empty:
        raise ValueError(
            "The Excel worksheet contains no data rows. "
            "Check that you downloaded the correct dataset."
        )

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "The dataset does not have the expected UCI columns.\n"
            f"Missing columns: {missing_columns}\n"
            f"Actual columns: {df.columns.tolist()}"
        )

    # Create a normalized, in-memory view for inspection only.
    # The original Excel file is never overwritten.
    invoice_text = df["InvoiceNo"].astype("string").str.strip()
    quantity = pd.to_numeric(df["Quantity"], errors="coerce")
    unit_price = pd.to_numeric(df["UnitPrice"], errors="coerce")
    invoice_date = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    cancellation_mask = invoice_text.str.upper().str.startswith(
        "C", na=False
    )

    report_lines = [
        "UCI ONLINE RETAIL - DATASET INSPECTION REPORT",
        "=" * 55,
        "",
        f"Source file: {DATA_FILE}",
        f"Rows: {len(df):,}",
        f"Columns: {len(df.columns):,}",
        "",
        "1. COLUMN NAMES",
        "-" * 30,
        *[str(column) for column in df.columns],
        "",
        "2. DATA TYPES",
        "-" * 30,
        df.dtypes.to_string(),
        "",
        "3. MISSING VALUES",
        "-" * 30,
        df.isna().sum().to_string(),
        "",
        "4. DUPLICATE ROWS",
        "-" * 30,
        f"Exact duplicate rows: {int(df.duplicated().sum()):,}",
        "",
        "5. INVOICE CHECKS",
        "-" * 30,
        f"Missing invoice numbers: {int(invoice_text.isna().sum()):,}",
        (
            "Invoice numbers beginning with C "
            f"(cancellation indicators): {int(cancellation_mask.sum()):,}"
        ),
        "",
        "6. NUMERIC DATA CHECKS",
        "-" * 30,
        f"Quantity values that cannot be parsed: {int(quantity.isna().sum()):,}",
        f"Zero or negative quantities: {int((quantity <= 0).sum()):,}",
        f"Unit prices that cannot be parsed: {int(unit_price.isna().sum()):,}",
        f"Zero or negative unit prices: {int((unit_price <= 0).sum()):,}",
        "",
        "7. DATE CHECKS",
        "-" * 30,
        (
            "Invoice dates that cannot be parsed: "
            f"{int(invoice_date.isna().sum()):,}"
        ),
    ]

    valid_dates = invoice_date.dropna()
    if not valid_dates.empty:
        report_lines.extend(
            [
                f"Earliest valid invoice date: {valid_dates.min()}",
                f"Latest valid invoice date: {valid_dates.max()}",
            ]
        )
    else:
        report_lines.append("No valid invoice dates were found.")

    report_lines.extend(
        [
            "",
            "8. NUMERIC DESCRIPTIVE STATISTICS",
            "-" * 30,
            df[["Quantity", "UnitPrice"]]
            .describe()
            .to_string(),
            "",
            "9. SAMPLE ROWS",
            "-" * 30,
            df.head(10).to_string(index=False),
            "",
            "10. INSPECTION NOTES",
            "-" * 30,
            "No rows were deleted or modified in the source workbook.",
            "Cancellation indicators do not by themselves identify every return.",
            "Negative quantities and non-positive prices require review before cleaning.",
            "Missing values and duplicates are reported, not automatically removed.",
        ]
    )

    report = "\n".join(report_lines) + "\n"
    REPORT_FILE.write_text(report, encoding="utf-8")

    print("\n--- Dataset inspection summary ---")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")
    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nMissing values by column:")
    print(df.isna().sum().to_string())

    print(f"\nExact duplicate rows: {int(df.duplicated().sum()):,}")
    print(f"Cancellation-indicator rows: {int(cancellation_mask.sum()):,}")

    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))

    print(f"\nFull inspection report saved to:\n{REPORT_FILE}")


if __name__ == "__main__":
    try:
        inspect_dataset()
    except (FileNotFoundError, ValueError, OSError, ImportError) as exc:
        print(f"\nERROR: {exc}")
        raise SystemExit(1) from exc
