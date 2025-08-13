import json
import pathlib
import os
import sys
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Tuple, TypedDict

if TYPE_CHECKING:
    import importlib.resources.abc


class Country(TypedDict, total=False):
    alpha_2: str
    alpha_3: str
    common_name: str
    flag: str
    name: str
    numeric: str
    official_name: str


class Language(TypedDict, total=False):
    alpha_2: str
    alpha_3: str
    bibliographic: str
    common_name: str
    name: str


class Currency(TypedDict, total=False):
    alpha_3: str
    name: str
    numeric: str


class CountrySubdivision(TypedDict, total=False):
    code: str
    name: str
    parent: str
    type: str


class FormerCountry(TypedDict, total=False):
    alpha_2: str
    alpha_3: str
    alpha_4: str
    comment: str
    name: str
    numeric: str
    withdrawal_date: str


class ExtendedLanguage(TypedDict, total=False):
    alpha_2: str
    alpha_3: str
    bibliographic: str
    common_name: str
    inverted_name: str
    name: str
    scope: str
    type: str


class LanguageFamily(TypedDict, total=False):
    alpha_3: str
    name: str


class ScriptName(TypedDict, total=False):
    alpha_4: str
    name: str
    numeric: str


class FormerNameMapping(TypedDict, total=False):
    alpha_2: Optional[str]
    alpha_3: Optional[str]
    current_name: Optional[str]
    change_date: str
    comment: Optional[str]


class ISONamespaceRecord(dict):
    """
    A dict-based record that provides dot notation access via SimpleNamespace
    while maintaining complete dictionary compatibility.

    This class ensures that existing code using dictionary access
    continues to work unchanged while enabling modern dot notation.

    Example:
        record = ISONamespaceRecord({"alpha_2": "US", "name": "United States"})

        # Dictionary access (backward compatible)
        print(record["name"])  # United States
        print(record.get("alpha_2"))  # US
        print(isinstance(record, dict))  # True

        # Dot notation access (new feature)
        print(record.name)  # United States
        print(record.alpha_2)  # US
    """

    def __init__(self, data: Dict[str, Any]):
        """Initialize with dictionary data."""
        # Initialize as a dictionary
        super().__init__(data)

        # Create a SimpleNamespace for dot notation access
        self._namespace = SimpleNamespace(**data)

    def __getattr__(self, name: str) -> Any:
        """Support dot notation access."""
        if name.startswith("_"):
            # Handle private attributes normally
            return object.__getattribute__(self, name)
        try:
            return getattr(self._namespace, name)
        except AttributeError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )

    def __setattr__(self, name: str, value: Any) -> None:
        """Support attribute assignment while keeping dict in sync."""
        if name.startswith("_"):
            # Private attributes go directly to the object
            super().__setattr__(name, value)
        else:
            # Public attributes should update both the dict and the namespace
            self[name] = value
            if hasattr(self, "_namespace"):
                setattr(self._namespace, name, value)

    def __setitem__(self, key: str, value: Any) -> None:
        """Override dict setitem to keep namespace in sync."""
        super().__setitem__(key, value)
        if hasattr(self, "_namespace"):
            setattr(self._namespace, key, value)

    def __delitem__(self, key: str) -> None:
        """Override dict delitem to keep namespace in sync."""
        super().__delitem__(key)
        if hasattr(self, "_namespace") and hasattr(self._namespace, key):
            delattr(self._namespace, key)

    def update(self, *args, **kwargs) -> None:
        """Override dict update to keep namespace in sync."""
        super().update(*args, **kwargs)
        if hasattr(self, "_namespace"):
            # Update namespace with current dict contents
            for key, value in self.items():
                setattr(self._namespace, key, value)

    def clear(self) -> None:
        """Override dict clear to keep namespace in sync."""
        super().clear()
        if hasattr(self, "_namespace"):
            # Clear namespace attributes
            for attr in list(vars(self._namespace).keys()):
                delattr(self._namespace, attr)

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"{self.__class__.__name__}({dict(self)})"


# Remove the MutableMapping registration since we now inherit from dict


def get_resource(resource: str) -> "importlib.resources.abc.Traversable":
    """Return a file handle on a named resource in a Package."""

    # Attempt importlib.resources
    if sys.version_info >= (3, 9):
        import importlib.resources

        return importlib.resources.files("isocodes").joinpath(resource)

    # Attempt importlib_resources backport
    try:
        if sys.version_info < (3, 9):
            import importlib_resources

            return importlib_resources.files("isocodes").joinpath(resource)
    except ImportError:
        ...

    # Fall back to __file__.
    # Undefined __file__ will raise NameError on variable access.
    try:
        package_path = os.path.abspath(os.path.dirname(__file__))
    except NameError:
        package_path = None

    if package_path is not None:
        resource_path = os.path.join(package_path, resource)

        return pathlib.Path(resource_path)

    # Could not resolve package path from __file__.
    raise Exception(f"do not know how to load resource: {resource}")


