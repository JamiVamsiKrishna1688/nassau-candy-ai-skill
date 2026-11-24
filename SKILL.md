---
name: nassau-candy-analytics
description: Use when the user asks to analyze business sales CSV files, calculate product profitability or gross margins, identify high-risk or low-margin products, generate sales performance reports, or answer questions about revenue and gross profit.
---

# Nassau Candy Analytics

## 1. Purpose

This skill helps users analyze business sales data and understand product profitability, revenue performance, gross margins, and potential financial risks.

It uses Python-based data processing and analytics to generate structured business reports and explain important findings in simple language.

## 2. Capabilities

- Analyze product-level profitability.
- Calculate sales revenue and gross profit.
- Calculate gross margins and profit per unit.
- Calculate revenue and profit contributions.
- Identify the most and least profitable products.
- Identify products with low profit margins.
- Classify products based on margin risk.
- Detect missing, invalid, and negative numerical values.
- Generate business insights and recommendations.
- Answer supported business questions.
- Generate CSV and JSON reports.
- Generate a structured business summary.

## 3. Input Requirements

Ask the user to provide a business sales dataset in CSV format.

The dataset must contain the following information:

| Required field | Description |
|---|---|
| Product ID | Unique product identifier |
| Product Name | Name of the product |
| Division | Business division |
| Sales | Sales revenue |
| Units | Number of units sold |
| Gross Profit | Gross profit |
| Cost | Product cost |

### Supported Alternative Column Names

The analytics engine supports these alternative names:

| Alternative name | Standard name |
|---|---|
| Revenue | Sales |
| Quantity | Units |
| Total Cost | Cost |
| Product | Product Name |

Column names are normalized to handle capitalization differences and extra spaces.

Additional columns are allowed.

Order Date and Ship Date are optional. When supplied, date and shipping-related features can be calculated.

## 4. Data Validation

Before performing analysis:

1. Inspect the uploaded CSV file.
2. Normalize column names.
3. Verify that all required columns are present.
4. Check numerical columns for missing values.
5. Detect non-numeric values in numerical columns.
6. Detect negative values in Sales, Units, Cost, and Gross Profit.
7. Stop the analysis if validation fails.
8. Explain validation errors clearly to the user.

Never invent missing financial values or silently replace invalid input values.

Zero values are allowed by numerical validation. However, the preprocessing pipeline filters out rows where Sales or Units are not greater than zero.

## 5. Analytics Processing

Use the Python analytics modules included in the skill.

Main modules:

- `scripts/preprocessing.py`
- `scripts/profitability.py`
- `scripts/analytics_engine.py`
- `scripts/run_analysis.py`

The analytics workflow is:

1. Read the input CSV.
2. Normalize column names.
3. Validate required columns.
4. Validate numerical data.
5. Clean and preprocess the dataset.
6. Calculate product profitability.
7. Generate business insights.
8. Generate recommendations.
9. Generate structured summaries.
10. Export reports.

Execute the available Python scripts using the execution environment provided by the host agent.

If dependencies are not installed, explain which dependencies are required using `requirements.txt`. Do not install packages or modify system configurations without authorization.

Do not claim that an analysis was executed unless the execution environment confirms successful completion.

## 6. Business Insights

Explain important findings, including:

- Most profitable product.
- Product with the lowest gross profit.
- Product with the highest gross margin.
- Products classified as high risk.

Use actual calculated results from the uploaded dataset.

## 7. Business Recommendations

Provide recommendations based on calculated results.

Examples:

- High-risk products: Review pricing and production costs.
- Products with gross margins below 25%: Investigate costs and opportunities to improve profitability.
- Products with gross margins of 70% or higher: Consider opportunities to increase sales.

These recommendations are indicators for further business investigation, not guaranteed outcomes.

Clearly distinguish calculated findings from recommendations.

## 8. Business Question Answering

The current analytics engine supports questions about:

- Highest profit or most profitable product.
- Lowest gross profit product.
- Highest gross margin product.
- Total sales or total revenue.
- Total gross profit.
- Average gross margin.
- Number of products.
- High-risk products.

If a question is not supported, clearly explain that the current version cannot answer it.

Do not invent answers.

## 9. Report Generation

The current system generates these reports:

### CSV Report

`product_profitability_report.csv`

Contains product-level profitability calculations.

### JSON Report

`product_profitability_report.json`

Contains structured product-level analytics results.

### Business Summary

`business_summary.json`

Contains:

- Total number of products.
- Total sales.
- Total gross profit.
- Average gross margin.
- High-risk products.

Only report successful file generation when the files have actually been created.

## 10. Error Handling

Handle common errors clearly:

- Missing CSV file.
- Empty CSV file.
- CSV containing headers but no data rows.
- Missing required columns.
- Missing numerical values.
- Invalid numerical values.
- Negative numerical values.
- Unexpected processing errors.

When an error occurs:

1. Explain what went wrong.
2. Identify the affected column or input when possible.
3. Explain how the user can correct the dataset.
4. Do not present incomplete analysis as a successful result.

## 11. Output Format

Present completed analyses using the following structure:

### A. Analysis Status

State whether the analysis completed successfully or was stopped because of validation errors.

### B. Business Summary

Present:

- Total number of products.
- Total sales.
- Total gross profit.
- Average gross margin.
- Number and names of high-risk products.

### C. Product Profitability

Present the most profitable product, lowest gross profit product, highest margin product, and relevant product-level findings.

### D. Business Insights

Explain the important findings in simple language using actual calculated values.

### E. Recommendations

Provide practical recommendations based on the results. Clearly identify them as suggestions rather than guaranteed outcomes.

### F. Generated Reports

List the actual report files created and their locations.

If a section cannot be calculated, explain why instead of inventing information.

## 12. Important Rules

- Never fabricate financial data.
- Never silently change the user's original dataset.
- Never hide validation errors.
- Do not claim unsupported analytics capabilities.
- Distinguish calculated facts from business recommendations.
- Explain technical results in simple language.
- Preserve the original input data.
- Use the actual generated reports as the source for reported results.
- Do not claim successful execution or file generation without confirmation.
- Do not expose sensitive information contained in uploaded datasets unnecessarily.

## 13. Future Improvements

Potential future capabilities include:

- Time-based sales analysis.
- Customer profitability analysis.
- Division-level performance analysis.
- Sales forecasting.
- Product segmentation.
- More advanced natural-language business questions.
- Interactive business dashboards.