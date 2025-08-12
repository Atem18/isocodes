import pytest
from isocodes import (
    Countries,
    Languages,
    Currencies,
    SubdivisionsCountries,
    FormerCountries,
    ExtendedLanguages,
    LanguageFamilies,
    ScriptNames,
    ISO,
    countries,
    languages,
    currencies,
    subdivisions_countries,
    former_countries,
    extendend_languages,
    language_families,
    script_names,
)


# Test fixtures for class instances
@pytest.fixture
def countries_instance():
    return Countries("3166-1")


@pytest.fixture
def languages_instance():
    return Languages("639-2")


@pytest.fixture
def currencies_instance():
    return Currencies("4217")


@pytest.fixture
def subdivisions_countries_instance():
    return SubdivisionsCountries("3166-2")


@pytest.fixture
def former_countries_instance():
    return FormerCountries("3166-3")


@pytest.fixture
def extended_languages_instance():
    return ExtendedLanguages("639-3")


@pytest.fixture
def language_families_instance():
    return LanguageFamilies("639-5")


@pytest.fixture
def script_names_instance():
    return ScriptNames("15924")


# Test ISO base class
class TestISO:
    def test_iso_initialization(self):
        """Test that ISO class initializes correctly"""
        iso = ISO("3166-1")
        assert iso.iso_key == "3166-1"
        assert isinstance(iso.data, list)
        assert len(iso.data) > 0

    def test_iso_len(self):
        """Test __len__ method"""
        iso = ISO("3166-1")
        assert len(iso) == len(iso.data)

    def test_iso_items(self):
        """Test items property"""
        iso = ISO("3166-1")
        assert iso.items == iso.data
        assert isinstance(iso.items, list)

    def test_iso_get_method(self):
        """Test get method with various parameters"""
        iso = ISO("3166-1")

        # Test getting by alpha_2
        result = iso.get(alpha_2="US")
        assert isinstance(result, dict)
        assert result.get("alpha_2") == "US"
        assert "name" in result

        # Test non-existent key
        result = iso.get(alpha_2="ZZ")
        assert result == {}

        # Test partial match (should return first occurrence)
        result = iso.get(name="United")
        assert isinstance(result, dict)


# Test Countries class
class TestCountries:
    def test_countries_initialization(self, countries_instance):
        """Test Countries class initialization"""
        assert countries_instance.iso_key == "3166-1"
        assert len(countries_instance) > 0

    def test_countries_by_alpha_2(self, countries_instance):
        """Test by_alpha_2 property"""
        result = countries_instance.by_alpha_2
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
        assert all(len(item[0]) == 2 for item in result)  # alpha_2 codes are 2 chars

        # Test sorting
        alpha_codes = [item[0] for item in result]
        assert alpha_codes == sorted(alpha_codes)

    def test_countries_by_alpha_3(self, countries_instance):
        """Test by_alpha_3 property"""
        result = countries_instance.by_alpha_3
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
        assert all(len(item[0]) == 3 for item in result)  # alpha_3 codes are 3 chars

        # Test sorting
        alpha_codes = [item[0] for item in result]
        assert alpha_codes == sorted(alpha_codes)

    def test_countries_by_name(self, countries_instance):
        """Test by_name property"""
        result = countries_instance.by_name
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

        # Test sorting
        names = [item[0] for item in result]
        assert names == sorted(names)

    def test_countries_by_numeric(self, countries_instance):
        """Test by_numeric property"""
        result = countries_instance.by_numeric
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
        assert all(item[0].isdigit() for item in result)  # numeric codes are digits

    def test_countries_by_common_name(self, countries_instance):
        """Test by_common_name property"""
        result = countries_instance.by_common_name
        assert isinstance(result, list)
        # Note: not all countries have common names, so this might be empty or partial

    def test_countries_name_generator(self, countries_instance):
        """Test name generator property"""
        result = list(countries_instance.name)
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_countries_get_specific_country(self, countries_instance):
        """Test getting specific countries"""
        # Test US
        us = countries_instance.get(alpha_2="US")
        assert us["alpha_2"] == "US"
        assert us["alpha_3"] == "USA"
        assert us["name"] == "United States"  # The common name, not official name
        assert (
            us["official_name"] == "United States of America"
        )  # This is the official name
        assert "numeric" in us

        # Test UK
        gb = countries_instance.get(alpha_2="GB")
        assert gb["alpha_2"] == "GB"
        assert gb["alpha_3"] == "GBR"

        # Test by alpha_3
        usa = countries_instance.get(alpha_3="USA")
        assert usa["alpha_2"] == "US"

    def test_countries_items_type(self, countries_instance):
        """Test that items returns proper Country type"""
        items = countries_instance.items
        assert isinstance(items, list)
        assert len(items) > 0

        # Check that each item has expected country fields
        sample_country = items[0]
        assert "name" in sample_country
        assert "alpha_2" in sample_country or "alpha_3" in sample_country


