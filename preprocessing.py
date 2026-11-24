
import sys
from pathlib import Path

import numpy as np
import pandas as pd


SKILL_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = SKILL_DIR / "outputs"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "cleaned_data.csv"


def load_data(file_path):

    csv_path = Path(file_path).expanduser()

    if not csv_path.is_file():
        raise FileNotFoundError(
            f"CSV file not found: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    if len(df.columns) == 0:
        raise ValueError("The CSV file has no columns.")

    if df.empty:
        raise ValueError(
            "The CSV file contains headers but no data rows."
        )

    return df


def clean_data(df):

    if df is None:
        raise ValueError("No dataset was provided.")

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Input must be a pandas DataFrame."
        )

    if df.empty:
        raise ValueError(
            "Cannot preprocess an empty dataset."
        )

    df = df.copy()

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # Required columns
    required_columns = [
        "Division",
        "Product ID",
        "Product Name",
        "Sales",
        "Units",
        "Gross Profit",
        "Cost"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Validate required text fields
    text_columns = [
        "Division",
        "Product ID",
        "Product Name"
    ]

    for column in text_columns:

        missing_mask = (
            df[column].isna()
            | df[column].astype(str).str.strip().eq("")
        )

        if missing_mask.any():
            raise ValueError(
                f"Missing values found in required column "
                f"'{column}'. Please correct these rows."
            )

    # Optional date processing
    date_columns = [
        "Order Date",
        "Ship Date"
    ]

    for column in date_columns:

        if column in df.columns:

            original_values = df[column].copy()

            df[column] = pd.to_datetime(
                df[column],
                errors="coerce",
                dayfirst=True
            )

            invalid_mask = (
                original_values.notna()
                & df[column].isna()
            )

            if invalid_mask.any():
                print(
                    f"Warning: {invalid_mask.sum()} invalid "
                    f"date value(s) found in {column}. "
                    "Rows are preserved."
                )

    # Only financial and transactional measures
    # are converted and strictly validated.
    numeric_columns = [
        "Sales",
        "Units",
        "Gross Profit",
        "Cost"
    ]

    for column in numeric_columns:

        converted = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        invalid_mask = (
            df[column].notna()
            & converted.isna()
        )

        if invalid_mask.any():
            raise ValueError(
                f"Non-numeric values found in '{column}'. "
                "Please correct the CSV before analysis."
            )

        if converted.isna().any():
            raise ValueError(
                f"Missing numerical values found in '{column}'."
            )

        if not np.isfinite(
            converted.to_numpy(dtype=float)
        ).all():
            raise ValueError(
                f"Non-finite numerical values found in '{column}'."
            )

        if (converted < 0).any():
            raise ValueError(
                f"Negative numerical values found in '{column}'."
            )

        df[column] = converted

    # Preserve duplicate rows
    original_row_count = len(df)
    duplicate_count = int(df.duplicated().sum())

    if duplicate_count:
        print(
            f"Notice: {duplicate_count} duplicate row(s) "
            "detected. They have been preserved."
        )

    # Recalculate gross profit
    df["Gross Profit"] = (
        df["Sales"] - df["Cost"]
    )

    # Profitability calculations
    df["Gross Margin"] = np.where(
        df["Sales"] > 0,
        df["Gross Profit"] / df["Sales"] * 100,
        0
    )

    df["Profit per Unit"] = np.where(
        df["Units"] > 0,
        df["Gross Profit"] / df["Units"],
        0
    )

    df["Cost per Unit"] = np.where(
        df["Units"] > 0,
        df["Cost"] / df["Units"],
        0
    )

    # Date-based features
    if "Order Date" in df.columns:

        df["Order Year"] = df["Order Date"].dt.year
        df["Order Month"] = df["Order Date"].dt.month
        df["Order Quarter"] = df["Order Date"].dt.quarter
        df["Order Month Name"] = (
            df["Order Date"].dt.month_name()
        )

    # Shipping features
    if (
        "Order Date" in df.columns
        and "Ship Date" in df.columns
    ):

        df["Shipping Days"] = (
            df["Ship Date"] - df["Order Date"]
        ).dt.days.clip(lower=0)

        df["Shipping Delay Flag"] = (
            df["Shipping Days"] > 7
        ).astype(int)

    # Revenue contribution
    total_sales = df["Sales"].sum()

    if total_sales > 0:
        df["Revenue Contribution"] = (
            df["Sales"] / total_sales * 100
        )
    else:
        df["Revenue Contribution"] = 0.0

    # Profit contribution
    total_profit = df["Gross Profit"].sum()

    if total_profit != 0:
        df["Profit Contribution"] = (
            df["Gross Profit"] / total_profit * 100
        )
    else:
        df["Profit Contribution"] = 0.0

    # Margin risk
    df["Margin Risk"] = np.select(
        [
            df["Gross Margin"] < 10,
            df["Gross Margin"] < 25
        ],
        [
            "High Risk",
            "Medium Risk"
        ],
        default="Low Risk"
    )

    print("\n========== PREPROCESSING SUMMARY ==========")
    print("Original rows:", original_row_count)
    print("Processed rows:", len(df))
    print("Rows removed:", original_row_count - len(df))
    print("Duplicate rows preserved:", duplicate_count)
    print("============================================")

    return df


def save_processed_data(
    df,
    output_path=DEFAULT_OUTPUT_PATH
):

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "A valid pandas DataFrame is required."
        )

    if df.empty:
        raise ValueError(
            "Cannot save an empty processed dataset."
        )

    destination = Path(output_path).expanduser().resolve()

    try:
        destination.relative_to(
            SKILL_DIR.resolve()
        )
    except ValueError:
        raise ValueError(
            "Output files must be saved inside the skill directory."
        )

    if destination == SKILL_DIR.resolve():
        raise ValueError(
            "The output path must identify a file."
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(destination, index=False)

    print(f"\nProcessed dataset saved: {destination}")

    return destination


def main():

    if len(sys.argv) < 2:
        print(
            "Usage: python -m scripts.preprocessing <csv_file>"
        )
        return

    try:

        print("Loading dataset...")

        raw_df = load_data(sys.argv[1])

        print("Original shape:", raw_df.shape)

        cleaned_df = clean_data(raw_df)

        print("Processed shape:", cleaned_df.shape)

        print("\nMissing values:")
        print(cleaned_df.isnull().sum().sum())

        print("\nDuplicate rows:")
        print(cleaned_df.duplicated().sum())

        print("\nDivisions:")
        print(cleaned_df["Division"].value_counts())

        print("\nMargin Risk:")
        print(cleaned_df["Margin Risk"].value_counts())

        print("\nTotal Sales:")
        print(round(cleaned_df["Sales"].sum(), 2))

        print("\nTotal Cost:")
        print(round(cleaned_df["Cost"].sum(), 2))

        print("\nTotal Gross Profit:")
        print(round(cleaned_df["Gross Profit"].sum(), 2))

        total_sales = cleaned_df["Sales"].sum()

        overall_margin = (
            cleaned_df["Gross Profit"].sum() / total_sales * 100
            if total_sales > 0
            else 0
        )

        print("\nOverall Gross Margin:")
        print(round(overall_margin, 2), "%")

        save_processed_data(cleaned_df)

        print("\nPreprocessing completed successfully.")

    except FileNotFoundError as error:
        print(f"File error: {error}")

    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")

    except (ValueError, TypeError) as error:
        print(f"Data processing error: {error}")

    except Exception as error:
        print(f"Unexpected processing error: {error}")


if __name__ == "__main__":
    main()
