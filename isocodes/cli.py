#!/usr/bin/env python3
"""
CLI for isocodes - Command line interface for ISO standard data lookup.

This CLI provides access to various ISO standards including:
- Countries (ISO 3166-1)
- Languages (ISO 639-2, 639-3, 639-5)
- Currencies (ISO 4217)
- Country subdivisions (ISO 3166-2)
- Former countries (ISO 3166-3)
- Script names (ISO 15924)
"""

import argparse
import json
import sys
from typing import Any, List, Optional

from . import (
    countries,
    currencies,
    former_countries,
    languages,
    script_names,
    subdivisions_countries,
)


def format_output(
    data: Any, output_format: str = "table", fields: Optional[List[str]] = None
) -> str:
    """Format output data based on the specified format."""
    if not data:
        return "No results found."

    if output_format == "json":
        if isinstance(data, list):
            return json.dumps(
                [dict(item) for item in data], indent=2, ensure_ascii=False
            )
        else:
            return json.dumps(dict(data), indent=2, ensure_ascii=False)

    elif output_format == "csv":
        if isinstance(data, list):
            if not data:
                return ""

            # Get all unique keys from all items
            all_keys = set()
            for item in data:
                all_keys.update(item.keys())

            if fields:
                headers = [key for key in fields if key in all_keys]
            else:
                headers = sorted(all_keys)

            lines = [",".join(headers)]
            for item in data:
                values = []
                for header in headers:
                    value = str(item.get(header, "")).replace(",", ";")
                    values.append(value)
                lines.append(",".join(values))
            return "\n".join(lines)
        else:
            if fields:
                headers = [key for key in fields if key in data.keys()]
            else:
                headers = sorted(data.keys())

            lines = [",".join(headers)]
            values = []
            for header in headers:
                value = str(data.get(header, "")).replace(",", ";")
                values.append(value)
            lines.append(",".join(values))
            return "\n".join(lines)

    else:  # table format
        if isinstance(data, list):
            if not data:
                return "No results found."

            # Get all unique keys from all items
            all_keys = set()
            for item in data:
                all_keys.update(item.keys())

            if fields:
                headers = [key for key in fields if key in all_keys]
            else:
                headers = sorted(all_keys)

            # Calculate column widths
            col_widths = {}
            for header in headers:
                col_widths[header] = len(header)
                for item in data:
                    value_len = len(str(item.get(header, "")))
                    col_widths[header] = max(col_widths[header], value_len)

            # Format table
            lines = []
            # Header
            header_line = " | ".join(h.ljust(col_widths[h]) for h in headers)
            lines.append(header_line)
            lines.append("-" * len(header_line))

            # Data rows
            for item in data:
                row = " | ".join(
                    str(item.get(h, "")).ljust(col_widths[h]) for h in headers
                )
                lines.append(row)

            return "\n".join(lines)
        else:
            # Single item table
            if fields:
                headers = [key for key in fields if key in data.keys()]
            else:
                headers = sorted(data.keys())

            max_key_len = max(len(h) for h in headers) if headers else 0
            lines = []
            for key in headers:
                value = str(data.get(key, ""))
                lines.append(f"{key.ljust(max_key_len)} : {value}")
            return "\n".join(lines)


def search_countries(args) -> None:
    """Search countries by various criteria."""
    results = []

    if args.code:
        # Try alpha_2 first, then alpha_3
        result = countries.find(alpha_2=args.code.upper())
        if not result:
            result = countries.find(alpha_3=args.code.upper())
        if result:
            results.append(result)

    elif args.name:
        if args.exact:
            result = countries.find(name=args.name)
            if result:
                results.append(result)
        else:
            results = countries.search(name=args.name)

    elif args.numeric:
        result = countries.find(numeric=args.numeric)
        if result:
            results.append(result)

    elif args.former_name:
        result = countries.get_by_former_name(args.former_name)
        if result:
            results.append(result)

    elif args.list_all:
        results = countries.items

    else:
        print("Please specify search criteria. Use --help for options.")
        return

    if args.limit and len(results) > args.limit:
        results = results[: args.limit]

    output = format_output(results, args.format, args.fields)
    print(output)


