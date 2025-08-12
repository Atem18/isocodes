"""Edge cases and error handling tests for the isocodes library."""

import pytest
from isocodes import ISO, Countries, Languages


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_iso_key(self):
        """Test initialization with invalid ISO key."""
        with pytest.raises(Exception):
            # This should fail because the file doesn't exist
            ISO("invalid-key")

    def test_get_with_empty_dict(self):
        """Test get method with empty parameters."""
        countries = Countries("3166-1")

        # Should return empty dict for invalid searches
        result = countries.get()
        assert result == {}

    def test_get_with_none_values(self):
        """Test get method with None values."""
        countries = Countries("3166-1")

        # Should handle None values gracefully
        result = countries.get(alpha_2=None)
        assert result == {}

    def test_get_with_empty_string(self):
        """Test get method with empty string values."""
        countries = Countries("3166-1")

        # Should handle empty strings gracefully
        result = countries.get(alpha_2="")
        assert result == {}

    def test_get_with_invalid_types(self):
        """Test get method with invalid data types."""
        countries = Countries("3166-1")

        # Should handle non-string values gracefully
        result = countries.get(alpha_2=123)
        assert result == {}

        result = countries.get(alpha_2=[])
        assert result == {}

        result = countries.get(alpha_2={})
        assert result == {}

    def test_get_with_multiple_kwargs(self):
        """Test get method with multiple keyword arguments."""
        countries = Countries("3166-1")

        # Should only use the first key
        result = countries.get(alpha_2="US", alpha_3="USA")
        # Should find US by alpha_2 (first key)
        assert result.get("alpha_2") == "US"

    def test_partial_string_matching(self):
        """Test that get method does partial string matching."""
        countries = Countries("3166-1")

        # Search for partial name match
        result = countries.get(name="United")
        assert isinstance(result, dict)
        # Should find a country with "United" in the name
        assert "United" in result.get("name", "") or "United" in result.get(
            "official_name", ""
        )

    def test_case_sensitivity(self):
        """Test case sensitivity in searches."""
        countries = Countries("3166-1")

        # Uppercase should work for codes
        result_upper = countries.get(alpha_2="US")
        assert result_upper.get("alpha_2") == "US"

        # Lowercase should not work for country codes (they're uppercase)
        result_lower = countries.get(alpha_2="us")
        assert result_lower == {}

    def test_empty_data_handling(self):
        """Test handling of items with missing optional fields."""
        countries = Countries("3166-1")

        # Find a country and check it handles missing optional fields gracefully
        for country in countries.items:
            # These should not raise errors even if fields are missing
            _ = country.get("alpha_2", "")
            _ = country.get("alpha_3", "")
            name = country.get("name", "")

            # At minimum, should have a name
            assert name != ""

    def test_generator_exhaustion(self):
        """Test that name generators can be consumed multiple times."""
        countries = Countries("3166-1")

        # First consumption
        names1 = list(countries.name)
        assert len(names1) > 0

        # Second consumption (should get fresh generator)
        names2 = list(countries.name)
        assert len(names2) > 0
        assert len(names1) == len(names2)

    def test_large_dataset_edge_cases(self):
        """Test edge cases with large datasets."""
        # Use the largest dataset (subdivisions)
        from isocodes import SubdivisionsCountries

        subdivisions = SubdivisionsCountries("3166-2")

        # Should handle large datasets without issues
        assert len(subdivisions) > 1000

        # Should be able to sort large datasets
        by_code = subdivisions.by_code
        assert len(by_code) > 1000

        # First and last items should be properly sorted
        assert by_code[0][0] <= by_code[-1][0]

    def test_special_characters_in_names(self):
        """Test handling of special characters in names."""
        countries = Countries("3166-1")

        # Find countries with special characters
        special_char_countries = [
            country
            for country in countries.items
            if any(char in country.get("name", "") for char in "áéíóúàèìòùâêîôûäëïöüñç")
        ]

        # Should have some countries with special characters
        assert len(special_char_countries) > 0

        # Should handle them properly in sorting
        by_name = countries.by_name
        assert len(by_name) > 0

    def test_unicode_handling(self):
        """Test Unicode character handling."""
        countries = Countries("3166-1")

        # Check that flag emojis are handled properly
        countries_with_flags = [
            country
            for country in countries.items
            if "flag" in country and country["flag"]
        ]

        # Should have countries with flag emojis
        assert len(countries_with_flags) > 0

        # Flags should be Unicode characters
        for country in countries_with_flags[:5]:  # Check first 5
            flag = country["flag"]
            # Should be Unicode emoji
            assert len(flag.encode()) > len(flag)  # Unicode chars take more bytes

    def test_numeric_string_handling(self):
        """Test handling of numeric codes as strings."""
        countries = Countries("3166-1")

        # Get countries with numeric codes
        countries_with_numeric = [
            country for country in countries.items if "numeric" in country
        ]

        assert len(countries_with_numeric) > 0

        # Numeric codes should be strings of digits
        for country in countries_with_numeric:
            numeric = country["numeric"]
            assert isinstance(numeric, str)
            assert numeric.isdigit()


class TestBoundaryConditions:
    """Test boundary conditions and limits."""

    def test_shortest_and_longest_names(self):
        """Test handling of shortest and longest country names."""
        countries = Countries("3166-1")

        names = [country["name"] for country in countries.items if "name" in country]

        # Should have names of varying lengths
        shortest = min(names, key=len)
        longest = max(names, key=len)

        # Shortest should be at least 2 characters
        assert len(shortest) >= 2
        # Longest should be reasonable (less than 100 chars)
        assert len(longest) < 100

    def test_code_boundaries(self):
        """Test handling of code boundaries."""
        countries = Countries("3166-1")

        # Test first and last alphabetically
        by_alpha_2 = countries.by_alpha_2
        assert len(by_alpha_2) > 0

        first_code = by_alpha_2[0][0]
        last_code = by_alpha_2[-1][0]

        # Should be proper 2-letter codes
        assert len(first_code) == 2
        assert len(last_code) == 2
        assert first_code < last_code  # Alphabetical order

    def test_empty_optional_fields(self):
        """Test items with empty optional fields."""
        languages = Languages("639-2")

        # Some languages might not have alpha_2 codes
        languages_without_alpha_2 = [
            lang for lang in languages.items if "alpha_2" not in lang
        ]

        # Should handle these gracefully
        for lang in languages_without_alpha_2[:5]:  # Check first 5
            assert "alpha_3" in lang
            assert "name" in lang
            assert lang["name"] != ""

    def test_data_type_consistency(self):
        """Test that data types are consistent."""
        countries = Countries("3166-1")

        for country in countries.items:
            # All values should be strings
            for key, value in country.items():
                assert isinstance(value, str), (
                    f"Value for {key} should be string, got {type(value)}"
                )

            # Required fields should exist and be non-empty
            assert "name" in country
            assert isinstance(country["name"], str)
            assert country["name"].strip() != ""
