"""In-process CLI tests for output formats, empty results and error handling.

The existing CLI tests shell out, which is slow and hides these branches from
coverage. These drive main() directly instead.
"""

import json

import pytest

from isocodes import cli


def run(monkeypatch, capsys, *argv):
    """Invoke the CLI in-process and return its stdout."""
    monkeypatch.setattr("sys.argv", ["isocodes", *argv])
    cli.main()
    return capsys.readouterr().out


class TestOutputFormats:
    def test_table_is_the_default(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, "countries", "--code", "FR")
        assert "France" in out and "|" in out

    def test_json(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, "--format", "json", "countries", "--code", "FR")
        payload = json.loads(out)
        assert payload[0]["name"] == "France"

    def test_csv(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, "--format", "csv", "countries", "--code", "FR")
        header, row = out.strip().splitlines()[:2]
        assert "alpha_2" in header and "FR" in row

    def test_selected_fields(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            "--format",
            "json",
            "--fields",
            "name,alpha_2",
            "countries",
            "--code",
            "FR",
        )
        assert set(json.loads(out)[0]) == {"name", "alpha_2"}

    def test_limit(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            "--format",
            "json",
            "--limit",
            "2",
            "countries",
            "--name",
            "Island",
        )
        assert len(json.loads(out)) == 2

    def test_exact_flag(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, "countries", "--name", "France", "--exact")
        assert "France" in out


class TestEmptyResults:
    """Every command has a no-match path."""

    @pytest.mark.parametrize(
        "command, flag, value",
        [
            ("countries", "--code", "ZZ"),
            ("countries", "--numeric", "000"),
            ("countries", "--former-name", "Nowhere At All"),
            ("languages", "--code", "zzz"),
            ("currencies", "--code", "ZZZ"),
            ("subdivisions", "--code", "ZZ-ZZ"),
            ("former-countries", "--code", "ZZ"),
            ("scripts", "--code", "Qxyz"),
        ],
    )
    def test_no_results(self, monkeypatch, capsys, command, flag, value):
        out = run(monkeypatch, capsys, command, flag, value)
        assert "No results found." in out

    def test_empty_csv(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, "--format", "csv", "countries", "--code", "ZZ")
        assert out.strip() == ""

    def test_empty_json(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, "--format", "json", "countries", "--code", "ZZ")
        assert json.loads(out) == []


class TestMissingCriteria:
    """Each command requires one search flag, enforced by argparse itself."""

    @pytest.mark.parametrize(
        "command",
        [
            "countries",
            "languages",
            "currencies",
            "subdivisions",
            "former-countries",
            "scripts",
        ],
    )
    def test_exits_with_usage_error(self, monkeypatch, capsys, command):
        monkeypatch.setattr("sys.argv", ["isocodes", command])
        with pytest.raises(SystemExit) as exit_info:
            cli.main()
        assert exit_info.value.code == 2
        assert "usage:" in capsys.readouterr().err


class TestCommands:
    """Each subcommand returns something sensible."""

    def test_languages(self, monkeypatch, capsys):
        assert "English" in run(monkeypatch, capsys, "languages", "--code", "eng")

    def test_currencies(self, monkeypatch, capsys):
        assert "Euro" in run(monkeypatch, capsys, "currencies", "--code", "EUR")

    def test_currencies_by_numeric(self, monkeypatch, capsys):
        assert "Euro" in run(monkeypatch, capsys, "currencies", "--numeric", "978")

    def test_subdivisions_by_country(self, monkeypatch, capsys):
        out = run(
            monkeypatch, capsys, "--limit", "3", "subdivisions", "--country", "FR"
        )
        assert out.strip() != ""

    def test_scripts(self, monkeypatch, capsys):
        assert "Latin" in run(monkeypatch, capsys, "scripts", "--code", "Latn")

    def test_former_countries(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, "former-countries", "--name", "Burma")
        assert "Burma" in out

    def test_list_all(self, monkeypatch, capsys):
        out = run(
            monkeypatch,
            capsys,
            "--format",
            "json",
            "--limit",
            "5",
            "countries",
            "--list-all",
        )
        assert len(json.loads(out)) == 5


