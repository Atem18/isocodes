"""Tests for the get(), find() and search() lookup semantics."""

from isocodes import (
    ISONamespaceRecord,
    countries,
    currencies,
    extended_languages,
    former_countries,
    language_families,
    languages,
    script_names,
    subdivisions_countries,
)


class TestFind:
    """find() is an exact-match lookup across every keyword given."""

    def test_single_indexed_field(self):
        assert countries.find(alpha_2="US").name == "United States"
        assert countries.find(alpha_3="DEU").name == "Germany"
        assert countries.find(numeric="250").name == "France"

    def test_all_criteria_must_match(self):
        """Extra keywords are not ignored; every one has to match."""
        assert countries.find(alpha_2="US", name="United States") is not None
        assert countries.find(alpha_2="US", name="Not A Country") is None

    def test_exact_not_substring(self):
        """Unlike get(), a partial code does not match."""
        assert countries.find(alpha_2="U") is None
        assert countries.find(alpha_2="US") is not None

    def test_no_match_and_no_kwargs(self):
        assert countries.find(alpha_2="ZZ") is None
        assert countries.find() is None

    def test_unindexed_field(self):
        result = countries.find(official_name="United States of America")
        assert result is not None and result.alpha_2 == "US"


class TestGet:
    """get() keeps its substring behaviour for backward compatibility."""

    def test_exact_code(self):
        assert countries.get(alpha_2="US").name == "United States"

    def test_partial_code_still_matches(self):
        assert countries.get(alpha_2="U") != {}

    def test_missing_returns_empty_record(self):
        result = countries.get(alpha_2="ZZ")
        assert result == {}
        assert isinstance(result, dict)


class TestSearch:
    """search() ignores word order and ranks its results."""

    def test_word_order_does_not_matter(self):
        """ISO stores this name inverted, as 'Korea, Republic of'."""
        names = [c.name for c in countries.search(name="Republic of Korea")]
        assert "Korea, Republic of" in names

    def test_closest_match_ranks_first(self):
        names = [c.name for c in countries.search(name="Republic of Korea")]
        assert names[0] == "Korea, Republic of"

    def test_exact_match_beats_longer_one(self):
        assert countries.search(name="Congo")[0].name == "Congo"

    def test_substring_still_works(self):
        assert countries.search(name="Kingdom")[0].name == "United Kingdom"

    def test_punctuation_is_tolerated(self):
        names = [c.name for c in countries.search(name="Cocos (Keeling)")]
        assert names == ["Cocos (Keeling) Islands"]

    def test_every_field_must_match(self):
        assert countries.search(alpha_2="DE", name="Germany") != []
        assert countries.search(alpha_2="DE", name="France") == []

    def test_no_match_and_no_kwargs(self):
        assert countries.search(name="Xyzzy Not A Place") == []
        assert countries.search() == []

    def test_records_without_a_usable_name_are_skipped(self, monkeypatch):
        """Guards for data that has no name to match against.

        Upstream has never shipped such a record, but an empty name would
        otherwise make the scoring raise on an empty sequence.
        """
        records = [
            ISONamespaceRecord({"alpha_2": "AA"}),
            ISONamespaceRecord({"alpha_2": "BB", "name": "---"}),
            ISONamespaceRecord({"alpha_2": "CC", "name": "Germany"}),
        ]
        monkeypatch.setattr(countries, "_namespace_records", records)
        assert [r.alpha_2 for r in countries.search_fuzzy("Germny")] == ["CC"]

    def test_works_on_other_standards(self):
        assert any(c.name == "Euro" for c in currencies.search(name="Euro"))