# Test Languages class
class TestLanguages:
    def test_languages_initialization(self, languages_instance):
        """Test Languages class initialization"""
        assert languages_instance.iso_key == "639-2"
        assert len(languages_instance) > 0

    def test_languages_by_alpha_3(self, languages_instance):
        """Test by_alpha_3 property"""
        result = languages_instance.by_alpha_3
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
        # Most alpha_3 codes are 3 chars, but there are some reserved ranges that are longer
        assert all(
            len(item[0]) >= 3 for item in result
        )  # alpha_3 codes are at least 3 chars

    def test_languages_by_name(self, languages_instance):
        """Test by_name property"""
        result = languages_instance.by_name
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_languages_get_specific_language(self, languages_instance):
        """Test getting specific languages"""
        # Test English
        eng = languages_instance.get(alpha_3="eng")
        assert eng["alpha_3"] == "eng"
        assert eng["name"] == "English"

        # Test language with alpha_2
        if "alpha_2" in eng:
            assert eng["alpha_2"] == "en"

    def test_languages_name_generator(self, languages_instance):
        """Test name generator property"""
        result = list(languages_instance.name)
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)


# Test Currencies class
class TestCurrencies:
    def test_currencies_initialization(self, currencies_instance):
        """Test Currencies class initialization"""
        assert currencies_instance.iso_key == "4217"
        assert len(currencies_instance) > 0

    def test_currencies_by_alpha_3(self, currencies_instance):
        """Test by_alpha_3 property"""
        result = currencies_instance.by_alpha_3
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
        assert all(len(item[0]) == 3 for item in result)  # currency codes are 3 chars

    def test_currencies_by_name(self, currencies_instance):
        """Test by_name property"""
        result = currencies_instance.by_name
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_currencies_by_numeric(self, currencies_instance):
        """Test by_numeric property"""
        result = currencies_instance.by_numeric
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_currencies_get_specific_currency(self, currencies_instance):
        """Test getting specific currencies"""
        # Test USD
        usd = currencies_instance.get(alpha_3="USD")
        assert usd["alpha_3"] == "USD"
        assert "US Dollar" in usd["name"]

        # Test EUR
        eur = currencies_instance.get(alpha_3="EUR")
        assert eur["alpha_3"] == "EUR"
        assert "Euro" in eur["name"]


# Test SubdivisionsCountries class
class TestSubdivisionsCountries:
    def test_subdivisions_initialization(self, subdivisions_countries_instance):
        """Test SubdivisionsCountries class initialization"""
        assert subdivisions_countries_instance.iso_key == "3166-2"
        assert len(subdivisions_countries_instance) > 0

    def test_subdivisions_by_code(self, subdivisions_countries_instance):
        """Test by_code property"""
        result = subdivisions_countries_instance.by_code
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_subdivisions_by_name(self, subdivisions_countries_instance):
        """Test by_name property"""
        result = subdivisions_countries_instance.by_name
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_subdivisions_by_type(self, subdivisions_countries_instance):
        """Test by_type property"""
        result = subdivisions_countries_instance.by_type
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)


