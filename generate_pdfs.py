#!/usr/bin/env python3
"""
PDF Report Generator CLI
Generate PDF reports from existing markdown reports.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.utils.pdf_generator import generate_pdf_reports


def find_latest_analysis(symbol: str, results_dir: str = "./results") -> Optional[str]:
    """Find the latest analysis date for a given symbol."""
    symbol_dir = os.path.join(results_dir, symbol)
    if not os.path.exists(symbol_dir):
        return None

    dates = [d for d in os.listdir(symbol_dir) if os.path.isdir(os.path.join(symbol_dir, d))]
    if not dates:
        return None

    # Sort dates and return the latest
    dates.sort(reverse=True)
    return dates[0]


def list_available_analyses(results_dir: str = "./results") -> dict:
    """List all available analyses."""
    analyses = {}

    if not os.path.exists(results_dir):
        return analyses

    for symbol in os.listdir(results_dir):
        symbol_path = os.path.join(results_dir, symbol)
        if os.path.isdir(symbol_path):
            dates = [
                d
                for d in os.listdir(symbol_path)
                if os.path.isdir(os.path.join(symbol_path, d))
            ]
            if dates:
                dates.sort(reverse=True)
                analyses[symbol] = dates

    return analyses


def main():
    parser = argparse.ArgumentParser(
        description="Generate PDF reports from TradingAgents markdown reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_pdfs.py --symbol NVDA --date 2025-07-24
  python generate_pdfs.py --symbol NVDA --latest
  python generate_pdfs.py --list
  python generate_pdfs.py --all
        """
    )

    parser.add_argument(
        "--symbol", "-s",
        help="Stock symbol (e.g., NVDA, AAPL)"
    )

    parser.add_argument(
        "--date", "-d",
        help="Analysis date (YYYY-MM-DD format)"
    )

    parser.add_argument(
        "--latest", "-l",
        action="store_true",
        help="Use the latest analysis for the symbol"
    )

    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Generate PDFs for all available analyses"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available analyses"
    )

    parser.add_argument(
        "--results-dir", "-r",
        default="./results",
        help="Results directory (default: ./results)"
    )

    args = parser.parse_args()

    # List available analyses
    if args.list:
        analyses = list_available_analyses(args.results_dir)
        if not analyses:
            print("No analyses found.")
            return 0

        print("Available analyses:")
        print("=" * 50)
        for symbol, dates in analyses.items():
            print(f"\n{symbol}:")
            for date in dates:
                reports_dir = os.path.join(args.results_dir, symbol, date, "reports")
                if os.path.exists(reports_dir):
                    report_count = len([
                        f for f in os.listdir(reports_dir)
                        if f.endswith('.md')
                    ])
                    print(f"  {date} ({report_count} reports)")
        return 0

    # Generate PDFs for all analyses
    if args.all:
        analyses = list_available_analyses(args.results_dir)
        if not analyses:
            print("No analyses found.")
            return 0

        total_generated = 0
        for symbol, dates in analyses.items():
            print(f"\nProcessing {symbol}...")
            for date in dates:
                try:
                    result = generate_pdf_reports(symbol, date, args.results_dir)
                    if isinstance(result, dict) and "error" in result:
                        print(f"  {date}: Error: {result['error']}")
                    else:
                        print(f"  {date}: PDFs generated successfully")
                        total_generated += 1
                except Exception as e:
                    print(f"  {date}: Error: {e}")

        print(f"\nGenerated PDFs for {total_generated} analyses!")
        return 0

    # Generate PDF for specific symbol and date
    if not args.symbol:
        print("Symbol is required. Use --symbol or --all")
        return 1

    # Determine the date
    if args.latest:
        date = find_latest_analysis(args.symbol, args.results_dir)
        if not date:
            print(f"No analyses found for {args.symbol}")
            return 1
        print(f"Using latest analysis: {date}")
    elif args.date:
        date = args.date
    else:
        print("Date is required. Use --date or --latest")
        return 1

    # Check if reports exist
    reports_dir = os.path.join(args.results_dir, args.symbol, date, "reports")
    if not os.path.exists(reports_dir):
        print(f"Reports not found: {reports_dir}")
        return 1

    # Generate PDFs
    print(f"Generating PDF reports for {args.symbol} ({date})...")

    try:
        result = generate_pdf_reports(args.symbol, date, args.results_dir)

        if isinstance(result, dict) and "error" in result:
            print(f"Error: {result['error']}")
            return 1

        output_dir = result.get("output_dir", "")
        full_report = result.get("full_report", "")
        summary = result.get("summary", "")

        print("PDF reports generated successfully!")
        if output_dir:
            print(f"Output directory: {output_dir}")
        if full_report:
            print(f"Full report: {os.path.basename(full_report)}")
        if summary:
            print(f"Summary: {os.path.basename(summary)}")

        return 0

    except Exception as e:
        print(f"Failed to generate PDFs: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
