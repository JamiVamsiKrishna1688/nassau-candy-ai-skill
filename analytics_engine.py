
import numpy as np
import pandas as pd

from .preprocessing import clean_data
from .profitability import product_profitability


# ==========================================
# 1. COLUMN NORMALIZATION
# ==========================================

def normalize_columns(df):

    column_mapping = {
        "product id": "Product ID",
        "product": "Product Name",
        "product name": "Product Name",
        "division": "Division",
        "sales": "Sales",
        "revenue": "Sales",
        "units": "Units",
        "quantity": "Units",
        "gross profit": "Gross Profit",
        "grossprofit": "Gross Profit",
        "cost": "Cost",
        "total cost": "Cost"
    }

    df = df.copy()

    rename_mapping = {}

    for column in df.columns:

        cleaned_name = str(column).strip().lower()

        if cleaned_name in column_mapping:
            rename_mapping[column] = column_mapping[cleaned_name]

        else:
            rename_mapping[column] = str(column).strip()

    df = df.rename(columns=rename_mapping)

    # Prevent different input columns from becoming
    # duplicate standard column names.
    duplicate_columns = df.columns[
        df.columns.duplicated()
    ].tolist()

    if duplicate_columns:
        raise ValueError(
            "Duplicate columns detected after normalization: "
            f"{duplicate_columns}. "
            "Please ensure each required field appears only once."
        )

    return df


# ==========================================
# 2. REQUIRED COLUMN VALIDATION
# ==========================================

def validate_data(df):

    required_columns = [
        "Product ID",
        "Product Name",
        "Division",
        "Sales",
        "Units",
        "Gross Profit",
        "Cost"
    ]

    missing_columns = []

    for column in required_columns:

        if column not in df.columns:
            missing_columns.append(column)

    if missing_columns:

        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return True


# ==========================================
# 3. NUMERICAL DATA VALIDATION
# ==========================================

def check_numeric_columns(df):

    numeric_columns = [
        "Sales",
        "Units",
        "Cost",
        "Gross Profit"
    ]

    invalid_found = False

    for column in numeric_columns:

        if column in df.columns:

            converted = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            # Check missing numerical values.
            missing_values = df[column].isna()

            if missing_values.any():

                invalid_found = True

                print(f"\nMissing values found in {column}:")

                print(
                    df.loc[missing_values, column]
                )

            # Check invalid text or non-numeric values.
            invalid_values = (
                df[column].notna() & converted.isna()
            )

            if invalid_values.any():

                invalid_found = True

                print(f"\nInvalid values found in {column}:")

                print(
                    df.loc[invalid_values, column]
                )

            # Check positive and negative infinity.
            non_finite_values = (
                converted.notna() & ~np.isfinite(converted)
            )

            if non_finite_values.any():

                invalid_found = True

                print(
                    f"\nNon-finite numerical values found in {column}:"
                )

                print(
                    df.loc[non_finite_values, column]
                )

            # Check negative numerical values.
            negative_values = converted < 0

            if negative_values.any():

                invalid_found = True

                print(f"\nNegative values found in {column}:")

                print(
                    df.loc[negative_values, column]
                )

    if not invalid_found:

        print(
            "No missing, invalid, negative, or non-finite "
            "numerical values found."
        )

    return not invalid_found


# ==========================================
# 4. MAIN ANALYTICS ENGINE
# ==========================================

def analyze_data(df):

    df = normalize_columns(df)

    validate_data(df)

    if not check_numeric_columns(df):

        raise ValueError(
            "Invalid numerical data found. "
            "Please correct missing, non-numeric, negative, "
            "or non-finite values in the CSV and try again."
        )

    cleaned_data = clean_data(df)

    # Stop if preprocessing removes every row.
    if cleaned_data.empty:

        raise ValueError(
            "No valid data remains after preprocessing. "
            "Check the Sales, Units, Cost, and date values "
            "in your CSV file."
        )

    product_results = product_profitability(cleaned_data)

    if product_results.empty:

        raise ValueError(
            "No product profitability results could be generated."
        )

    return product_results


# ==========================================
# 5. MISSING VALUE CHECK
# ==========================================

def check_missing_values(df):

    missing_values = df.isnull().sum()

    missing_values = missing_values[
        missing_values > 0
    ]

    if missing_values.empty:

        print("No missing values found!")

    else:

        print("Missing values found:")
        print(missing_values)

    return missing_values


# ==========================================
# 6. COMPLETE DATA QUALITY REPORT
# ==========================================

def check_data_quality(df):

    print("\n--- DATA QUALITY REPORT ---")

    print("\n1. Checking required columns:")

    df = normalize_columns(df)

    validate_data(df)

    print("All required columns are present.")

    print("\n2. Checking missing values:")

    check_missing_values(df)

    print("\n3. Checking invalid numeric values:")

    numeric_data_valid = check_numeric_columns(df)

    if not numeric_data_valid:

        print(
            "\nData quality warning: "
            "Missing, invalid, negative, or non-finite "
            "numerical values detected."
        )

    print("\nData quality checks completed.")

    return numeric_data_valid


# ==========================================
# 7. BUSINESS INSIGHTS
# ==========================================

