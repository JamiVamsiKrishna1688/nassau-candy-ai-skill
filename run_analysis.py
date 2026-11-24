
import sys
import json
from pathlib import Path

import pandas as pd

from .analytics_engine import (
    analyze_data,
    generate_business_insights,
    generate_recommendations,
    answer_business_question,
    answer_advanced_question,
    get_structured_summary
)


# Find the main skill folder
SKILL_DIR = Path(__file__).resolve().parent.parent

# Create the outputs folder path
OUTPUT_DIR = SKILL_DIR / "outputs"


def load_csv(csv_file):
    """Load a CSV file and check that it contains usable data."""

    csv_path = Path(csv_file).expanduser()

    if not csv_path.exists():
        raise FileNotFoundError("CSV file not found.")

    if not csv_path.is_file():
        raise ValueError("The supplied path is not a file.")

    df = pd.read_csv(csv_path)

    if len(df.columns) == 0:
        raise ValueError("The CSV file has no columns.")

    if df.empty:
        raise ValueError("The CSV file has headers but no data rows.")

    return df


def save_reports(results, summary):
    """Save analysis reports inside the skill's outputs folder."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save business summary as JSON
    summary_file = OUTPUT_DIR / "business_summary.json"

    with summary_file.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4, allow_nan=False)

    print(f"\nBusiness summary saved: {summary_file}")

    # Export product profitability as CSV
    csv_report = OUTPUT_DIR / "product_profitability_report.csv"

    results.to_csv(csv_report, index=False)

    print(f"CSV report saved: {csv_report}")

    # Export product profitability as JSON
    json_report = OUTPUT_DIR / "product_profitability_report.json"

    results.to_json(
        json_report,
        orient="records",
        indent=4
    )

    print(f"JSON report saved: {json_report}")


def run_interactive_questions(results):
    """Allow a user to ask business questions interactively."""

    print("\n========== ASK YOUR BUSINESS QUESTION ==========")
    print("Type 'exit' to finish question-answering mode.")

    while True:
        try:
            question = input("\nAsk a question: ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nExiting question-answering mode.")
            break

        if question.lower() == "exit":
            print("Exiting question-answering mode.")
            break

        if not question:
            print("Please enter a question.")
            continue

        answer = answer_business_question(results, question)

        if answer == "Sorry, I cannot answer that question yet.":
            answer = answer_advanced_question(results, question)

        print("\nAnswer:", answer)


def main():

    # Check command-line arguments
    if len(sys.argv) < 2:
        print(
            "Usage: python -m scripts.run_analysis "
            "<csv_file> [--interactive]"
        )
        return 1

    csv_file = sys.argv[1]

    # Interactive mode is optional
    interactive_mode = "--interactive" in sys.argv[2:]

    # Reject unsupported command-line arguments
    unsupported_arguments = [
        argument
        for argument in sys.argv[2:]
        if argument != "--interactive"
    ]

    if unsupported_arguments:
        print(
            "Error: Unsupported arguments:",
            ", ".join(unsupported_arguments)
        )
        return 1

    # Load and analyze CSV data
    try:
        print("Loading CSV dataset...")

        df = load_csv(csv_file)

        print(f"Loaded {len(df)} rows and {len(df.columns)} columns.")

        print("\nRunning data validation and analysis...")

        results = analyze_data(df)

        if results.empty:
            raise ValueError(
                "Analysis produced no product profitability results."
            )

    except FileNotFoundError as error:
        print(f"Error: {error}")
        return 1

    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
        return 1

    except pd.errors.ParserError as error:
        print(f"Error: Unable to parse the CSV file: {error}")
        return 1

    except PermissionError:
        print("Error: Permission denied while reading the CSV file.")
        return 1

    except ValueError as error:
        print(f"Data validation error: {error}")
        return 1

    except Exception as error:
        print(f"Unexpected error: {error}")
        return 1

    # Generate structured business summary
    summary = get_structured_summary(results)

    print("\n========== STRUCTURED BUSINESS SUMMARY ==========")
    print(json.dumps(summary, indent=4))

    # Generate business insights
    generate_business_insights(results)

    # Generate business recommendations
    generate_recommendations(results)

    # Display product profitability results
    print("\n========== PRODUCT PROFITABILITY RESULTS ==========")
    print(results.to_string(index=False))

    # Save all reports before optional interactive mode
    try:
        save_reports(results, summary)

    except (OSError, ValueError) as error:
        print(f"Error while saving reports: {error}")
        return 1

    print("\nAnalysis completed successfully.")

    # Interactive questions only when explicitly requested
    if interactive_mode:
        run_interactive_questions(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
