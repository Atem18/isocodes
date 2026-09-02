"""Tests for how translation catalogues are located.

`isocodes locales` can remove catalogues, so the library has to behave when they
are missing. These drive that path directly rather than deleting real files.
"""

import warnings

import pytest

import isocodes


@pytest.fixture(autouse=True)
def reset_discovery():
    """Clear the caches and the once-only warning flag around each test."""
    isocodes._locale_dirs.cache_clear()
    isocodes._translator.cache_clear()
    isocodes._warned_no_catalogues = False
    yield
    isocodes._locale_dirs.cache_clear()
    isocodes._translator.cache_clear()
    isocodes._warned_no_catalogues = False


class TestNoCatalogues:
    """The warning is the only signal that translations are missing."""

    def test_warns_and_falls_back(self, monkeypatch):
        monkeypatch.setattr(isocodes, "_locale_dirs", lambda: ())
        germany = isocodes.countries.find(alpha_2="DE")

        with pytest.warns(RuntimeWarning, match="No isocodes translation"):
            assert isocodes.countries.translate(germany, "fr") == "Germany"

    def test_warns_only_once(self, monkeypatch):
        """Warning on every lookup would make the fallback unusable."""
        monkeypatch.setattr(isocodes, "_locale_dirs", lambda: ())

        with warnings.catch_warnings(record=True) as first:
            warnings.simplefilter("always")
            isocodes.countries.translate("Germany", "fr")
        assert len(first) == 1

        with warnings.catch_warnings(record=True) as second:
            warnings.simplefilter("always")
            isocodes.currencies.translate("Euro", "fr")
            isocodes.countries.translate("Spain", "de")
        assert second == []

    def test_available_languages_is_empty(self, monkeypatch):
        monkeypatch.setattr(isocodes, "_locale_dirs", lambda: ())
        assert isocodes.available_languages() == []

    def test_locale_path_falls_back(self, monkeypatch):
        """LOCALE_PATH stays a usable path even with nothing installed."""
        monkeypatch.setattr(isocodes, "_locale_dirs", lambda: ())
        assert isocodes.LOCALE_PATH == isocodes._BUNDLED_LOCALE_PATH


class TestMatchRank:
    """Ranking rules behind search()."""

    def test_ordering_of_ranks(self):
        rank = isocodes.ISO._match_rank
        assert rank("germany", "Germany") == 0
        assert rank("ger", "Germany") == 1
        assert rank("erman", "Germany") == 2
        assert rank("republic korea", "Korea, Republic of") == 3

    def test_no_match_and_empty_query(self):
        rank = isocodes.ISO._match_rank
        assert rank("xyzzy", "Germany") is None
        assert rank("", "Germany") is None
        assert rank("   ", "Germany") is None

    def test_records_missing_the_field_are_skipped(self):
        """Most countries have no common_name, and must not match on it."""
        results = isocodes.countries.search(common_name="Bolivia")
        assert all("common_name" in record for record in results)


class TestDomainAliases:
    """Upstream's obsolete catalogue names still resolve.

    Only the current filenames are packaged, since shipping both doubled the
    package, so the old names are mapped onto them.
    """

    @pytest.mark.parametrize(
        "legacy, current",
        [
            ("iso_3166", "iso_3166-1"),
            ("iso_3166_2", "iso_3166-2"),
            ("iso_639", "iso_639-2"),
            ("iso_639_3", "iso_639-3"),
            ("iso_639_5", "iso_639-5"),
        ],
    )
    def test_alias_maps_to_current_domain(self, legacy, current):
        assert isocodes._DOMAIN_ALIASES[legacy] == current

    @pytest.mark.skipif(
        "fr" not in isocodes.available_languages(),
        reason="the French catalogue is not installed",
    )
    def test_legacy_domain_still_translates(self):
        translate = isocodes._translator("iso_3166", "fr")
        assert translate("Germany") == "Allemagne"

    def test_current_domains_are_unaffected(self):
        assert isocodes.countries.domain == "iso_3166-1"


class TestLocaleDirs:
    """_locale_dirs reports what is actually on disk."""

    def test_finds_the_bundled_catalogues(self):
        dirs = isocodes._locale_dirs()
        assert dirs == (isocodes._BUNDLED_LOCALE_PATH,)

    def test_empty_when_the_directory_is_gone(self, monkeypatch, tmp_path):
        """`isocodes locales` can remove every language."""
        monkeypatch.setattr(isocodes, "_BUNDLED_LOCALE_PATH", tmp_path / "absent")
        isocodes._locale_dirs.cache_clear()
        assert isocodes._locale_dirs() == ()
