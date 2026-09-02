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
import dataclasses
import json
import shutil
import sys
from typing import Any, Callable, List, Optional, Tuple

import isocodes


def format_output(
    data: List[Any], output_format: str = "table", fields: Optional[List[str]] = None
) -> str:
    """Render a list of records in the requested format.

    The empty case is handled per format: no results must still produce valid
    JSON or CSV, so that callers parsing the output are not surprised.
    """

    def headers_for(records: List[Any]) -> List[str]:
        """Column names, in the order --fields asked for when it was given."""
        available = set()
        for record in records:
            available.update(record.keys())
        if fields:
            return [key for key in fields if key in available]
        return sorted(available)

    if output_format == "json":
        return json.dumps(
            [
                {key: record[key] for key in headers_for([record])}
                for record in map(dict, data)
            ],
            indent=2,
            ensure_ascii=False,
        )

    elif output_format == "csv":
        if not data:
            return ""

        headers = headers_for(data)
        lines = [",".join(headers)]
        for item in data:
            lines.append(
                ",".join(
                    str(item.get(header, "")).replace(",", ";") for header in headers
                )
            )
        return "\n".join(lines)

    else:  # table format
        if not data:
            return "No results found."

        headers = headers_for(data)
        widths = {
            header: max(
                [len(header)] + [len(str(item.get(header, ""))) for item in data]
            )
            for header in headers
        }

        header_line = " | ".join(header.ljust(widths[header]) for header in headers)
        lines = [header_line, "-" * len(header_line)]
        for item in data:
            lines.append(
                " | ".join(
                    str(item.get(header, "")).ljust(widths[header])
                    for header in headers
                )
            )
        return "\n".join(lines)


@dataclasses.dataclass(frozen=True)
class _Standard:
    """How one ISO standard is exposed on the command line.

    The six standards differ only in which code fields they carry and how those
    codes are cased, so they share a parser builder and a search handler.
    """

    dataset: str
    """Attribute on the isocodes package; looked up lazily so that commands
    which need no data, like `locales` and `--help`, stay fast."""

    help: str
    noun: str
    name_help: str
    code_help: str
    code_fields: Tuple[str, ...]
    normalise: Callable[[str], str]
    numeric_help: Optional[str] = None
    former_name_help: Optional[str] = None
    country_help: Optional[str] = None


_STANDARDS: "dict[str, _Standard]" = {
    "countries": _Standard(
        dataset="countries",
        name_help="Country name",
        help="Search countries (ISO 3166-1)",
        noun="countries",
        code_help="Country code (alpha-2 or alpha-3)",
        code_fields=("alpha_2", "alpha_3"),
        normalise=str.upper,
        numeric_help="Numeric country code",
        former_name_help="Former country name",
    ),
    "languages": _Standard(
        dataset="languages",
        name_help="Language name",
        help="Search languages (ISO 639-2)",
        noun="languages",
        code_help="Language code (alpha-2 or alpha-3)",
        code_fields=("alpha_2", "alpha_3"),
        normalise=str.lower,
    ),
    "currencies": _Standard(
        dataset="currencies",
        name_help="Currency name",
        help="Search currencies (ISO 4217)",
        noun="currencies",
        code_help="Currency code (alpha-3)",
        code_fields=("alpha_3",),
        normalise=str.upper,
        numeric_help="Numeric currency code",
    ),
    "subdivisions": _Standard(
        dataset="subdivisions_countries",
        name_help="Subdivision name",
        help="Search country subdivisions (ISO 3166-2)",
        noun="subdivisions",
        code_help="Subdivision code",
        code_fields=("code",),
        normalise=str.upper,
        country_help="Country code to list subdivisions for",
    ),
    "former-countries": _Standard(
        dataset="former_countries",
        name_help="Former country name",
        help="Search former countries (ISO 3166-3)",
        noun="former countries",
        code_help="Former country code",
        code_fields=("alpha_2", "alpha_3", "alpha_4"),
        normalise=str.upper,
    ),
    "scripts": _Standard(
        dataset="script_names",
        name_help="Script name",
        help="Search script names (ISO 15924)",
        noun="scripts",
        code_help="Script code (alpha-4)",
        code_fields=("alpha_4",),
        normalise=str.title,
        numeric_help="Numeric script code",
    ),
}


def search_standard(args) -> None:
    """Search one ISO standard using the criteria the user supplied."""
    standard = _STANDARDS[args.command]
    dataset = getattr(isocodes, standard.dataset)
    results: List[Any] = []

    if args.code:
        code = standard.normalise(args.code)
        for field in standard.code_fields:
            match = dataset.find(**{field: code})
            if match:
                results.append(match)
                break

    elif args.name:
        if args.fuzzy:
            results = dataset.search_fuzzy(args.name)
        elif args.exact:
            match = dataset.find(name=args.name)
            if match:
                results.append(match)
        else:
            results = dataset.search(name=args.name)

    elif getattr(args, "numeric", None):
        match = dataset.find(numeric=args.numeric)
        if match:
            results.append(match)

    elif getattr(args, "former_name", None):
        match = dataset.get_by_former_name(args.former_name)
        if match:
            results.append(match)

    elif getattr(args, "country", None):
        prefix = f"{args.country.upper()}-"
        results = [
            item for item in dataset.items if item.get("code", "").startswith(prefix)
        ]

    elif args.list_all:
        results = dataset.items

    if args.limit and len(results) > args.limit:
        results = results[: args.limit]

    print(format_output(results, args.format, args.fields))


