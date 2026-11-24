# Nassau Candy Analytics

A Python-powered business analytics skill that helps AI agents analyze sales data, evaluate product profitability, identify margin risks, and generate structured business reports.

## Features

- Product-level profitability analysis
- Sales revenue and gross profit calculations
- Gross margin analysis
- Identification of high- and low-profit products
- High-risk product identification
- Data validation and error handling
- Business insights and recommendations
- CSV and JSON report generation
- Answers to supported business questions

## Requirements

- Python
- Dependencies listed in `requirements.txt`

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Project Structure

```text
nassau-candy-analytics/
├── SKILL.md
├── README.md
├── requirements.txt
├── scripts/
│   ├── __init__.py
│   ├── analytics_engine.py
│   ├── preprocessing.py
│   ├── profitability.py
│   └── run_analysis.py
├── test_data/
│   └── Sample CSV datasets
└── outputs/
    └── Generated reports
```

## Input Data

Provide a sales dataset in CSV format.

The required columns are:

- Product ID
- Product Name
- Division
- Sales
- Units
- Gross Profit
- Cost

The analytics engine also supports alternative column names such as Revenue, Quantity, Total Cost, and Product.

Additional columns are allowed. Order Date and Ship Date are optional.

## Run the Analysis

From the skill directory, execute:

```bash
python -m scripts.run_analysis "test_data/Nassau Candy Distributor.csv"
```

You can replace the sample filename with another CSV file.

## Generated Reports

The analysis generates:

| Report | Description |
|---|---|
| `product_profitability_report.csv` | Product-level profitability results |
| `product_profitability_report.json` | Structured product-level results |
| `business_summary.json` | Overall business performance summary |

Reports are saved in the `outputs/` directory.

## Data Validation

The analytics engine checks for:

- Missing required columns
- Missing numerical values
- Invalid numerical values
- Negative numerical values
- Empty CSV files
- Unexpected processing errors

Invalid datasets are rejected with an explanatory error.

The original input CSV is preserved.

## Limitations

- Business questions are limited to the capabilities implemented in the current analytics engine.
- Recommendations are based on calculated metrics and are not guaranteed business outcomes.
- Forecasting, customer profitability, and interactive dashboards are not included in the current skill version.
- Compatibility with individual AI-agent execution environments must be tested separately.

## License and Usage

Review the applicable project license and usage permissions before redistributing or commercializing this skill.