import difflib
import functools
import gettext
import importlib.resources
import json
import pathlib
import re
import threading
import warnings
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    TypedDict,
)

from importlib.resources.abc import Traversable

# Where the bundled gettext catalogues live.
_BUNDLED_LOCALE_PATH = pathlib.Path(__file__).parent / "share" / "locale"

_warned_no_catalogues = False


@functools.lru_cache(maxsize=None)
def _locale_dirs() -> Tuple[pathlib.Path, ...]:
    """Return the directories holding gettext catalogues.

    Catalogues ship with the package, but `isocodes locales` can remove them, so
    this may legitimately come back empty.
    """
    if _BUNDLED_LOCALE_PATH.is_dir():
        return (_BUNDLED_LOCALE_PATH,)
    return ()


def _warn_if_no_catalogues() -> None:
    """Warn once when a translation is asked for but nothing is installed.

    Without this the fallback is silent, and an upgrade from a version that
    bundled every language would quietly start returning English.
    """
    global _warned_no_catalogues
    if _locale_dirs() or _warned_no_catalogues:
        return
    _warned_no_catalogues = True
    warnings.warn(
        "No isocodes translation catalogues were found, so names are returned "
        "untranslated. They ship with the package, so this usually means they "
        "were removed; run 'pip install --force-reinstall isocodes' to restore "
        "them.",
        RuntimeWarning,
        stacklevel=3,
    )


# Upstream ships each catalogue under a current and an obsolete name. Only the
# current files are packaged, so the old names are mapped onto them here for
# anyone who still asks for one.
_DOMAIN_ALIASES = {
    "iso_3166": "iso_3166-1",
    "iso_3166_2": "iso_3166-2",
    "iso_639": "iso_639-2",
    "iso_639_3": "iso_639-3",
    "iso_639_5": "iso_639-5",
}


@functools.lru_cache(maxsize=None)
def _translator(domain: str, language: str) -> Callable[[str], str]:
    """Return a gettext callable for one standard and language.

    Falls back to returning text unchanged when no catalogue is installed for
    that language, so callers never have to special-case missing translations.
    """
    domain = _DOMAIN_ALIASES.get(domain, domain)
    for directory in _locale_dirs():
        try:
            translation = gettext.translation(
                domain, localedir=str(directory), languages=[language]
            )
        except OSError:
            continue
        return translation.gettext
    _warn_if_no_catalogues()
    return lambda text: text