def search_languages(args) -> None:
    """Search languages by various criteria."""
    results = []

    if args.code:
        # Try alpha_2 first, then alpha_3
        result = languages.find(alpha_2=args.code.lower())
        if not result:
            result = languages.find(alpha_3=args.code.lower())
        if result:
            results.append(result)

    elif args.name:
        if args.exact:
            result = languages.find(name=args.name)
            if result:
                results.append(result)
        else:
            results = languages.search(name=args.name)

    elif args.list_all:
        results = languages.items

    else:
        print("Please specify search criteria. Use --help for options.")
        return

    if args.limit and len(results) > args.limit:
        results = results[: args.limit]

    output = format_output(results, args.format, args.fields)
    print(output)


def search_currencies(args) -> None:
    """Search currencies by various criteria."""
    results = []

    if args.code:
        result = currencies.find(alpha_3=args.code.upper())
        if result:
            results.append(result)

    elif args.name:
        if args.exact:
            result = currencies.find(name=args.name)
            if result:
                results.append(result)
        else:
            results = currencies.search(name=args.name)

    elif args.numeric:
        result = currencies.find(numeric=args.numeric)
        if result:
            results.append(result)

    elif args.list_all:
        results = currencies.items

    else:
        print("Please specify search criteria. Use --help for options.")
        return

    if args.limit and len(results) > args.limit:
        results = results[: args.limit]

    output = format_output(results, args.format, args.fields)
    print(output)


def search_subdivisions(args) -> None:
    """Search country subdivisions by various criteria."""
    results = []

    if args.code:
        result = subdivisions_countries.find(code=args.code.upper())
        if result:
            results.append(result)

    elif args.name:
        if args.exact:
            result = subdivisions_countries.find(name=args.name)
            if result:
                results.append(result)
        else:
            results = subdivisions_countries.search(name=args.name)

    elif args.country:
        # Filter by country code
        country_code = args.country.upper()
        results = [
            item
            for item in subdivisions_countries.items
            if item.get("code", "").startswith(f"{country_code}-")
        ]

    elif args.list_all:
        results = subdivisions_countries.items

    else:
        print("Please specify search criteria. Use --help for options.")
        return

    if args.limit and len(results) > args.limit:
        results = results[: args.limit]

    output = format_output(results, args.format, args.fields)
    print(output)


def search_former_countries(args) -> None:
    """Search former countries by various criteria."""
    results = []

    if args.code:
        # Try alpha_2, alpha_3, or alpha_4
        result = former_countries.find(alpha_2=args.code.upper())
        if not result:
            result = former_countries.find(alpha_3=args.code.upper())
        if not result:
            result = former_countries.find(alpha_4=args.code.upper())
        if result:
            results.append(result)

    elif args.name:
        if args.exact:
            result = former_countries.find(name=args.name)
            if result:
                results.append(result)
        else:
            results = former_countries.search(name=args.name)

    elif args.list_all:
        results = former_countries.items

    else:
        print("Please specify search criteria. Use --help for options.")
        return

    if args.limit and len(results) > args.limit:
        results = results[: args.limit]

    output = format_output(results, args.format, args.fields)
    print(output)


def search_scripts(args) -> None:
    """Search script names by various criteria."""
    results = []

    if args.code:
        result = script_names.find(alpha_4=args.code.title())
        if result:
            results.append(result)

    elif args.name:
        if args.exact:
            result = script_names.find(name=args.name)
            if result:
                results.append(result)
        else:
            results = script_names.search(name=args.name)

    elif args.numeric:
        result = script_names.find(numeric=args.numeric)
        if result:
            results.append(result)

    elif args.list_all:
        results = script_names.items

    else:
        print("Please specify search criteria. Use --help for options.")
        return

    if args.limit and len(results) > args.limit:
        results = results[: args.limit]

    output = format_output(results, args.format, args.fields)
    print(output)


