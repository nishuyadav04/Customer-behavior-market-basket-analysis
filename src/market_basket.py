from pathlib import Path
from itertools import combinations
from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "processed" / "cleaned_sales.csv"
REPORT_DIR = ROOT / "outputs" / "reports"
FIGURE_DIR = ROOT / "outputs" / "figures"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

# Minimum number of invoices containing a product pair.
MIN_PAIR_COUNT = 20


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Cleaned data not found: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        dtype={"InvoiceNo": "string", "StockCode": "string"},
        low_memory=False,
    )

    df = df.dropna(subset=["InvoiceNo", "StockCode"]).copy()

    # One occurrence of each product per invoice.
    # This prevents repeated lines for the same product
    # from inflating basket counts.
    baskets = (
        df.groupby("InvoiceNo")["StockCode"]
        .apply(lambda items: sorted(set(items)))
    )

    total_invoices = len(baskets)

    if total_invoices == 0:
        raise ValueError("No valid invoices found.")

    print(f"Transactions: {total_invoices:,}")
    print("Counting product and product-pair occurrences...")

    item_counts = Counter()
    pair_counts = Counter()

    for items in baskets:
        item_counts.update(items)
        pair_counts.update(combinations(items, 2))

    # Item support: proportion of invoices containing each product.
    item_support = pd.DataFrame(
        [
            {
                "StockCode": item,
                "InvoiceCount": count,
                "Support": count / total_invoices,
            }
            for item, count in item_counts.items()
        ]
    ).sort_values("InvoiceCount", ascending=False)

    descriptions = (
        df.dropna(subset=["StockCode"])
        .drop_duplicates("StockCode")
        .set_index("StockCode")["Description"]
    )

    item_support["Description"] = (
        item_support["StockCode"].map(descriptions)
    )

    item_support.to_csv(
        REPORT_DIR / "basket_item_support.csv", index=False
    )

    # Build pair metrics and both directional rules.
    rules = []

    for (item_a, item_b), pair_count in pair_counts.items():
        if pair_count < MIN_PAIR_COUNT:
            continue

        support_pair = pair_count / total_invoices
        support_a = item_counts[item_a] / total_invoices
        support_b = item_counts[item_b] / total_invoices

        # A -> B
        confidence_ab = pair_count / item_counts[item_a]
        lift_ab = confidence_ab / support_b

        rules.append({
            "Antecedent": item_a,
            "AntecedentDescription": descriptions.get(item_a),
            "Consequent": item_b,
            "ConsequentDescription": descriptions.get(item_b),
            "InvoiceCount": pair_count,
            "Support": support_pair,
            "Confidence": confidence_ab,
            "Lift": lift_ab,
        })

        # B -> A
        confidence_ba = pair_count / item_counts[item_b]
        lift_ba = confidence_ba / support_a

        rules.append({
            "Antecedent": item_b,
            "AntecedentDescription": descriptions.get(item_b),
            "Consequent": item_a,
            "ConsequentDescription": descriptions.get(item_a),
            "InvoiceCount": pair_count,
            "Support": support_pair,
            "Confidence": confidence_ba,
            "Lift": lift_ba,
        })

    columns = [
        "Antecedent",
        "AntecedentDescription",
        "Consequent",
        "ConsequentDescription",
        "InvoiceCount",
        "Support",
        "Confidence",
        "Lift",
    ]

    rules_df = pd.DataFrame(rules, columns=columns)

    if not rules_df.empty:
        rules_df = rules_df.sort_values(
            ["Lift", "InvoiceCount"],
            ascending=[False, False],
        )

    rules_df.to_csv(
        REPORT_DIR / "market_basket_rules.csv", index=False
    )

    # Chart: most frequently co-purchased product pairs.
    if pair_counts:
        top_pairs = pair_counts.most_common(15)

        plot_df = pd.DataFrame(
            [
                {
                    "Pair": (
                        f"{a} + {b}: "
                        f"{descriptions.get(a, 'Unknown')} / "
                        f"{descriptions.get(b, 'Unknown')}"
                    ),
                    "Invoices": count,
                }
                for (a, b), count in top_pairs
            ]
        ).sort_values("Invoices")

        plt.figure(figsize=(13, 9))
        sns.barplot(data=plot_df, x="Invoices", y="Pair")
        plt.title("Top 15 Product Pairs by Invoice Count")
        plt.xlabel("Invoices containing both products")
        plt.ylabel("Product pair")
        plt.tight_layout()
        plt.savefig(
            FIGURE_DIR / "top_product_pairs.png", dpi=150
        )
        plt.close()

    print("\nMARKET BASKET ANALYSIS COMPLETE")
    print(f"Transactions analyzed: {total_invoices:,}")
    print(f"Unique products: {len(item_counts):,}")
    print(f"Unique product pairs: {len(pair_counts):,}")
    print(f"Rules meeting minimum pair count: {len(rules_df):,}")

    if not rules_df.empty:
        print("\nTOP 10 RULES BY LIFT")
        print(rules_df.head(10).to_string(index=False))
    else:
        print(
            "No rules met the minimum pair count. "
            "Review MIN_PAIR_COUNT if needed."
        )

    print(f"\nReports saved to: {REPORT_DIR}")
    print(f"Charts saved to: {FIGURE_DIR}")


if __name__ == "__main__":
    main()