def _language_sizes() -> dict[str, int]:
    """Installed language code -> bytes of catalogue data."""
    root = isocodes.LOCALE_PATH
    if not root.is_dir():
        return {}
    sizes = {}
    for path in root.iterdir():
        if (path / "LC_MESSAGES").is_dir():
            sizes[path.name] = sum(
                item.stat().st_size for item in path.rglob("*") if item.is_file()
            )
    return sizes


def _human(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB"):
        if value < 1024:
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} MB"


def manage_locales(args) -> None:
    """List or remove the bundled translation catalogues.

    Catalogues ship with the package, so this only ever deletes files that pip
    put there. It is meant for trimming container images, where the removal
    happens in the same build step as the install; a later `pip install
    --upgrade` restores every language.
    """
    sizes = _language_sizes()
    if not sizes:
        print("No translation catalogues are installed.")
        return

    total = sum(sizes.values())

    if not args.keep and not args.remove:
        print(f"{len(sizes)} languages installed, {_human(total)} total\n")
        for language in sorted(sizes):
            print(f"  {language:12} {_human(sizes[language]):>9}")
        print("\nRemove all but a few with: isocodes locales --keep fr,en --yes")
        return

    if args.keep:
        wanted = {code.strip() for code in args.keep.split(",") if code.strip()}
        unknown = wanted - set(sizes)
        if unknown:
            print(
                f"Error: not installed: {', '.join(sorted(unknown))}. "
                "Run 'isocodes locales' to see what is available.",
                file=sys.stderr,
            )
            sys.exit(1)
        doomed = sorted(set(sizes) - wanted)
    else:
        doomed = sorted(
            code.strip() for code in args.remove.split(",") if code.strip() in sizes
        )

    if not doomed:
        print("Nothing to remove.")
        return

    freed = sum(sizes[code] for code in doomed)

    if not args.yes:
        print(f"Would remove {len(doomed)} languages, freeing {_human(freed)}:")
        print("  " + ", ".join(doomed))
        print(f"\nKeeping: {', '.join(sorted(set(sizes) - set(doomed))) or 'none'}")
        print("\nRe-run with --yes to apply. This cannot be undone without")
        print("'pip install --force-reinstall isocodes'.")
        return

    root = isocodes.LOCALE_PATH
    for code in doomed:
        try:
            shutil.rmtree(root / code)
        except OSError as error:
            print(
                f"Error: could not remove '{code}': {error}. "
                "The package directory may be read-only.",
                file=sys.stderr,
            )
            sys.exit(1)

    print(f"Removed {len(doomed)} languages, freed {_human(freed)}.")


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
  isocodes locales                                # List installed languages
  isocodes locales --keep fr,en --yes             # Keep only French and English
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

    for name, standard in _STANDARDS.items():
        command = subparsers.add_parser(name, help=standard.help)
        group = command.add_mutually_exclusive_group(required=True)
        group.add_argument("--code", help=standard.code_help)
        group.add_argument("--name", help=standard.name_help)
        if standard.numeric_help:
            group.add_argument("--numeric", help=standard.numeric_help)
        if standard.former_name_help:
            group.add_argument("--former-name", help=standard.former_name_help)
        if standard.country_help:
            group.add_argument("--country", help=standard.country_help)
        group.add_argument(
            "--list-all", action="store_true", help=f"List all {standard.noun}"
        )
        matching = command.add_mutually_exclusive_group()
        matching.add_argument(
            "--exact", action="store_true", help="Exact name match only"
        )
        matching.add_argument(
            "--fuzzy", action="store_true", help="Tolerate misspellings in --name"
        )

    # Translation catalogues
    locales_parser = subparsers.add_parser(
        "locales",
        help="List or remove bundled translation catalogues",
        description=(
            "Every language ships with the package. Removing the ones you do "
            "not need is useful for trimming container images; do it in the "
            "same build step as the install, because 'pip install --upgrade' "
            "restores them all."
        ),
    )
    locales_group = locales_parser.add_mutually_exclusive_group()
    locales_group.add_argument(
        "--keep", help="Comma-separated languages to keep; all others are removed"
    )
    locales_group.add_argument("--remove", help="Comma-separated languages to remove")
    locales_parser.add_argument(
        "--yes",
        action="store_true",
        help="Actually delete. Without it, the removal is only described.",
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
        if args.command in _STANDARDS:
            search_standard(args)
        elif args.command == "locales":
            manage_locales(args)
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
