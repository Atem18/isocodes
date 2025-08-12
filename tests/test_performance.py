"""Performance tests for the isocodes library."""

import time
from isocodes import (
    Countries,
    Languages,
    SubdivisionsCountries,
    ExtendedLanguages,
)


class TestPerformance:
    """Test performance characteristics of the library."""

    def test_countries_initialization_performance(self):
        """Test that Countries initialization is reasonably fast."""
        start_time = time.time()
        countries = Countries("3166-1")
        end_time = time.time()

        assert len(countries) > 0
        # Should initialize in less than 1 second
        assert (end_time - start_time) < 1.0

    def test_languages_initialization_performance(self):
        """Test that Languages initialization is reasonably fast."""
        start_time = time.time()
        languages = Languages("639-2")
        end_time = time.time()

        assert len(languages) > 0
        # Should initialize in less than 1 second
        assert (end_time - start_time) < 1.0

    def test_multiple_get_operations_performance(self):
        """Test performance of multiple get operations."""
        countries = Countries("3166-1")

        start_time = time.time()

        # Perform multiple lookups
        for _ in range(100):
            countries.get(alpha_2="US")
            countries.get(alpha_2="GB")
            countries.get(alpha_2="CA")
            countries.get(alpha_2="FR")
            countries.get(alpha_2="DE")

        end_time = time.time()

        # 500 lookups should complete in less than 1 second
        assert (end_time - start_time) < 1.0

    def test_sorting_operations_performance(self):
        """Test performance of sorting operations."""
        countries = Countries("3166-1")

        start_time = time.time()

        # Access sorted properties multiple times
        for _ in range(10):
            _ = countries.by_alpha_2
            _ = countries.by_alpha_3
            _ = countries.by_name
            _ = countries.by_numeric

        end_time = time.time()

        # Should complete in reasonable time
        assert (end_time - start_time) < 2.0

    def test_large_dataset_handling(self):
        """Test handling of the largest dataset (subdivisions)."""
        subdivisions = SubdivisionsCountries("3166-2")

        # This is typically the largest dataset
        assert len(subdivisions) > 1000

        start_time = time.time()
        sorted_by_code = subdivisions.by_code
        end_time = time.time()

        assert len(sorted_by_code) > 1000
        # Should sort large dataset in reasonable time
        assert (end_time - start_time) < 2.0

    def test_extended_languages_performance(self):
        """Test performance with extended languages (large dataset)."""
        extended_languages = ExtendedLanguages("639-3")

        # This is also a large dataset
        assert len(extended_languages) > 1000

        start_time = time.time()

        # Test multiple operations
        _ = extended_languages.by_alpha_3
        _ = extended_languages.by_name
        _ = extended_languages.by_scope
        _ = extended_languages.by_type

        end_time = time.time()

        # Should complete all operations in reasonable time
        assert (end_time - start_time) < 3.0