def available_languages() -> List[str]:
    """List the language codes for which catalogues are installed."""
    languages = {
        path.name
        for directory in _locale_dirs()
        for path in directory.iterdir()
        if (path / "LC_MESSAGES").is_dir()
    }
    return sorted(languages)


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
    A dict-based record that also supports attribute access.

    Fields are stored once, in the dict itself; attribute access reads straight
    through, so there is no second copy that can drift out of sync.

    Example:
        record = ISONamespaceRecord({"alpha_2": "US", "name": "United States"})

        # Dictionary access (backward compatible)
        print(record["name"])  # United States
        print(record.get("alpha_2"))  # US
        print(isinstance(record, dict))  # True

        # Dot notation access
        print(record.name)  # United States
        print(record.alpha_2)  # US
    """

    __slots__ = ()

    def __getattr__(self, name: str) -> Any:
        """Support dot notation access."""
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            ) from None

    def __setattr__(self, name: str, value: Any) -> None:
        """Attribute assignment writes through to the dict."""
        self[name] = value

    def __delattr__(self, name: str) -> None:
        """Attribute deletion removes the dict entry."""
        try:
            del self[name]
        except KeyError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            ) from None

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"{self.__class__.__name__}({dict(self)})"


# Remove the MutableMapping registration since we now inherit from dict


def get_resource(resource: str) -> Traversable:
    """Return a file handle on a named resource in a Package."""
    return importlib.resources.files("isocodes").joinpath(resource)


class ISO:
    iso_key: str
    data: List[Dict[str, str]]

    # Fields whose values all share a fixed width, so a substring match can
    # only ever be an exact match. Only these are safe to serve from an index
    # in get(), which is otherwise a substring scan.
    _FIXED_WIDTH_FIELDS = frozenset({"alpha_2", "alpha_3", "alpha_4", "numeric"})

    def __init__(self, iso_key: str) -> None:
        self.iso_key = iso_key
        resource_file = get_resource(f"share/iso-codes/json/iso_{self.iso_key}.json")
        with resource_file.open(encoding="utf-8") as iso_file:
            self.data = json.load(iso_file)[self.iso_key]

        # Create enhanced records with dot notation support
        self._namespace_records = [ISONamespaceRecord(item) for item in self.data]

        # Create efficient indexes for fast lookups
        self._create_indexes()

    def _create_indexes(self) -> None:
        """Create indexed access for common fields."""
        self._index_alpha_2: Dict[str, "ISONamespaceRecord"] = {}
        self._index_alpha_3: Dict[str, "ISONamespaceRecord"] = {}
        self._index_name: Dict[str, "ISONamespaceRecord"] = {}
        self._index_numeric: Dict[str, "ISONamespaceRecord"] = {}
        self._indexes: Dict[str, Dict[str, "ISONamespaceRecord"]] = {
            "alpha_2": self._index_alpha_2,
            "alpha_3": self._index_alpha_3,
            "name": self._index_name,
            "numeric": self._index_numeric,
        }

        for record in self._namespace_records:
            for field, index in self._indexes.items():
                value = record.get(field)
                if value is not None:
                    index[value] = record

    def __len__(self) -> int:
        return len(self.data)

    def _name_from_index(self, index: str) -> Generator[Tuple[str, str], None, None]:
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
        Return the first record whose field *contains* the given value.

        Matching is a substring test, kept for backward compatibility.
        Use find() for exact lookups.

        Returns an empty ISONamespaceRecord when nothing matches, so callers
        that treat the result as a dict keep working.
        """
        if not kwargs:
            return ISONamespaceRecord({})

        key: str = next(iter(kwargs))
        value = kwargs[key]

        if not isinstance(value, str) or not value:
            return ISONamespaceRecord({})

        # On fixed-width fields a substring match is necessarily an exact match,
        # so the index returns the same record the scan below would find.
        if key in self._FIXED_WIDTH_FIELDS:
            index = self._indexes.get(key)
            if index is not None:
                record = index.get(value)
                if record is not None:
                    return record

        for record in self._namespace_records:
            field = record.get(key)
            if field is not None and value in field:
                return record

        return ISONamespaceRecord({})

    def find(self, **kwargs: str) -> Optional[ISONamespaceRecord]:
        """
        Exact-match lookup. Every keyword must match for a record to be returned.

        Example:
            country = countries.find(alpha_2="US")
            print(country.name)  # United States
        """
        if not kwargs:
            return None

        # Single indexed field: O(1).
        if len(kwargs) == 1:
            key, value = next(iter(kwargs.items()))
            index = self._indexes.get(key)
            if index is not None:
                return index.get(value)

        for record in self._namespace_records:
            if all(record.get(key) == value for key, value in kwargs.items()):
                return record

        return None

    @staticmethod
    def _match_rank(query: str, value: str) -> Optional[int]:
        """Score how well `value` matches `query`; None when it does not.

        Lower is better. Word order is ignored, because ISO stores many names
        in inverted form ("Korea, Republic of"), which a plain substring test
        can never match against how people actually type them.
        """
        query, value = query.lower().strip(), value.lower()
        if not query:
            return None
        if value == query:
            return 0
        if value.startswith(query):
            return 1
        if query in value:
            return 2
        words = [word for word in re.split(r"\W+", query) if word]
        if words and all(word in value for word in words):
            return 3
        return None

    def search(self, **kwargs: str) -> List[ISONamespaceRecord]:
        """
        Search for records matching every criterion, ignoring word order.

        Results are ranked: exact matches first, then prefixes, then substrings,
        then records containing all the words in any order. Ties are broken by
        the shorter, and so more specific, value.

        Example:
            island_countries = countries.search(name="Island")
            for country in island_countries:
                print(f"{country.name} - {country.flag}")

            # Word order does not matter
            countries.search(name="Republic of Korea")
            # [ISONamespaceRecord({... 'name': 'Korea, Republic of' ...})]
        """
        if not kwargs:
            return []

        scored = []
        for record in self._namespace_records:
            ranks = []
            for key, query in kwargs.items():
                value = record.get(key)
                if value is None:
                    break
                rank = self._match_rank(query, str(value))
                if rank is None:
                    break
                ranks.append((rank, len(str(value))))
            else:
                scored.append((max(ranks), record))

        scored.sort(key=lambda item: (item[0], str(item[1].get("name", ""))))
        return [record for _, record in scored]

    def search_fuzzy(
        self, query: str, cutoff: float = 0.7, limit: int = 10
    ) -> List[ISONamespaceRecord]:
        """
        Search names while tolerating misspellings.

        A correctly spelled query never gets an approximate answer: whatever
        search() finds is returned unchanged, and the similarity pass only runs
        when that comes back empty. Results are ordered by closeness.

        Example:
            countries.search_fuzzy("Repblic")   # finds the Republics
            countries.search_fuzzy("Germny")    # [Germany]
        """
        matches = self.search(name=query)
        if matches:
            return matches[:limit]

        normalised = query.lower().strip()
        words = [word for word in re.split(r"\W+", normalised) if word]
        if not words:
            return []

        scored: List[Tuple[float, ISONamespaceRecord]] = []
        for record in self._namespace_records:
            name = str(record.get("name", "")).lower()
            if not name:
                continue
            candidates = [word for word in re.split(r"\W+", name) if word]
            if not candidates:
                continue
            # Compare the query as a whole, and word by word, so a typo in one
            # word of a long inverted name still scores well.
            per_word = [
                max(
                    difflib.SequenceMatcher(None, word, candidate).ratio()
                    for candidate in candidates
                )
                for word in words
            ]
            score = max(
                difflib.SequenceMatcher(None, normalised, name).ratio(),
                sum(per_word) / len(per_word),
            )
            if score >= cutoff:
                scored.append((score, record))

        # Ties go to the shorter, and so more specific, name: "Latin" should
        # beat a long name that merely contains the word.
        scored.sort(
            key=lambda item: (
                -item[0],
                len(str(item[1].get("name", ""))),
                str(item[1].get("name", "")),
            )
        )
        return [record for _, record in scored[:limit]]

    @property
    def domain(self) -> str:
        """The gettext domain holding this standard's translations."""
        return f"iso_{self.iso_key}"

    def translator(self, language: str) -> Callable[[str], str]:
        """
        Return a callable that translates this standard's names into `language`.

        Example:
            to_french = countries.translator("fr")
            to_french("Germany")  # 'Allemagne'
        """
        return _translator(self.domain, language)

    def translate(self, value: Any, language: str) -> str:
        """
        Translate a record or a name into `language`.

        Accepts either a record or a plain name, and returns the name unchanged
        when no translation exists.

        Example:
            countries.translate(countries.find(alpha_2="DE"), "fr")  # 'Allemagne'
            countries.translate("Germany", "fr")                     # 'Allemagne'
        """
        text = value.get("name", "") if isinstance(value, dict) else value
        if not isinstance(text, str) or not text:
            return ""
        return self.translator(language)(text)

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
        former_countries_instance = _dataset("former_countries")

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
        former_countries_instance = _dataset("former_countries")

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
        former_countries_instance = _dataset("former_countries")

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


