
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


SKILL_DIR = Path(__file__).resolve().parent.parent


def safe_percentage(numerator, denominator):
    """Calculate percentages safely when the denominator is zero."""
    if denominator == 0:
        return np.zeros(len(numerator), dtype=float)

    return numerator / denominator * 100


def validate_input_data(df):
    """Validate the columns required for profitability analysis."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("The dataset is empty.")

    required_columns = [
        "Product ID",
        "Product Name",
        "Division",
        "Sales",
        "Units",
        "Gross Profit",
        "Cost"
    ]

    missing = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}"
        )

    result = df.copy()

    numeric_columns = [
        "Sales",
        "Units",
        "Gross Profit",
        "Cost"
    ]

    for column in numeric_columns:
        result[column] = pd.to_numeric(
            result[column],
            errors="coerce"
        )

        values = result[column].to_numpy(dtype=float)

        if not np.isfinite(values).all():
            raise ValueError(
                f"Column '{column}' contains missing, invalid, "
                "or non-finite numerical values."
            )

    return result


def load_data(file_path):
    """Load a CSV file using an explicitly provided path."""
    path = Path(file_path).expanduser()

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Provided path is not a file: {path}")

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError("The CSV file contains no data.")

    for date_column in ["Order Date", "Ship Date"]:
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(
                df[date_column],
                errors="coerce",
                dayfirst=True
            )

    return validate_input_data(df)


def product_profitability(df):
    """Calculate profitability metrics for each product."""
    df = validate_input_data(df)

    product = (
        df.groupby(
            ["Product ID", "Product Name", "Division"],
            as_index=False
        )
        .agg(
            Sales=("Sales", "sum"),
            Units=("Units", "sum"),
            GrossProfit=("Gross Profit", "sum"),
            Cost=("Cost", "sum")
        )
    )

    product["GrossMargin"] = np.where(
        product["Sales"] > 0,
        product["GrossProfit"] / product["Sales"] * 100,
        0
    )

    product["ProfitPerUnit"] = np.where(
        product["Units"] > 0,
        product["GrossProfit"] / product["Units"],
        0
    )

    total_sales = product["Sales"].sum()
    total_profit = product["GrossProfit"].sum()

    product["RevenueContribution"] = safe_percentage(
        product["Sales"],
        total_sales
    )

    product["ProfitContribution"] = safe_percentage(
        product["GrossProfit"],
        total_profit
    )

    product["MarginRisk"] = np.select(
        [
            product["GrossMargin"] < 10,
            product["GrossMargin"] < 25
        ],
        [
            "High Risk",
            "Medium Risk"
        ],
        default="Low Risk"
    )

    return product


def division_profitability(df):
    """Calculate profitability metrics for each division."""
    df = validate_input_data(df)

    division = (
        df.groupby("Division", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Units=("Units", "sum"),
            GrossProfit=("Gross Profit", "sum"),
            Cost=("Cost", "sum"),
            Products=("Product ID", "nunique")
        )
    )

    division["GrossMargin"] = np.where(
        division["Sales"] > 0,
        division["GrossProfit"] / division["Sales"] * 100,
        0
    )

    division["ProfitPerUnit"] = np.where(
        division["Units"] > 0,
        division["GrossProfit"] / division["Units"],
        0
    )

    total_sales = division["Sales"].sum()
    total_profit = division["GrossProfit"].sum()

    division["RevenueContribution"] = safe_percentage(
        division["Sales"],
        total_sales
    )

    division["ProfitContribution"] = safe_percentage(
        division["GrossProfit"],
        total_profit
    )

    return division


def monthly_profitability(df):
    """Calculate monthly profitability when Order Date is available."""
    if "Order Date" not in df.columns:
        return pd.DataFrame(
            columns=[
                "Order Date", "Sales", "Cost",
                "GrossProfit", "Units",
                "GrossMargin", "ProfitPerUnit"
            ]
        )

    dated = df.dropna(subset=["Order Date"]).copy()

    if dated.empty:
        return pd.DataFrame(
            columns=[
                "Order Date", "Sales", "Cost",
                "GrossProfit", "Units",
                "GrossMargin", "ProfitPerUnit"
            ]
        )

    dated["Order Date"] = pd.to_datetime(
        dated["Order Date"],
        errors="coerce",
        dayfirst=True
    )

    dated = dated.dropna(subset=["Order Date"])

    monthly = (
        dated.groupby(
            dated["Order Date"].dt.to_period("M")
        )
        .agg(
            Sales=("Sales", "sum"),
            Cost=("Cost", "sum"),
            GrossProfit=("Gross Profit", "sum"),
            Units=("Units", "sum")
        )
        .reset_index()
    )

    monthly["Order Date"] = (
        monthly["Order Date"].dt.to_timestamp()
    )

    monthly["GrossMargin"] = np.where(
        monthly["Sales"] > 0,
        monthly["GrossProfit"] / monthly["Sales"] * 100,
        0
    )

    monthly["ProfitPerUnit"] = np.where(
        monthly["Units"] > 0,
        monthly["GrossProfit"] / monthly["Units"],
        0
    )

    return monthly


def margin_volatility(df):
    """Measure product margin variation across months."""
    if "Order Date" not in df.columns:
        return pd.DataFrame(
            columns=[
                "Product ID", "Product Name",
                "MarginVolatility", "AverageMargin"
            ]
        )

    dated = df.dropna(subset=["Order Date"]).copy()

    if dated.empty:
        return pd.DataFrame(
            columns=[
                "Product ID", "Product Name",
                "MarginVolatility", "AverageMargin"
            ]
        )

    dated["Order Date"] = pd.to_datetime(
        dated["Order Date"],
        errors="coerce",
        dayfirst=True
    )

    dated = dated.dropna(subset=["Order Date"])

    if dated.empty:
        return pd.DataFrame(
            columns=[
                "Product ID", "Product Name",
                "MarginVolatility", "AverageMargin"
            ]
        )

    monthly_product = (
        dated.groupby(
            [
                "Product ID",
                "Product Name",
                dated["Order Date"].dt.to_period("M")
            ]
        )
        .agg(
            Sales=("Sales", "sum"),
            GrossProfit=("Gross Profit", "sum")
        )
        .reset_index()
    )

    monthly_product["Margin"] = np.where(
        monthly_product["Sales"] > 0,
        monthly_product["GrossProfit"]
        / monthly_product["Sales"] * 100,
        0
    )

    volatility = (
        monthly_product.groupby(
            ["Product ID", "Product Name"],
            as_index=False
        )
        .agg(
            MarginVolatility=("Margin", "std"),
            AverageMargin=("Margin", "mean")
        )
    )

    volatility["MarginVolatility"] = (
        volatility["MarginVolatility"].fillna(0)
    )

    return volatility


def pareto_analysis(product_df):
    """Identify products contributing approximately 80% of sales/profit."""
    if product_df.empty:
        return {
            "revenue_sorted": product_df.copy(),
            "profit_sorted": product_df.copy(),
            "revenue_80_count": 0,
            "profit_80_count": 0,
            "revenue_80_percentage": 0,
            "profit_80_percentage": 0
        }

    revenue = product_df.sort_values(
        "Sales",
        ascending=False
    ).copy()

    total_revenue = revenue["Sales"].sum()

    if total_revenue != 0:
        revenue["CumulativeRevenue"] = (
            revenue["Sales"].cumsum() / total_revenue * 100
        )
    else:
        revenue["CumulativeRevenue"] = 0.0

    profit = product_df.sort_values(
        "GrossProfit",
        ascending=False
    ).copy()

    total_profit = profit["GrossProfit"].sum()

    if total_profit != 0:
        profit["CumulativeProfit"] = (
            profit["GrossProfit"].cumsum() / total_profit * 100
        )
    else:
        profit["CumulativeProfit"] = 0.0

    total_products = len(product_df)

    revenue_80 = (
        int((revenue["CumulativeRevenue"] <= 80).sum()) + 1
        if total_revenue != 0 else 0
    )

    profit_80 = (
        int((profit["CumulativeProfit"] <= 80).sum()) + 1
        if total_profit != 0 else 0
    )

    return {
        "revenue_sorted": revenue,
        "profit_sorted": profit,
        "revenue_80_count": min(revenue_80, total_products),
        "profit_80_count": min(profit_80, total_products),
        "revenue_80_percentage": (
            revenue_80 / total_products * 100
        ),
        "profit_80_percentage": (
            profit_80 / total_products * 100
        )
    }


def identify_margin_risks(product_df):
    """Classify products using margin, sales, and profit metrics."""
    risks = product_df.copy()

    if risks.empty:
        risks["PerformanceFlag"] = pd.Series(dtype="object")
        return risks

    median_margin = risks["GrossMargin"].median()
    median_sales = risks["Sales"].median()
    median_profit = risks["GrossProfit"].median()

    conditions = [
        (
            (risks["Sales"] >= median_sales) &
            (risks["GrossMargin"] < median_margin)
        ),
        (
            (risks["GrossMargin"] < 10) &
            (risks["GrossProfit"] < median_profit)
        ),
        (
            (risks["GrossMargin"] >= median_margin) &
            (risks["GrossProfit"] >= median_profit)
        )
    ]

    choices = [
        "High Sales - Low Margin",
        "Low Profit - Margin Risk",
        "High Performer"
    ]

    risks["PerformanceFlag"] = np.select(
        conditions,
        choices,
        default="Standard"
    )

    return risks


def generate_summary(df, product_df, division_df):
    """Generate an overall business profitability summary."""
    if df.empty or product_df.empty or division_df.empty:
        raise ValueError(
            "Cannot generate a summary from empty analysis results."
        )

    total_sales = df["Sales"].sum()
    total_cost = df["Cost"].sum()
    total_profit = df["Gross Profit"].sum()

    overall_margin = (
        total_profit / total_sales * 100
        if total_sales > 0 else 0
    )

    top_profit_product = product_df.loc[
        product_df["GrossProfit"].idxmax()
    ]

    top_margin_product = product_df.loc[
        product_df["GrossMargin"].idxmax()
    ]

    best_division = division_df.loc[
        division_df["GrossMargin"].idxmax()
    ]

    return {
        "total_sales": total_sales,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "overall_margin": overall_margin,
        "top_profit_product": top_profit_product["Product Name"],
        "top_profit_value": top_profit_product["GrossProfit"],
        "top_margin_product": top_margin_product["Product Name"],
        "top_margin_value": top_margin_product["GrossMargin"],
        "best_division": best_division["Division"],
        "best_division_margin": best_division["GrossMargin"]
    }


def main():
    parser = argparse.ArgumentParser(
        description="Nassau Candy profitability analysis."
    )

    parser.add_argument(
        "csv_file",
        help="Path to the input CSV dataset."
    )

    args = parser.parse_args()

    try:
        print("Loading dataset...")
        df = load_data(args.csv_file)

        print("Calculating product profitability...")
        product_df = product_profitability(df)

        print("Calculating division profitability...")
        division_df = division_profitability(df)

        print("Calculating monthly profitability...")
        monthly_df = monthly_profitability(df)

        print("Calculating margin volatility...")
        volatility_df = margin_volatility(df)

        if not volatility_df.empty:
            product_df = product_df.merge(
                volatility_df[
                    ["Product ID", "MarginVolatility"]
                ],
                on="Product ID",
                how="left"
            )
        else:
            product_df["MarginVolatility"] = 0.0

        product_df["MarginVolatility"] = (
            product_df["MarginVolatility"].fillna(0)
        )

        product_df = identify_margin_risks(product_df)

        pareto = pareto_analysis(product_df)

        summary = generate_summary(
            df,
            product_df,
            division_df
        )

        print("\n" + "=" * 60)
        print("NASSAU CANDY PROFITABILITY ANALYSIS")
        print("=" * 60)

        print("\nTotal Sales:")
        print(f"${summary['total_sales']:,.2f}")

        print("\nTotal Cost:")
        print(f"${summary['total_cost']:,.2f}")

        print("\nTotal Gross Profit:")
        print(f"${summary['total_profit']:,.2f}")

        print("\nOverall Gross Margin:")
        print(f"{summary['overall_margin']:.2f}%")

        print("\nTop Profit Product:")
        print(summary["top_profit_product"])
        print(f"${summary['top_profit_value']:,.2f}")

        print("\nHighest Margin Product:")
        print(summary["top_margin_product"])
        print(f"{summary['top_margin_value']:.2f}%")

        print("\nBest Margin Division:")
        print(summary["best_division"])
        print(f"{summary['best_division_margin']:.2f}%")

        print("\nProducts generating approximately 80% of revenue:")
        print(
            f"{pareto['revenue_80_count']} "
            f"({pareto['revenue_80_percentage']:.2f}%)"
        )

        print("\nProducts generating approximately 80% of profit:")
        print(
            f"{pareto['profit_80_count']} "
            f"({pareto['profit_80_percentage']:.2f}%)"
        )

        print("\nDivision Performance:")
        print(
            division_df[
                [
                    "Division",
                    "Sales",
                    "GrossProfit",
                    "GrossMargin",
                    "Products"
                ]
            ].to_string(index=False)
        )

        print("\nTop 10 Products by Gross Profit:")
        print(
            product_df
            .sort_values("GrossProfit", ascending=False)
            [
                [
                    "Product Name",
                    "Division",
                    "Sales",
                    "GrossProfit",
                    "GrossMargin"
                ]
            ]
            .head(10)
            .to_string(index=False)
        )

        print("\nMargin Risk Distribution:")
        print(
            product_df["MarginRisk"]
            .value_counts()
            .to_string()
        )

        if not monthly_df.empty:
            print("\nMonthly Profitability:")
            print(monthly_df.to_string(index=False))
        else:
            print(
                "\nMonthly analysis skipped: "
                "no valid Order Date values were available."
            )

        print("\nProfitability analysis completed successfully.")
        return 0

    except (
        FileNotFoundError,
        PermissionError,
        ValueError,
        pd.errors.ParserError
    ) as error:
        print(f"\nAnalysis error: {error}")
        return 1

    except Exception as error:
        print(f"\nUnexpected error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
