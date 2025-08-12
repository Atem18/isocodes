"""Data validation tests for the isocodes library."""

import re
from isocodes import (
    Countries,
    Languages,
    Currencies,
    SubdivisionsCountries,
    FormerCountries,
    ScriptNames,
)


class TestDataValidation:
    """Test that the data in the library meets expected standards."""

    def test_countries_data_validation(self):
        """Test that countries data is properly formatted."""
        countries = Countries("3166-1")

        for country_code, country_data in countries.by_alpha_2:
            # Alpha-2 codes should be exactly 2 uppercase letters
            assert len(country_code) == 2
            assert country_code.isupper()
            assert country_code.isalpha()

            # Country data should have required fields
            assert "name" in country_data
            assert "alpha_2" in country_data
            assert country_data["alpha_2"] == country_code

            # If alpha_3 exists, it should be 3 uppercase letters
            if "alpha_3" in country_data:
                assert len(country_data["alpha_3"]) == 3
                assert country_data["alpha_3"].isupper()
                assert country_data["alpha_3"].isalpha()

            # If numeric exists, it should be digits
            if "numeric" in country_data:
                assert country_data["numeric"].isdigit()
                assert len(country_data["numeric"]) == 3

    def test_languages_data_validation(self):
        """Test that languages data is properly formatted."""
        languages = Languages("639-2")

        for lang_code, lang_data in languages.by_alpha_3:
            # Alpha-3 codes should be at least 3 characters and lowercase
            assert len(lang_code) >= 3
            assert lang_code.islower()

            # Language data should have required fields
            assert "name" in lang_data
            assert "alpha_3" in lang_data
            assert lang_data["alpha_3"] == lang_code

            # If alpha_2 exists, it should be 2 lowercase letters
            if "alpha_2" in lang_data:
                assert len(lang_data["alpha_2"]) == 2
                assert lang_data["alpha_2"].islower()
                assert lang_data["alpha_2"].isalpha()

    def test_currencies_data_validation(self):
        """Test that currencies data is properly formatted."""
        currencies = Currencies("4217")

        for curr_code, curr_data in currencies.by_alpha_3:
            # Currency codes should be 3 uppercase letters
            assert len(curr_code) == 3
            assert curr_code.isupper()
            assert curr_code.isalpha()

            # Currency data should have required fields
            assert "name" in curr_data
            assert "alpha_3" in curr_data
            assert curr_data["alpha_3"] == curr_code

            # If numeric exists, it should be digits
            if "numeric" in curr_data:
                assert curr_data["numeric"].isdigit()

    def test_subdivisions_data_validation(self):
        """Test that subdivisions data is properly formatted."""
        subdivisions = SubdivisionsCountries("3166-2")

        for subdiv_code, subdiv_data in subdivisions.by_code:
            # Subdivision codes should follow pattern: CC-SUBDIVISION
            assert len(subdiv_code) >= 4  # At least CC-X
            assert "-" in subdiv_code

            country_code, subdivision_part = subdiv_code.split("-", 1)
            assert len(country_code) == 2
            assert country_code.isupper()
            assert country_code.isalpha()

            # Subdivision data should have required fields
            assert "name" in subdiv_data
            assert "code" in subdiv_data
            assert subdiv_data["code"] == subdiv_code

    def test_former_countries_data_validation(self):
        """Test that former countries data is properly formatted."""
        former_countries = FormerCountries("3166-3")

        for country in former_countries.items:
            # Should have name
            assert "name" in country

            # If withdrawal_date exists, it should be a valid date format
            if "withdrawal_date" in country:
                # Should be in YYYY-MM-DD format or similar
                date_pattern = r"\d{4}(-\d{2})?(-\d{2})?"
                assert re.match(date_pattern, country["withdrawal_date"])

    def test_script_names_data_validation(self):
        """Test that script names data is properly formatted."""
        script_names = ScriptNames("15924")

        for script_code, script_data in script_names.by_alpha_4:
            # Script codes should be 4 characters, first letter uppercase, rest lowercase
            assert len(script_code) == 4
            assert script_code[0].isupper()
            assert script_code[1:].islower() or script_code[1:].isdigit()

            # Script data should have required fields
            assert "name" in script_data
            assert "alpha_4" in script_data
            assert script_data["alpha_4"] == script_code

            # If numeric exists, it should be digits
            if "numeric" in script_data:
                assert script_data["numeric"].isdigit()

    def test_no_duplicate_codes(self):
        """Test that there are no duplicate codes within each dataset."""
        # Test countries
        countries = Countries("3166-1")
        alpha_2_codes = [item[0] for item in countries.by_alpha_2]
        assert len(alpha_2_codes) == len(set(alpha_2_codes))

        alpha_3_codes = [item[0] for item in countries.by_alpha_3]
        assert len(alpha_3_codes) == len(set(alpha_3_codes))

        # Test languages
        languages = Languages("639-2")
        lang_codes = [item[0] for item in languages.by_alpha_3]
        assert len(lang_codes) == len(set(lang_codes))

        # Test currencies
        currencies = Currencies("4217")
        curr_codes = [item[0] for item in currencies.by_alpha_3]
        assert len(curr_codes) == len(set(curr_codes))

    def test_data_completeness(self):
        """Test that essential data is present."""
        # Countries should include major countries
        countries = Countries("3166-1")
        us_found = any(country.get("alpha_2") == "US" for country in countries.items)
        gb_found = any(country.get("alpha_2") == "GB" for country in countries.items)
        assert us_found, "US should be in countries list"
        assert gb_found, "GB should be in countries list"

        # Languages should include major languages
        languages = Languages("639-2")
        eng_found = any(lang.get("alpha_3") == "eng" for lang in languages.items)
        fra_found = any(lang.get("alpha_3") == "fra" for lang in languages.items)
        assert eng_found, "English should be in languages list"
        assert fra_found, "French should be in languages list"

        # Currencies should include major currencies
        currencies = Currencies("4217")
        usd_found = any(curr.get("alpha_3") == "USD" for curr in currencies.items)
        eur_found = any(curr.get("alpha_3") == "EUR" for curr in currencies.items)
        assert usd_found, "USD should be in currencies list"
        assert eur_found, "EUR should be in currencies list"

    def test_data_consistency_across_properties(self):
        """Test that different property views return consistent data."""
        countries = Countries("3166-1")

        # Compare by_alpha_2 and by_name - should have same items (different order)
        alpha_2_items = {item[1]["alpha_2"]: item[1] for item in countries.by_alpha_2}
        name_items = {
            item[1]["alpha_2"]: item[1]
            for item in countries.by_name
            if "alpha_2" in item[1]
        }

        # All items in name_items should be in alpha_2_items
        for code, data in name_items.items():
            assert code in alpha_2_items
            assert alpha_2_items[code] == data

    def test_name_fields_not_empty(self):
        """Test that name fields are not empty."""
        countries = Countries("3166-1")
        for country in countries.items:
            if "name" in country:
                assert country["name"].strip() != ""
            if "official_name" in country:
                assert country["official_name"].strip() != ""
            if "common_name" in country:
                assert country["common_name"].strip() != ""

    def test_sorted_output_validity(self):
        """Test that sorted outputs are actually sorted."""
        countries = Countries("3166-1")

        # Test alpha_2 sorting
        alpha_2_codes = [item[0] for item in countries.by_alpha_2]
        assert alpha_2_codes == sorted(alpha_2_codes)

        # Test alpha_3 sorting
        alpha_3_codes = [item[0] for item in countries.by_alpha_3]
        assert alpha_3_codes == sorted(alpha_3_codes)

        # Test name sorting
        names = [item[0] for item in countries.by_name]
        assert names == sorted(names)

        # Test numeric sorting
        numeric_codes = [item[0] for item in countries.by_numeric]
        assert numeric_codes == sorted(numeric_codes)