def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="CLI for isocodes - Access ISO standard data from the command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  isocodes countries --code US                    # Find country by code
  isocodes countries --name Germany --exact       # Find exact country name
  isocodes countries --name Island                # Search countries with "Island"
  isocodes countries --former-name Burma          # Find by former name
  isocodes languages --code en                    # Find language by code
  isocodes currencies --code USD                  # Find currency by code
  isocodes subdivisions --country US              # List US subdivisions
  isocodes countries --list-all --format json     # List all countries as JSON
  isocodes countries --code US --fields name,flag # Show only specific fields
        """,
    )

    # Global options
    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument("--fields", help="Comma-separated list of fields to display")
    parser.add_argument("--limit", type=int, help="Limit number of results")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Countries subcommand
    countries_parser = subparsers.add_parser(
        "countries", help="Search countries (ISO 3166-1)"
    )
    countries_group = countries_parser.add_mutually_exclusive_group(required=True)
    countries_group.add_argument("--code", help="Country code (alpha-2 or alpha-3)")
    countries_group.add_argument("--name", help="Country name")
    countries_group.add_argument("--numeric", help="Numeric country code")
    countries_group.add_argument("--former-name", help="Former country name")
    countries_group.add_argument(
        "--list-all", action="store_true", help="List all countries"
    )
    countries_parser.add_argument(
        "--exact", action="store_true", help="Exact name match only"
    )

    # Languages subcommand
    languages_parser = subparsers.add_parser(
        "languages", help="Search languages (ISO 639-2)"
    )
    languages_group = languages_parser.add_mutually_exclusive_group(required=True)
    languages_group.add_argument("--code", help="Language code (alpha-2 or alpha-3)")
    languages_group.add_argument("--name", help="Language name")
    languages_group.add_argument(
        "--list-all", action="store_true", help="List all languages"
    )
    languages_parser.add_argument(
        "--exact", action="store_true", help="Exact name match only"
    )

    # Currencies subcommand
    currencies_parser = subparsers.add_parser(
        "currencies", help="Search currencies (ISO 4217)"
    )
    currencies_group = currencies_parser.add_mutually_exclusive_group(required=True)
    currencies_group.add_argument("--code", help="Currency code (alpha-3)")
    currencies_group.add_argument("--name", help="Currency name")
    currencies_group.add_argument("--numeric", help="Numeric currency code")
    currencies_group.add_argument(
        "--list-all", action="store_true", help="List all currencies"
    )
    currencies_parser.add_argument(
        "--exact", action="store_true", help="Exact name match only"
    )

    # Subdivisions subcommand
    subdivisions_parser = subparsers.add_parser(
        "subdivisions", help="Search country subdivisions (ISO 3166-2)"
    )
    subdivisions_group = subdivisions_parser.add_mutually_exclusive_group(required=True)
    subdivisions_group.add_argument("--code", help="Subdivision code")
    subdivisions_group.add_argument("--name", help="Subdivision name")
    subdivisions_group.add_argument(
        "--country", help="Country code to list subdivisions for"
    )
    subdivisions_group.add_argument(
        "--list-all", action="store_true", help="List all subdivisions"
    )
    subdivisions_parser.add_argument(
        "--exact", action="store_true", help="Exact name match only"
    )

    # Former countries subcommand
    former_parser = subparsers.add_parser(
        "former-countries", help="Search former countries (ISO 3166-3)"
    )
    former_group = former_parser.add_mutually_exclusive_group(required=True)
    former_group.add_argument("--code", help="Former country code")
    former_group.add_argument("--name", help="Former country name")
    former_group.add_argument(
        "--list-all", action="store_true", help="List all former countries"
    )
    former_parser.add_argument(
        "--exact", action="store_true", help="Exact name match only"
    )

    # Scripts subcommand
    scripts_parser = subparsers.add_parser(
        "scripts", help="Search script names (ISO 15924)"
    )
    scripts_group = scripts_parser.add_mutually_exclusive_group(required=True)
    scripts_group.add_argument("--code", help="Script code (alpha-4)")
    scripts_group.add_argument("--name", help="Script name")
    scripts_group.add_argument("--numeric", help="Numeric script code")
    scripts_group.add_argument(
        "--list-all", action="store_true", help="List all scripts"
    )
    scripts_parser.add_argument(
        "--exact", action="store_true", help="Exact name match only"
    )

    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    # Parse fields if provided
    if args.fields:
        args.fields = [field.strip() for field in args.fields.split(",")]

    try:
        if args.command == "countries":
            search_countries(args)
        elif args.command == "languages":
            search_languages(args)
        elif args.command == "currencies":
            search_currencies(args)
        elif args.command == "subdivisions":
            search_subdivisions(args)
        elif args.command == "former-countries":
            search_former_countries(args)
        elif args.command == "scripts":
            search_scripts(args)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