_DATASETS: Dict[str, Tuple[str, str]] = {
    "countries": ("Countries", "3166-1"),
    "languages": ("Languages", "639-2"),
    "currencies": ("Currencies", "4217"),
    "subdivisions_countries": ("SubdivisionsCountries", "3166-2"),
    "former_countries": ("FormerCountries", "3166-3"),
    "extended_languages": ("ExtendedLanguages", "639-3"),
    "language_families": ("LanguageFamilies", "639-5"),
    "script_names": ("ScriptNames", "15924"),
}

_instances: Dict[str, ISO] = {}
_instances_lock = threading.Lock()


def _dataset(name: str) -> ISO:
    """Build a dataset on first use and cache it for subsequent lookups."""
    try:
        return _instances[name]
    except KeyError:
        pass
    with _instances_lock:
        if name not in _instances:
            class_name, iso_key = _DATASETS[name]
            _instances[name] = globals()[class_name](iso_key)
        return _instances[name]


def __getattr__(name: str) -> Any:
    """Resolve datasets and LOCALE_PATH on first access (PEP 562).

    Datasets are parsed lazily, and LOCALE_PATH points at wherever the
    catalogues actually are, which depends on which locale packages are
    installed.
    """
    if name in _DATASETS:
        return _dataset(name)
    if name == "LOCALE_PATH":
        directories = _locale_dirs()
        return directories[0] if directories else _BUNDLED_LOCALE_PATH
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> List[str]:
    return sorted(set(globals()) | set(_DATASETS) | {"LOCALE_PATH"})


if TYPE_CHECKING:
    # Declared for type checkers, which cannot see through module __getattr__.
    LOCALE_PATH: pathlib.Path
    countries: Countries
    languages: Languages
    currencies: Currencies
    subdivisions_countries: SubdivisionsCountries
    former_countries: FormerCountries
    extended_languages: ExtendedLanguages
    language_families: LanguageFamilies
    script_names: ScriptNames