class TestAccessors:
    """The by_* views and name generators exist on every standard."""

    def test_country_index_dicts(self):
        assert countries.by_alpha_2_dict["FR"].name == "France"
        assert countries.by_alpha_3_dict["FRA"].alpha_2 == "FR"
        assert countries.by_numeric_dict["250"].alpha_2 == "FR"
        assert countries.by_name_dict["France"].alpha_2 == "FR"

    def test_index_dicts_are_copies(self):
        """Mutating the returned view must not corrupt the index."""
        view = countries.by_alpha_2_dict
        view.pop("FR")
        assert "FR" in countries.by_alpha_2_dict

    def test_former_countries(self):
        assert former_countries.by_alpha_4 != []
        assert former_countries.by_withdrawal_date != []
        assert dict(former_countries.name)

    def test_extended_languages(self):
        assert extended_languages.by_scope != []
        assert extended_languages.by_type != []
        assert dict(extended_languages.name)
        assert extended_languages.items != []

    def test_language_families(self):
        assert language_families.by_alpha_3 != []
        assert dict(language_families.name)
        assert language_families.items != []

    def test_script_names(self):
        assert script_names.by_alpha_4 != []
        assert script_names.by_numeric != []
        assert dict(script_names.name)
        assert script_names.items != []

    def test_subdivisions(self):
        assert subdivisions_countries.by_code != []
        assert subdivisions_countries.by_type != []
        assert dict(subdivisions_countries.name)

    def test_languages_and_currencies(self):
        assert languages.by_alpha_3 != []
        assert dict(languages.name)
        assert currencies.by_numeric != []
        assert dict(currencies.name)


class TestFormerNames:
    """Lookups for countries that were renamed or withdrawn."""

    def test_unmapped_former_code_returns_none(self):
        """A withdrawn country with no successor mapping has no current entry."""
        assert countries._get_current_country_from_former_codes("XX", "XXX") is None

    def test_rejects_non_string_and_empty(self):
        assert countries.get_by_former_name("") is None
        assert countries.get_by_former_name(None) is None
        assert countries.get_former_names_info("") is None
        assert countries.get_former_names_info(None) is None

    def test_known_rename(self):
        assert countries.get_by_former_name("Swaziland").name == "Eswatini"
        assert (
            countries.get_former_names_info("Swaziland")["current_name"] == "Eswatini"
        )

    def test_former_countries_sorted_views(self):
        assert former_countries.by_name != []
        assert former_countries.by_numeric != []


class TestSearchFuzzy:
    """search_fuzzy tolerates misspellings, but only as a fallback."""

    def test_correct_spelling_uses_the_exact_path(self):
        """A well-spelled query must never get an approximate answer."""
        assert [c.name for c in countries.search_fuzzy("Kingdom")] == ["United Kingdom"]

    def test_misspelling_is_recovered(self):
        assert "Germany" in [c.name for c in countries.search_fuzzy("Germny")]

    def test_transposition_is_recovered(self):
        names = [c.name for c in countries.search_fuzzy("Untied Kingdom")]
        assert names == ["United Kingdom"]

    def test_misspelled_word_within_a_phrase(self):
        """The case that motivated this: 'Repblic' should find the Republics."""
        names = [c.name for c in countries.search_fuzzy("Repblic")]
        assert names and all("Republic" in name for name in names)

    def test_nonsense_returns_nothing(self):
        assert countries.search_fuzzy("xyzzy not a place at all") == []

    def test_empty_query(self):
        assert countries.search_fuzzy("") == []
        assert countries.search_fuzzy("   ") == []

    def test_limit_is_honoured(self):
        assert len(countries.search_fuzzy("Repblic", limit=2)) == 2

    def test_cutoff_controls_strictness(self):
        loose = countries.search_fuzzy("Germny", cutoff=0.5)
        strict = countries.search_fuzzy("Germny", cutoff=0.95)
        assert len(loose) >= len(strict)

    def test_works_on_other_standards(self):
        """Also checks the tiebreak: several script names contain "Latin", and
        the bare word must outrank the longer names that merely include it."""
        assert script_names.search_fuzzy("Latinn")[0].name == "Latin"
