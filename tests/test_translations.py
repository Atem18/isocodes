"""Tests for translation support and lazy dataset loading."""

import pathlib

import pytest

import isocodes
from isocodes import (
    ISONamespaceRecord,
    available_languages,
    countries,
    currencies,
)


def _has(language: str) -> bool:
    """Whether a catalogue for `language` is installed in this environment."""
    return language in available_languages()


needs_french = pytest.mark.skipif(
    not _has("fr"), reason="the French catalogue is not installed"
)


class TestTranslation:
    """translate() and translator() read the gettext catalogues."""

    @needs_french
    def test_translate_a_record(self):
        germany = countries.find(alpha_2="DE")
        assert countries.translate(germany, "fr") == "Allemagne"

    @needs_french
    def test_translate_a_plain_name(self):
        assert countries.translate("France", "fr") == "France"
        assert countries.translate("Germany", "fr") == "Allemagne"

    @needs_french
    def test_each_standard_uses_its_own_domain(self):
        euro = currencies.find(alpha_3="EUR")
        assert currencies.translate(euro, "fr") == "Euro"

    @needs_french
    def test_translator_is_reusable(self):
        to_french = countries.translator("fr")
        assert to_french("Germany") == "Allemagne"
        assert to_french("Spain") == "Espagne"

    def test_unknown_language_falls_back(self):
        """A language with no catalogue returns the name unchanged."""
        germany = countries.find(alpha_2="DE")
        assert countries.translate(germany, "zz-not-a-language") == "Germany"

    def test_empty_input(self):
        assert countries.translate("", "fr") == ""
        assert countries.translate({}, "fr") == ""

    def test_domain_matches_the_standard(self):
        assert countries.domain == "iso_3166-1"
        assert currencies.domain == "iso_4217"


class TestAvailableLanguages:
    def test_returns_sorted_codes(self):
        languages = available_languages()
        assert languages == sorted(languages)

    def test_locale_path_is_a_path(self):
        assert isinstance(isocodes.LOCALE_PATH, pathlib.Path)


class TestLazyLoading:
    """Datasets are built on first access, not at import."""

    def test_datasets_are_reachable(self):
        assert isocodes.countries.find(alpha_2="FR").name == "France"

    def test_same_instance_each_time(self):
        assert isocodes.countries is isocodes.countries

    def test_listed_in_dir(self):
        listing = dir(isocodes)
        assert "countries" in listing
        assert "LOCALE_PATH" in listing

    def test_unknown_attribute_raises(self):
        with pytest.raises(AttributeError):
            isocodes.not_a_real_dataset


class TestRecord:
    """Records are dicts that also support attribute access."""

    def test_both_access_styles(self):
        france = countries.find(alpha_2="FR")
        assert france["name"] == france.name
        assert isinstance(france, dict)

    def test_missing_attribute_raises(self):
        with pytest.raises(AttributeError):
            countries.find(alpha_2="FR").not_a_field

    def test_assignment_writes_through(self):
        record = ISONamespaceRecord({"name": "Test"})
        record.name = "Changed"
        assert record["name"] == "Changed"
        record["name"] = "Again"
        assert record.name == "Again"

    def test_deletion_writes_through(self):
        record = ISONamespaceRecord({"name": "Test", "alpha_2": "TT"})
        del record.alpha_2
        assert "alpha_2" not in record
        with pytest.raises(AttributeError):
            del record.alpha_2

    def test_repr_shows_the_contents(self):
        assert repr(ISONamespaceRecord({"a": "b"})) == "ISONamespaceRecord({'a': 'b'})"

    def test_dict_methods_still_work(self):
        record = ISONamespaceRecord({"name": "Test"})
        assert record.get("name") == "Test"
        assert record.get("missing") is None
        assert list(record.keys()) == ["name"]