def generate_business_insights(results):

    print("\n========== BUSINESS INSIGHTS ==========")

    if results.empty:

        print("No product results are available for analysis.")
        print("=======================================")
        return

    best_product = results.loc[
        results["GrossProfit"].idxmax()
    ]

    lowest_product = results.loc[
        results["GrossProfit"].idxmin()
    ]

    highest_margin = results.loc[
        results["GrossMargin"].idxmax()
    ]

    high_risk_products = results[
        results["MarginRisk"] == "High Risk"
    ]

    print("\nMost profitable product:")
    print(best_product["Product Name"])

    print("\nLowest gross profit product:")
    print(lowest_product["Product Name"])

    print("\nHighest margin product:")
    print(highest_margin["Product Name"])

    print("\nHigh-risk products:")

    if high_risk_products.empty:

        print("No high-risk products found.")

    else:

        print(
            high_risk_products["Product Name"].to_string(
                index=False
            )
        )

    print("\n=======================================")


# ==========================================
# 8. BUSINESS RECOMMENDATIONS
# ==========================================

def generate_recommendations(results):

    print("\n========== BUSINESS RECOMMENDATIONS ==========")

    if results.empty:

        print("No product results are available for recommendations.")
        print("==============================================")
        return

    for _, product in results.iterrows():

        name = product["Product Name"]
        margin = product["GrossMargin"]
        risk = product["MarginRisk"]

        if risk == "High Risk":

            print(f"\n{name}:")
            print("Action: Review product pricing and production costs.")
            print(f"Current gross margin: {margin:.2f}%")

        elif margin < 25:

            print(f"\n{name}:")
            print("Action: Investigate costs and improve the profit margin.")
            print(f"Current gross margin: {margin:.2f}%")

        elif margin >= 70:

            print(f"\n{name}:")
            print("Action: Consider opportunities to increase sales.")
            print(f"Current gross margin: {margin:.2f}%")

    print("\n==============================================")


# ==========================================
# 9. BASIC BUSINESS QUESTION ANSWERING
# ==========================================

def answer_business_question(results, question):

    if results.empty:
        return "No product results are available to answer this question."

    question = question.lower().strip()

    if (
        "highest profit" in question
        or "most profitable" in question
    ):

        product = results.loc[
            results["GrossProfit"].idxmax()
        ]

        return (
            f"{product['Product Name']} generates the highest "
            f"gross profit: {product['GrossProfit']:.2f}"
        )

    elif "lowest profit" in question:

        product = results.loc[
            results["GrossProfit"].idxmin()
        ]

        return (
            f"{product['Product Name']} has the lowest "
            f"gross profit: {product['GrossProfit']:.2f}"
        )

    elif "highest margin" in question:

        product = results.loc[
            results["GrossMargin"].idxmax()
        ]

        return (
            f"{product['Product Name']} has the highest "
            f"gross margin: {product['GrossMargin']:.2f}%"
        )

    elif "high risk" in question:

        high_risk = results[
            results["MarginRisk"] == "High Risk"
        ]

        return (
            f"Number of high-risk products: {len(high_risk)}. "
            f"Products: {', '.join(high_risk['Product Name'].tolist())}"
        )

    else:

        return "Sorry, I cannot answer that question yet."


# ==========================================
# 10. ADVANCED BUSINESS QUESTION ANSWERING
# ==========================================

def answer_advanced_question(results, question):

    if results.empty:
        return "No product results are available to answer this question."

    question = question.lower().strip()

    if (
        "total sales" in question
        or "total revenue" in question
    ):

        total_sales = results["Sales"].sum()

        return f"Total sales revenue: {total_sales:,.2f}"

    elif "total gross profit" in question:

        total_profit = results["GrossProfit"].sum()

        return f"Total gross profit: {total_profit:,.2f}"

    elif (
        "average margin" in question
        or "average gross margin" in question
    ):

        average_margin = results["GrossMargin"].mean()

        return f"Average gross margin: {average_margin:.2f}%"

    elif (
        "how many products" in question
        or "number of products" in question
    ):

        total_products = len(results)

        return f"Total number of products: {total_products}"

    elif "high risk" in question:

        high_risk = results[
            results["MarginRisk"] == "High Risk"
        ]

        if high_risk.empty:
            return "There are no high-risk products."

        names = ", ".join(
            high_risk["Product Name"].tolist()
        )

        return f"High-risk products: {names}"

    else:

        return "Sorry, I cannot answer that question yet."


# ==========================================
# 11. STRUCTURED BUSINESS SUMMARY
# ==========================================

def get_structured_summary(results):

    if results.empty:

        raise ValueError(
            "Cannot generate a business summary because "
            "there are no product results."
        )

    summary = {

        "total_products": int(len(results)),

        "total_sales": float(
            round(results["Sales"].sum(), 2)
        ),

        "total_gross_profit": float(
            round(results["GrossProfit"].sum(), 2)
        ),

        "average_gross_margin": float(
            round(results["GrossMargin"].mean(), 2)
        ),

        "high_risk_products": results[
            results["MarginRisk"] == "High Risk"
        ]["Product Name"].tolist()

    }

    return summary