class TestErrorHandling:
    def test_no_arguments_prints_help(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys)
        assert "CLI for isocodes" in out

    def test_unexpected_error_exits_nonzero(self, monkeypatch, capsys):
        """Failures are reported on stderr rather than as a traceback."""

        def boom(_args):
            raise RuntimeError("kaboom")

        monkeypatch.setattr(cli, "search_standard", boom)
        monkeypatch.setattr("sys.argv", ["isocodes", "countries", "--code", "FR"])
        with pytest.raises(SystemExit) as exit_info:
            cli.main()
        assert exit_info.value.code == 1
        assert "kaboom" in capsys.readouterr().err

    def test_interrupt_is_handled(self, monkeypatch, capsys):
        def interrupt(_args):
            raise KeyboardInterrupt

        monkeypatch.setattr(cli, "search_standard", interrupt)
        monkeypatch.setattr("sys.argv", ["isocodes", "countries", "--code", "FR"])
        with pytest.raises(SystemExit) as exit_info:
            cli.main()
        assert exit_info.value.code == 1
        assert "cancelled" in capsys.readouterr().out.lower()


class TestLocalesCommand:
    """The locales command lists and prunes bundled catalogues."""

    def test_listing_shows_languages_and_total(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, "locales")
        assert "languages installed" in out
        assert "  fr " in out

    def test_dry_run_by_default(self, monkeypatch, capsys, tmp_path):
        """Nothing is deleted without --yes."""
        catalogues = _fake_locales(tmp_path, "fr", "de", "es")
        monkeypatch.setattr(cli.isocodes, "LOCALE_PATH", catalogues, raising=False)
        out = run(monkeypatch, capsys, "locales", "--keep", "fr")
        assert "Would remove 2 languages" in out
        assert "Re-run with --yes" in out
        assert sorted(p.name for p in catalogues.iterdir()) == ["de", "es", "fr"]

    def test_keep_removes_the_rest(self, monkeypatch, capsys, tmp_path):
        catalogues = _fake_locales(tmp_path, "fr", "de", "es")
        monkeypatch.setattr(cli.isocodes, "LOCALE_PATH", catalogues, raising=False)
        out = run(monkeypatch, capsys, "locales", "--keep", "fr", "--yes")
        assert "Removed 2 languages" in out
        assert [p.name for p in catalogues.iterdir()] == ["fr"]

    def test_remove_named_languages(self, monkeypatch, capsys, tmp_path):
        catalogues = _fake_locales(tmp_path, "fr", "de", "es")
        monkeypatch.setattr(cli.isocodes, "LOCALE_PATH", catalogues, raising=False)
        run(monkeypatch, capsys, "locales", "--remove", "de,es", "--yes")
        assert [p.name for p in catalogues.iterdir()] == ["fr"]

    def test_unknown_language_is_an_error(self, monkeypatch, capsys, tmp_path):
        catalogues = _fake_locales(tmp_path, "fr")
        monkeypatch.setattr(cli.isocodes, "LOCALE_PATH", catalogues, raising=False)
        monkeypatch.setattr("sys.argv", ["isocodes", "locales", "--keep", "fr,nope"])
        with pytest.raises(SystemExit) as exit_info:
            cli.main()
        assert exit_info.value.code == 1
        assert "not installed: nope" in capsys.readouterr().err

    def test_nothing_to_remove(self, monkeypatch, capsys, tmp_path):
        catalogues = _fake_locales(tmp_path, "fr")
        monkeypatch.setattr(cli.isocodes, "LOCALE_PATH", catalogues, raising=False)
        assert "Nothing to remove" in run(
            monkeypatch, capsys, "locales", "--keep", "fr", "--yes"
        )

    def test_no_catalogues_at_all(self, monkeypatch, capsys, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        monkeypatch.setattr(cli.isocodes, "LOCALE_PATH", empty, raising=False)
        assert "No translation catalogues" in run(monkeypatch, capsys, "locales")

    def test_read_only_directory_is_reported(self, monkeypatch, capsys, tmp_path):
        """Site-packages is read-only in some installs; say so rather than crash."""
        catalogues = _fake_locales(tmp_path, "fr", "de")
        monkeypatch.setattr(cli.isocodes, "LOCALE_PATH", catalogues, raising=False)

        def refuse(_path):
            raise OSError("Read-only file system")

        monkeypatch.setattr(cli.shutil, "rmtree", refuse)
        monkeypatch.setattr(
            "sys.argv", ["isocodes", "locales", "--keep", "fr", "--yes"]
        )
        with pytest.raises(SystemExit) as exit_info:
            cli.main()
        assert exit_info.value.code == 1
        assert "read-only" in capsys.readouterr().err.lower()


def _fake_locales(tmp_path, *languages):
    """Build a locale directory tree with one dummy catalogue per language."""
    root = tmp_path / "locale"
    for language in languages:
        messages = root / language / "LC_MESSAGES"
        messages.mkdir(parents=True)
        (messages / "iso_3166-1.mo").write_bytes(b"\x00" * 1024)
    return root


class TestEveryCommandPath:
    """Each subcommand supports --name, --exact, --list-all and --limit."""

    @pytest.mark.parametrize(
        "command, name",
        [
            ("languages", "French"),
            ("currencies", "Euro"),
            ("subdivisions", "Paris"),
            ("former-countries", "Burma, Socialist Republic of the Union of"),
            ("scripts", "Latin"),
        ],
    )
    def test_exact_name(self, monkeypatch, capsys, command, name):
        out = run(monkeypatch, capsys, command, "--name", name, "--exact")
        assert name in out

    @pytest.mark.parametrize(
        "command, fragment",
        [
            ("subdivisions", "Paris"),
            ("scripts", "Latin"),
            ("former-countries", "Burma"),
        ],
    )
    def test_fuzzy_name(self, monkeypatch, capsys, command, fragment):
        assert fragment in run(monkeypatch, capsys, command, "--name", fragment)

    @pytest.mark.parametrize(
        "command",
        [
            "countries",
            "languages",
            "currencies",
            "subdivisions",
            "former-countries",
            "scripts",
        ],
    )
    def test_list_all_with_limit(self, monkeypatch, capsys, command):
        out = run(
            monkeypatch,
            capsys,
            "--format",
            "json",
            "--limit",
            "3",
            command,
            "--list-all",
        )
        assert len(json.loads(out)) == 3

    @pytest.mark.parametrize(
        "command, value",
        [
            ("countries", "250"),
            ("currencies", "978"),
            ("scripts", "215"),
        ],
    )
    def test_numeric_lookup(self, monkeypatch, capsys, command, value):
        out = run(monkeypatch, capsys, "--format", "json", command, "--numeric", value)
        assert json.loads(out) != []

    def test_no_subcommand_prints_help(self, monkeypatch, capsys):
        """Global flags without a command should not be a crash."""
        out = run(monkeypatch, capsys, "--format", "json")
        assert "CLI for isocodes" in out


class TestHelpers:
    def test_human_readable_sizes(self):
        assert cli._human(512) == "512 B"
        assert cli._human(2048) == "2.0 KB"
        assert cli._human(5 * 1024 * 1024) == "5.0 MB"
        assert cli._human(3 * 1024 * 1024 * 1024) == "3072.0 MB"

    def test_language_sizes_without_a_directory(self, monkeypatch, tmp_path):
        monkeypatch.setattr(
            cli.isocodes, "LOCALE_PATH", tmp_path / "gone", raising=False
        )
        assert cli._language_sizes() == {}


class TestFuzzyFlag:
    """--fuzzy opts in to misspelling tolerance."""

    def test_recovers_a_typo(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, "countries", "--name", "Germny", "--fuzzy")
        assert "Germany" in out

    def test_default_does_not_guess(self, monkeypatch, capsys):
        out = run(monkeypatch, capsys, "countries", "--name", "Germny")
        assert "No results found." in out

    def test_available_on_every_standard(self, monkeypatch, capsys):
        for command, typo in [
            ("languages", "Frenchh"),
            ("currencies", "Eruo"),
            ("scripts", "Latn"),
        ]:
            out = run(monkeypatch, capsys, command, "--name", typo, "--fuzzy")
            assert out.strip() != ""

    def test_conflicts_with_exact(self, monkeypatch, capsys):
        monkeypatch.setattr(
            "sys.argv", ["isocodes", "countries", "--name", "x", "--exact", "--fuzzy"]
        )
        with pytest.raises(SystemExit) as exit_info:
            cli.main()
        assert exit_info.value.code == 2