# Test FormerCountries class
class TestFormerCountries:
    def test_former_countries_initialization(self, former_countries_instance):
        """Test FormerCountries class initialization"""
        assert former_countries_instance.iso_key == "3166-3"
        assert len(former_countries_instance) > 0

    def test_former_countries_by_alpha_2(self, former_countries_instance):
        """Test by_alpha_2 property"""
        result = former_countries_instance.by_alpha_2
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_former_countries_by_alpha_3(self, former_countries_instance):
        """Test by_alpha_3 property"""
        result = former_countries_instance.by_alpha_3
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_former_countries_by_alpha_4(self, former_countries_instance):
        """Test by_alpha_4 property"""
        result = former_countries_instance.by_alpha_4
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_former_countries_by_withdrawal_date(self, former_countries_instance):
        """Test by_withdrawal_date property"""
        result = former_countries_instance.by_withdrawal_date
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)


# Test ExtendedLanguages class
class TestExtendedLanguages:
    def test_extended_languages_initialization(self, extended_languages_instance):
        """Test ExtendedLanguages class initialization"""
        assert extended_languages_instance.iso_key == "639-3"
        assert len(extended_languages_instance) > 0

    def test_extended_languages_by_alpha_3(self, extended_languages_instance):
        """Test by_alpha_3 property"""
        result = extended_languages_instance.by_alpha_3
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_extended_languages_by_scope(self, extended_languages_instance):
        """Test by_scope property"""
        result = extended_languages_instance.by_scope
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_extended_languages_by_type(self, extended_languages_instance):
        """Test by_type property"""
        result = extended_languages_instance.by_type
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)


# Test LanguageFamilies class
class TestLanguageFamilies:
    def test_language_families_initialization(self, language_families_instance):
        """Test LanguageFamilies class initialization"""
        assert language_families_instance.iso_key == "639-5"
        assert len(language_families_instance) > 0

    def test_language_families_by_alpha_3(self, language_families_instance):
        """Test by_alpha_3 property"""
        result = language_families_instance.by_alpha_3
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_language_families_by_name(self, language_families_instance):
        """Test by_name property"""
        result = language_families_instance.by_name
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)


# Test ScriptNames class
class TestScriptNames:
    def test_script_names_initialization(self, script_names_instance):
        """Test ScriptNames class initialization"""
        assert script_names_instance.iso_key == "15924"
        assert len(script_names_instance) > 0

    def test_script_names_by_alpha_4(self, script_names_instance):
        """Test by_alpha_4 property"""
        result = script_names_instance.by_alpha_4
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
        assert all(len(item[0]) == 4 for item in result)  # script codes are 4 chars

    def test_script_names_by_name(self, script_names_instance):
        """Test by_name property"""
        result = script_names_instance.by_name
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)

    def test_script_names_by_numeric(self, script_names_instance):
        """Test by_numeric property"""
        result = script_names_instance.by_numeric
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)


