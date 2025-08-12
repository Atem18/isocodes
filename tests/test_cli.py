"""Tests for the isocodes CLI."""

import json
import subprocess
import sys
from typing import List


def run_cli_command(args: List[str]) -> subprocess.CompletedProcess:
    """Run a CLI command and return the result."""
    cmd = [sys.executable, "-m", "isocodes.cli"] + args
    return subprocess.run(cmd, capture_output=True, text=True)


class TestCLIBasic:
    """Test basic CLI functionality."""

    def test_cli_help(self):
        """Test that CLI help works."""
        result = run_cli_command(["--help"])
        assert result.returncode == 0
        assert "CLI for isocodes" in result.stdout
        assert "countries" in result.stdout
        assert "languages" in result.stdout
        assert "currencies" in result.stdout

    def test_cli_no_args(self):
        """Test CLI with no arguments shows help."""
        result = run_cli_command([])
        assert result.returncode == 0
        assert "CLI for isocodes" in result.stdout


class TestCountriesCLI:
    """Test countries CLI functionality."""

    def test_country_by_alpha2_code(self):
        """Test finding country by alpha-2 code."""
        result = run_cli_command(["countries", "--code", "US"])
        assert result.returncode == 0
        assert "United States" in result.stdout
        assert "🇺🇸" in result.stdout

    def test_country_by_alpha3_code(self):
        """Test finding country by alpha-3 code."""
        result = run_cli_command(["countries", "--code", "DEU"])
        assert result.returncode == 0
        assert "Germany" in result.stdout
        assert "🇩🇪" in result.stdout

    def test_country_by_name_exact(self):
        """Test finding country by exact name."""
        result = run_cli_command(["countries", "--name", "France", "--exact"])
        assert result.returncode == 0
        assert "France" in result.stdout
        assert "🇫🇷" in result.stdout

    def test_country_by_name_search(self):
        """Test searching countries by name."""
        result = run_cli_command(["countries", "--name", "Island"])
        assert result.returncode == 0
        assert "Island" in result.stdout

    def test_country_by_former_name(self):
        """Test finding country by former name."""
        result = run_cli_command(["countries", "--former-name", "Burma"])
        assert result.returncode == 0
        assert "Myanmar" in result.stdout

    def test_country_json_format(self):
        """Test JSON output format."""
        result = run_cli_command(["--format", "json", "countries", "--code", "US"])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data[0]["alpha_2"] == "US"
        assert data[0]["name"] == "United States"

    def test_country_csv_format(self):
        """Test CSV output format."""
        result = run_cli_command(["--format", "csv", "countries", "--code", "US"])
        assert result.returncode == 0

        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 2  # Header + data
        assert "alpha_2" in lines[0]

    def test_country_specific_fields(self):
        """Test displaying specific fields only."""
        result = run_cli_command(
            ["--fields", "name,flag,alpha_2", "countries", "--code", "US"]
        )
        assert result.returncode == 0
        assert "United States" in result.stdout
        assert "🇺🇸" in result.stdout
        # Should not contain other fields like alpha_3, numeric, etc.
        assert "USA" not in result.stdout

    def test_country_numeric_code(self):
        """Test finding country by numeric code."""
        result = run_cli_command(["countries", "--numeric", "840"])
        assert result.returncode == 0
        assert "United States" in result.stdout


class TestLanguagesCLI:
    """Test languages CLI functionality."""

    def test_language_by_alpha2_code(self):
        """Test finding language by alpha-2 code."""
        result = run_cli_command(["languages", "--code", "en"])
        assert result.returncode == 0
        assert "English" in result.stdout

    def test_language_by_alpha3_code(self):
        """Test finding language by alpha-3 code."""
        result = run_cli_command(["languages", "--code", "deu"])
        assert result.returncode == 0
        assert "German" in result.stdout

    def test_language_by_name_search(self):
        """Test searching languages by name."""
        result = run_cli_command(["languages", "--name", "French"])
        assert result.returncode == 0
        assert "French" in result.stdout


class TestCurrenciesCLI:
    """Test currencies CLI functionality."""

    def test_currency_by_code(self):
        """Test finding currency by code."""
        result = run_cli_command(["currencies", "--code", "USD"])
        assert result.returncode == 0
        assert "US Dollar" in result.stdout

    def test_currency_by_name_search(self):
        """Test searching currencies by name."""
        result = run_cli_command(["currencies", "--name", "Euro"])
        assert result.returncode == 0
        assert "Euro" in result.stdout

    def test_currency_by_numeric(self):
        """Test finding currency by numeric code."""
        result = run_cli_command(["currencies", "--numeric", "840"])
        assert result.returncode == 0
        assert "US Dollar" in result.stdout


class TestSubdivisionsCLI:
    """Test subdivisions CLI functionality."""

    def test_subdivision_by_code(self):
        """Test finding subdivision by code."""
        result = run_cli_command(["subdivisions", "--code", "US-CA"])
        assert result.returncode == 0
        assert "California" in result.stdout

    def test_subdivisions_by_country(self):
        """Test listing subdivisions by country."""
        result = run_cli_command(["--limit", "5", "subdivisions", "--country", "US"])
        assert result.returncode == 0
        assert "US-" in result.stdout


class TestFormerCountriesCLI:
    """Test former countries CLI functionality."""

    def test_former_country_by_code(self):
        """Test finding former country by code."""
        result = run_cli_command(["former-countries", "--code", "YUG"])
        assert result.returncode == 0
        assert "Yugoslavia" in result.stdout


class TestScriptsCLI:
    """Test scripts CLI functionality."""

    def test_script_by_code(self):
        """Test finding script by code."""
        result = run_cli_command(["scripts", "--code", "Latn"])
        assert result.returncode == 0
        assert "Latin" in result.stdout

    def test_script_by_numeric(self):
        """Test finding script by numeric code."""
        result = run_cli_command(["scripts", "--numeric", "215"])
        assert result.returncode == 0
        assert "Latin" in result.stdout


class TestCLIEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_country_code(self):
        """Test searching for invalid country code."""
        result = run_cli_command(["countries", "--code", "INVALID"])
        assert result.returncode == 0
        assert "No results found" in result.stdout

    def test_invalid_command(self):
        """Test invalid command shows help."""
        result = run_cli_command(["invalid-command"])
        assert result.returncode != 0 or "CLI for isocodes" in result.stdout

    def test_limit_functionality(self):
        """Test limit functionality."""
        result = run_cli_command(["--limit", "2", "countries", "--name", "Island"])
        assert result.returncode == 0
        # Count number of result lines (excluding header and separator)
        lines = [
            line
            for line in result.stdout.split("\n")
            if line.strip() and not line.startswith("-")
        ]
        # Should have header + max 2 data lines
        assert len(lines) <= 3


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_pipeline_json_to_jq(self):
        """Test that JSON output can be piped to jq (if available)."""
        result = run_cli_command(["--format", "json", "countries", "--code", "US"])
        assert result.returncode == 0

        # Validate JSON
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert "alpha_2" in data[0]

    def test_csv_output_parseable(self):
        """Test that CSV output is properly formatted."""
        result = run_cli_command(["--format", "csv", "countries", "--code", "US"])
        assert result.returncode == 0

        lines = result.stdout.strip().split("\n")
        assert len(lines) >= 2

        # Check header line
        headers = lines[0].split(",")
        assert "alpha_2" in headers

        # Check data line
        data_line = lines[1].split(",")
        assert len(data_line) == len(headers)