class ISO:
    iso_key: str
    data: List[Dict[str, str]]

    def __init__(self, iso_key: str) -> None:
        self.iso_key = iso_key
        resource_file = get_resource(f"share/iso-codes/json/iso_{self.iso_key}.json")
        with resource_file.open(encoding="utf-8") as iso_file:
            self.data = json.load(iso_file)[self.iso_key]

        # Create enhanced records with dot notation support
        self._namespace_records = [ISONamespaceRecord(item) for item in self.data]

        # Create efficient indexes for fast lookups
        self._create_indexes()

    def _create_indexes(self):
        """Create indexed access for common fields."""
        self._index_alpha_2 = {}
        self._index_alpha_3 = {}
        self._index_name = {}
        self._index_numeric = {}

        for record in self._namespace_records:
            if hasattr(record, "alpha_2"):
                self._index_alpha_2[record.alpha_2] = record
            if hasattr(record, "alpha_3"):
                self._index_alpha_3[record.alpha_3] = record
            if hasattr(record, "name"):
                self._index_name[record.name] = record
            if hasattr(record, "numeric"):
                self._index_numeric[record.numeric] = record

    def __len__(self) -> int:
        return len(self.data)

    def _name_from_index(self, index: str) -> Generator[Any, None, None]:
        return ((element[index], element["name"]) for element in self.data)

    def _sorted_by_index(self, index: str) -> List[Tuple[str, ISONamespaceRecord]]:
        """Return sorted list of (index_value, record) tuples using enhanced records."""
        return sorted(
            [
                (getattr(record, index), record)
                for record in self._namespace_records
                if hasattr(record, index)
            ],
            key=lambda x: x[0],
        )

    def get(self, **kwargs: str) -> ISONamespaceRecord:
        """
        Enhanced get method that returns ISONamespaceRecord objects.
        Maintains backward compatibility with the original API.

        Returns empty ISONamespaceRecord for non-matching cases to maintain consistency,
        but ISONamespaceRecord objects are dict-compatible for existing code.
        """
        try:
            # Handle empty kwargs - return empty ISONamespaceRecord for backward compatibility
            if not kwargs:
                return ISONamespaceRecord({})

            key: str = next(iter(kwargs))
            value = kwargs[key]

            # Handle None or empty values - return empty ISONamespaceRecord for backward compatibility
            if value is None or value == "":
                return ISONamespaceRecord({})

            # Ensure value is a string - return empty ISONamespaceRecord for backward compatibility
            if not isinstance(value, str):
                return ISONamespaceRecord({})

            # Find the matching record in original data
            base_result = [
                element
                for element in self.data
                if key in element and value in element[key]
            ][0]

            # Find the corresponding namespace record
            for record in self._namespace_records:
                if dict(record) == base_result:
                    return record

            # Fallback: create a new one (shouldn't happen normally)
            return ISONamespaceRecord(base_result)

        except (IndexError, StopIteration, TypeError):
            return ISONamespaceRecord({})

    def find(self, **kwargs: str) -> Optional[ISONamespaceRecord]:
        """
        New method for exact match lookups using indexes for better performance.

        Example:
            country = countries.find(alpha_2="US")
            print(country.name)  # United States
        """
        if not kwargs:
            return None

        # Try indexed lookups first for common fields
        for key, value in kwargs.items():
            if key == "alpha_2" and value in self._index_alpha_2:
                return self._index_alpha_2[value]
            elif key == "alpha_3" and value in self._index_alpha_3:
                return self._index_alpha_3[value]
            elif key == "name" and value in self._index_name:
                return self._index_name[value]
            elif key == "numeric" and value in self._index_numeric:
                return self._index_numeric[value]

        # Fallback to linear search for exact matches
        for record in self._namespace_records:
            if all(
                hasattr(record, k) and getattr(record, k) == v
                for k, v in kwargs.items()
            ):
                return record

        return None

    def search(self, **kwargs: str) -> List[ISONamespaceRecord]:
        """
        Search for records that match criteria (supports partial matches).

        Example:
            island_countries = countries.search(name="Island")
            for country in island_countries:
                print(f"{country.name} - {country.flag}")
        """
        if not kwargs:
            return []

        results = []
        for record in self._namespace_records:
            match = True
            for key, value in kwargs.items():
                if not hasattr(record, key):
                    match = False
                    break
                record_value = str(getattr(record, key))
                if value.lower() not in record_value.lower():
                    match = False
                    break
            if match:
                results.append(record)

        return results

    @property
    def items(self) -> List[ISONamespaceRecord]:
        """Return all records as ISONamespaceRecord objects with dot notation support."""
        return self._namespace_records

    # Enhanced index access properties
    @property
    def by_alpha_2_dict(self) -> Dict[str, ISONamespaceRecord]:
        """Dictionary for O(1) lookup by alpha_2 code."""
        return self._index_alpha_2.copy()

    @property
    def by_alpha_3_dict(self) -> Dict[str, ISONamespaceRecord]:
        """Dictionary for O(1) lookup by alpha_3 code."""
        return self._index_alpha_3.copy()

    @property
    def by_name_dict(self) -> Dict[str, ISONamespaceRecord]:
        """Dictionary for O(1) lookup by name."""
        return self._index_name.copy()

    @property
    def by_numeric_dict(self) -> Dict[str, ISONamespaceRecord]:
        """Dictionary for O(1) lookup by numeric code."""
        return self._index_numeric.copy()