# Test module-level instances
class TestModuleLevelInstances:
    def test_countries_instance(self):
        """Test the module-level countries instance"""
        assert isinstance(countries, Countries)
        assert countries.iso_key == "3166-1"
        assert len(countries) > 0

    def test_languages_instance(self):
        """Test the module-level languages instance"""
        assert isinstance(languages, Languages)
        assert languages.iso_key == "639-2"
        assert len(languages) > 0

    def test_currencies_instance(self):
        """Test the module-level currencies instance"""
        assert isinstance(currencies, Currencies)
        assert currencies.iso_key == "4217"
        assert len(currencies) > 0

    def test_subdivisions_countries_instance(self):
        """Test the module-level subdivisions_countries instance"""
        assert isinstance(subdivisions_countries, SubdivisionsCountries)
        assert subdivisions_countries.iso_key == "3166-2"
        assert len(subdivisions_countries) > 0

    def test_former_countries_instance(self):
        """Test the module-level former_countries instance"""
        assert isinstance(former_countries, FormerCountries)
        assert former_countries.iso_key == "3166-3"
        assert len(former_countries) > 0

    def test_extended_languages_instance(self):
        """Test the module-level extendend_languages instance"""
        assert isinstance(extendend_languages, ExtendedLanguages)
        assert extendend_languages.iso_key == "639-3"
        assert len(extendend_languages) > 0

    def test_language_families_instance(self):
        """Test the module-level language_families instance"""
        assert isinstance(language_families, LanguageFamilies)
        assert language_families.iso_key == "639-5"
        assert len(language_families) > 0

    def test_script_names_instance(self):
        """Test the module-level script_names instance"""
        assert isinstance(script_names, ScriptNames)
        assert script_names.iso_key == "15924"
        assert len(script_names) > 0


# Integration tests
class TestIntegration:
    def test_cross_reference_countries_currencies(self):
        """Test cross-referencing countries with their currencies"""
        # Get USA
        usa = countries.get(alpha_2="US")
        assert usa["alpha_2"] == "US"

        # Check USD exists
        usd = currencies.get(alpha_3="USD")
        assert usd["alpha_3"] == "USD"

    def test_cross_reference_countries_subdivisions(self):
        """Test cross-referencing countries with their subdivisions"""
        # Get some US subdivisions
        us_subdivisions = [
            item
            for item in subdivisions_countries.items
            if item.get("code", "").startswith("US-")
        ]
        assert len(us_subdivisions) > 0

        # Verify they all belong to US
        for subdivision in us_subdivisions:
            assert subdivision["code"].startswith("US-")

    def test_data_consistency(self):
        """Test data consistency across different ISO standards"""
        # Ensure all data sets are non-empty
        assert len(countries) > 0
        assert len(languages) > 0
        assert len(currencies) > 0
        assert len(subdivisions_countries) > 0
        assert len(former_countries) > 0
        assert len(extendend_languages) > 0
        assert len(language_families) > 0
        assert len(script_names) > 0

    def test_sorted_properties(self):
        """Test that all 'by_*' properties return sorted results"""
        # Test countries
        alpha_2_codes = [item[0] for item in countries.by_alpha_2]
        assert alpha_2_codes == sorted(alpha_2_codes)

        alpha_3_codes = [item[0] for item in countries.by_alpha_3]
        assert alpha_3_codes == sorted(alpha_3_codes)

        # Test languages
        lang_codes = [item[0] for item in languages.by_alpha_3]
        assert lang_codes == sorted(lang_codes)

        # Test currencies
        curr_codes = [item[0] for item in currencies.by_alpha_3]
        assert curr_codes == sorted(curr_codes)


# Edge cases and error handling
class TestEdgeCases:
    def test_get_with_nonexistent_keys(self):
        """Test get method with non-existent keys"""
        result = countries.get(alpha_2="ZZ")
        assert result == {}

        result = languages.get(alpha_3="zzz")
        assert result == {}

        result = currencies.get(alpha_3="ZZZ")
        assert result == {}

    def test_get_with_invalid_parameters(self):
        """Test get method with invalid parameters"""
        result = countries.get(invalid_key="test")
        assert result == {}

    def test_empty_search_results(self):
        """Test handling of empty search results"""
        # Test with a key that doesn't exist in any record
        result = countries.get(nonexistent_field="test")
        assert result == {}

    def test_name_generators_are_iterators(self):
        """Test that name properties return generators/iterators"""
        country_names = countries.name
        # Should be a generator
        assert hasattr(country_names, "__iter__")
        assert hasattr(country_names, "__next__")

        # Convert to list and verify content
        name_list = list(countries.name)  # Create fresh generator
        assert len(name_list) > 0
        assert all(isinstance(item, tuple) and len(item) == 2 for item in name_list)
