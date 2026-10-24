# Customer Behavior & Market Basket Analysis System

## Project Overview

This project analyzes online retail transaction data to understand customer purchasing behavior, identify sales trends, segment customers, and discover product associations using Market Basket Analysis.

The project combines Python-based data analysis with an interactive Power BI dashboard to transform raw retail data into actionable business insights.

## Objectives

- Analyze sales and revenue trends over time.
- Identify top-performing products and countries.
- Segment customers based on purchasing behavior.
- Discover product associations using Market Basket Analysis.
- Present key business insights through a Power BI dashboard.

## Tools and Technologies

- **Python** — data cleaning and analysis
- **Pandas and NumPy** — data manipulation
- **Matplotlib and Seaborn** — data visualization
- **MLxtend** — association rule mining
- **Power BI Desktop** — interactive dashboard development
- **Jupyter Notebook / VS Code** — development environment

## Dataset

**Source:** UCI Machine Learning Repository — Online Retail

The dataset contains transactional records from a UK-based online retailer.

Dataset: https://archive.ics.uci.edu/dataset/352/online+retail

## Key Results

- **524,878** cleaned transaction rows
- **19,960** unique invoices
- **4,338** identified customers
- **£10,642,110.80** in retained positive sales-line revenue
- **695,838** directional association rules generated

The analysis includes monthly sales trends, top products by revenue, country-level sales, customer segments, and product association rules.

*Note: December 2011 contains partial-month data, and association rules should be interpreted with their support and confidence values.*

## Project Structure

```text
Customer Behavior & Market Basket Analysis System/
├── inspect_data.py
├── clean_data.py
├── sales_analysis.py
├── customer_analysis.py
├── market_basket.py
├── tests/
│   └── validate_outputs.py
├── outputs/
│   ├── reports/
│   └── figures/
├── README.md
└── .gitignore
```

The Power BI `.pbix` file should also be saved in the project folder.

## How to Run

1. Clone or download this repository.
2. Install the required Python packages.
3. Place the dataset in the expected input-data location.
4. Run the Python scripts in the appropriate order.
5. Open the generated reports and figures.
6. Open the Power BI `.pbix` file in Power BI Desktop.

Install commonly used packages with:

```bash
pip install pandas numpy matplotlib seaborn mlxtend openpyxl
```

Check the individual scripts for their expected input paths and execution order before running them.

## Dashboard

The Power BI dashboard presents sales performance, product trends, customer segments, and market basket association rules.

## Validation

The project output validation script completed successfully, confirming that the required reports and charts exist.

Run the validation script from the project root:

```bash
python tests/validate_outputs.py
```

## Future Improvements

- Add customer lifetime value analysis.
- Build customer retention and churn indicators.
- Improve association rule filtering and interpretation.
- Automate data refresh and dashboard updates.

## Author

Add your name and professional contact or portfolio links here.