class Countries(ISO):
    def __init__(self, iso_key: str) -> None:
        super().__init__(iso_key)
        # Former names mapping for countries that changed names but kept codes
        # This is hardcoded to avoid dependency on external files that get overwritten
        self._former_names_data = {
            "Swaziland": {
                "alpha_2": "SZ",
                "alpha_3": "SWZ",
                "current_name": "Eswatini",
                "change_date": "2018-04-19",
                "comment": "Name change, codes remained the same",
            }
        }

        # Mapping from former codes to current codes for countries that changed both
        self._code_mappings = {
            ("BU", "BUR"): ("MM", "MMR"),  # Burma -> Myanmar
            ("ZR", "ZAR"): ("CD", "COD"),  # Zaire -> Congo (DRC)
        }

    @property
    def by_alpha_2(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="alpha_2")

    @property
    def by_alpha_3(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_common_name(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="common_name")

    @property
    def by_name(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="name")

    @property
    def by_numeric(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="numeric")

    @property
    def name(self) -> Generator[Tuple[str, str], None, None]:
        return self._name_from_index(index="alpha_2")

    @property
    def items(self) -> List[ISONamespaceRecord]:
        return super().items

    def _get_current_country_from_former_codes(
        self, alpha_2: str, alpha_3: str
    ) -> Optional[ISONamespaceRecord]:
        """
        Look up current country by former ISO codes using the mapping table.
        """
        current_codes = self._code_mappings.get((alpha_2, alpha_3))
        if current_codes:
            return self.find(alpha_2=current_codes[0])
        return None

    def get_by_former_name(self, former_name: str) -> Optional[ISONamespaceRecord]:
        """
        Look up a country by its former name.

        This method searches in two places:
        1. Hardcoded former names (for name changes that kept the same codes)
        2. ISO 3166-3 former countries (for countries that changed codes)

        Args:
            former_name: The former name of the country (e.g., "Swaziland", "Burma")

        Returns:
            ISONamespaceRecord if found, None if not found or if the former country
            no longer exists as a single entity
        """
        if not isinstance(former_name, str) or not former_name:
            return None

        # First, check hardcoded former names (name changes with same codes)
        former_mapping = self._former_names_data.get(former_name)
        if former_mapping:
            # Look up the current country by alpha_2 code
            return self.find(alpha_2=former_mapping["alpha_2"])

        # Second, check ISO 3166-3 former countries data
        # Look for the former name in the former_countries data
        former_countries_instance = FormerCountries("3166-3")

        for former_country in former_countries_instance.items:
            country_name = former_country.get("name", "")
            # Check if former_name matches the country name (with some flexibility)
            if (
                former_name.lower() in country_name.lower()
                or country_name.lower().startswith(former_name.lower())
            ):
                # Try to find current country with updated codes
                result = self._get_current_country_from_former_codes(
                    former_country.get("alpha_2", ""), former_country.get("alpha_3", "")
                )
                if result:
                    return result

        return None

    def get_former_names_info(self, former_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a former country name.

        Args:
            former_name: The former name of the country

        Returns:
            Dict with former name mapping info, or None if not found
        """
        if not isinstance(former_name, str) or not former_name:
            return None

        # Check hardcoded former names first
        custom_info = self._former_names_data.get(former_name)
        if custom_info:
            return custom_info

        # Check ISO 3166-3 former countries
        former_countries_instance = FormerCountries("3166-3")

        for former_country in former_countries_instance.items:
            country_name = former_country.get("name", "")
            if (
                former_name.lower() in country_name.lower()
                or country_name.lower().startswith(former_name.lower())
            ):
                # Convert ISO 3166-3 format to our format
                current_codes = self._code_mappings.get(
                    (
                        former_country.get("alpha_2", ""),
                        former_country.get("alpha_3", ""),
                    )
                )
                current_country = None
                if current_codes:
                    current_country = self.find(alpha_2=current_codes[0])

                return {
                    "alpha_2": former_country.get("alpha_2"),
                    "alpha_3": former_country.get("alpha_3"),
                    "alpha_4": former_country.get("alpha_4"),
                    "current_name": current_country.name if current_country else None,
                    "change_date": former_country.get("withdrawal_date"),
                    "comment": f"Former country from ISO 3166-3: {country_name}",
                }

        return None

    @property
    def former_names(self) -> List[str]:
        """
        Get a list of all available former country names.

        Returns:
            List of former country names that can be looked up
        """
        names = list(self._former_names_data.keys())

        # Add simplified names from ISO 3166-3
        former_countries_instance = FormerCountries("3166-3")

        for former_country in former_countries_instance.items:
            country_name = former_country.get("name", "")
            # Extract main country name (before comma or other punctuation)
            main_name = country_name.split(",")[0].strip()
            # Clean up common patterns
            main_name = main_name.replace(
                "Socialist Republic of the Union of", ""
            ).strip()
            main_name = main_name.replace("Republic of", "").strip()

            if main_name and main_name not in names and len(main_name) > 3:
                names.append(main_name)

        return sorted(names)


class Languages(ISO):
    @property
    def by_alpha_3(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_name(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="name")

    @property
    def name(self) -> Generator[Tuple[str, str], None, None]:
        return self._name_from_index(index="alpha_3")

    @property
    def items(self) -> List[ISONamespaceRecord]:
        return super().items


class Currencies(ISO):
    @property
    def by_alpha_3(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_name(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="name")

    @property
    def by_numeric(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="numeric")

    @property
    def name(self) -> Generator[Tuple[str, str], None, None]:
        return self._name_from_index(index="alpha_3")

    @property
    def items(self) -> List[ISONamespaceRecord]:
        return super().items


class SubdivisionsCountries(ISO):
    @property
    def by_code(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="code")

    @property
    def by_name(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="name")

    @property
    def by_type(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="type")

    @property
    def name(self) -> Generator[Tuple[str, str], None, None]:
        return self._name_from_index(index="code")

    @property
    def items(self) -> List[ISONamespaceRecord]:
        return super().items


class FormerCountries(ISO):
    @property
    def by_alpha_2(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="alpha_2")

    @property
    def by_alpha_3(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_alpha_4(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="alpha_4")

    @property
    def by_name(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="name")

    @property
    def by_numeric(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="numeric")

    @property
    def by_withdrawal_date(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="withdrawal_date")

    @property
    def name(self) -> Generator[Tuple[str, str], None, None]:
        return self._name_from_index(index="alpha_2")

    @property
    def items(self) -> List[ISONamespaceRecord]:
        return super().items


class ExtendedLanguages(ISO):
    @property
    def by_alpha_3(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_name(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="name")

    @property
    def by_scope(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="scope")

    @property
    def by_type(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="type")

    @property
    def name(self) -> Generator[Tuple[str, str], None, None]:
        return self._name_from_index(index="alpha_3")

    @property
    def items(self) -> List[ISONamespaceRecord]:
        return super().items


class LanguageFamilies(ISO):
    @property
    def by_alpha_3(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_name(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="name")

    @property
    def name(self) -> Generator[Tuple[str, str], None, None]:
        return self._name_from_index(index="alpha_3")

    @property
    def items(self) -> List[ISONamespaceRecord]:
        return super().items


class ScriptNames(ISO):
    @property
    def by_alpha_4(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="alpha_4")

    @property
    def by_name(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="name")

    @property
    def by_numeric(self) -> List[Tuple[str, ISONamespaceRecord]]:
        return self._sorted_by_index(index="numeric")

    @property
    def name(self) -> Generator[Tuple[str, str], None, None]:
        return self._name_from_index(index="alpha_4")

    @property
    def items(self) -> List[ISONamespaceRecord]:
        return super().items


countries = Countries("3166-1")
languages = Languages("639-2")
currencies = Currencies("4217")
subdivisions_countries = SubdivisionsCountries("3166-2")
former_countries = FormerCountries("3166-3")
extendend_languages = ExtendedLanguages("639-3")
language_families = LanguageFamilies("639-5")
script_names = ScriptNames("15924")
