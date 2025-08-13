from isocodes import Countries, countries


class TestFormerNamesLookup:
    """Test the former names lookup functionality."""

    def test_get_by_former_name_swaziland(self):
        """Test looking up Eswatini by its former name Swaziland."""
        result = countries.get_by_former_name("Swaziland")
        assert result is not None
        assert result.alpha_2 == "SZ"
        assert result.alpha_3 == "SWZ"
        assert result.name == "Eswatini"

    def test_get_by_former_name_burma(self):
        """Test looking up Myanmar by its former name Burma (from ISO 3166-3)."""
        result = countries.get_by_former_name("Burma")
        assert result is not None
        assert result.alpha_2 == "MM"
        assert result.alpha_3 == "MMR"
        assert result.name == "Myanmar"

    def test_get_by_former_name_zaire(self):
        """Test looking up Congo (DRC) by its former name Zaire (from ISO 3166-3)."""
        result = countries.get_by_former_name("Zaire")
        assert result is not None
        assert result.alpha_2 == "CD"
        assert result.alpha_3 == "COD"

    def test_get_by_former_name_nonexistent(self):
        """Test looking up a non-existent former name."""
        result = countries.get_by_former_name("Atlantis")
        assert result is None

    def test_get_by_former_name_empty_string(self):
        """Test looking up with empty string."""
        result = countries.get_by_former_name("")
        assert result is None

    def test_get_by_former_name_none(self):
        """Test looking up with None."""
        result = countries.get_by_former_name(None)
        assert result is None

    def test_get_former_names_info_swaziland(self):
        """Test getting detailed info about Swaziland."""
        result = countries.get_former_names_info("Swaziland")
        assert result is not None
        assert result["alpha_2"] == "SZ"
        assert result["alpha_3"] == "SWZ"
        assert result["current_name"] == "Eswatini"
        assert result["change_date"] == "2018-04-19"
        assert "Name change" in result["comment"]

    def test_get_former_names_info_burma(self):
        """Test getting detailed info about Burma from ISO 3166-3."""
        result = countries.get_former_names_info("Burma")
        assert result is not None
        assert result["alpha_2"] == "BU"
        assert result["alpha_3"] == "BUR"
        assert result["current_name"] == "Myanmar"
        assert "1989" in result["change_date"]

    def test_get_former_names_info_nonexistent(self):
        """Test getting info for non-existent former name."""
        result = countries.get_former_names_info("Atlantis")
        assert result is None

    def test_former_names_property(self):
        """Test the former_names property."""
        former_names = countries.former_names
        assert isinstance(former_names, list)
        assert "Swaziland" in former_names
        # Should also include names from ISO 3166-3
        assert "Burma" in former_names or any("Burma" in name for name in former_names)

    def test_case_sensitivity(self):
        """Test that former name lookup is case sensitive."""
        result = countries.get_by_former_name("swaziland")  # lowercase
        assert result is None

        result = countries.get_by_former_name("SWAZILAND")  # uppercase
        assert result is None

        result = countries.get_by_former_name("Swaziland")  # correct case
        assert result is not None

    def test_partial_matches_not_supported(self):
        """Test that partial matches are not supported."""
        result = countries.get_by_former_name("Swazi")
        assert result is None

    def test_countries_instance_has_former_names_data(self):
        """Test that Countries instance loads former names data."""
        test_countries = Countries("3166-1")
        assert hasattr(test_countries, "_former_names_data")
        assert isinstance(test_countries._former_names_data, dict)
        assert len(test_countries._former_names_data) > 0

    def test_integration_with_existing_get_method(self):
        """Test that the new functionality doesn't break existing get method."""
        # Test existing functionality still works
        result = countries.get(alpha_2="US")
        assert result is not None
        assert result.name == "United States"

        # Test new functionality works alongside
        result = countries.get_by_former_name("Swaziland")
        assert result is not None
        assert result.name == "Eswatini"
