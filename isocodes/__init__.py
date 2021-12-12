import json
from pathlib import Path
from typing import Generator


BASE_DIR = Path(__file__).resolve().parent.parent

LOCALES_DIR = f"{BASE_DIR}/isocodes/share/locale"


class ISO:
    def __init__(self, iso_key: str) -> None:
        self.iso_key: str = iso_key
        with open(
            f"{BASE_DIR}/isocodes/share/iso-codes/json/iso_{self.iso_key}.json"
        ) as iso_file:
            self.data: list[dict] = json.load(iso_file)[self.iso_key]

    def _name_from_index(self, index: str) -> Generator[tuple, None, None]:
        return ((element[index], element["name"]) for element in self.data)

    def _sorted_by_index(self, index: str) -> list[tuple]:
        return sorted(((element[index], element) for element in self.data))

    def get(self, **kwargs) -> dict[str, str]:
        key: str = next(iter(kwargs))
        return [element for element in self.data if element[key] == kwargs[key]][0]

    @property
    def items(self) -> list[dict]:
        return self.data


class Countries(ISO):
    @property
    def by_alpha_2(self) -> list[tuple]:
        return self._sorted_by_index(index="alpha_2")

    @property
    def by_alpha_3(self) -> list[tuple]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_name(self) -> list[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def by_numeric(self) -> list[tuple]:
        return self._sorted_by_index(index="numeric")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="alpha_2")


class Languages(ISO):
    @property
    def by_alpha_3(self) -> list[tuple]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_name(self) -> list[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="alpha_3")


class Currencies(ISO):
    @property
    def by_alpha_3(self) -> list[tuple]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_name(self) -> list[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def by_numeric(self) -> list[tuple]:
        return self._sorted_by_index(index="numeric")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="alpha_3")


class SubdivisionsCountries(ISO):
    @property
    def by_code(self) -> list[tuple]:
        return self._sorted_by_index(index="code")

    @property
    def by_name(self) -> list[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def by_type(self) -> list[tuple]:
        return self._sorted_by_index(index="type")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="code")


class FormerCountries(ISO):
    @property
    def by_alpha_2(self) -> list[tuple]:
        return self._sorted_by_index(index="alpha_2")

    @property
    def by_alpha_3(self) -> list[tuple]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_alpha_4(self) -> list[tuple]:
        return self._sorted_by_index(index="alpha_4")

    @property
    def by_name(self) -> list[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def by_numeric(self) -> list[tuple]:
        return self._sorted_by_index(index="numeric")

    @property
    def by_withdrawal_date(self) -> list[tuple]:
        return self._sorted_by_index(index="withdrawal_date")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="alpha_2")


class ExtendedLanguages(ISO):
    @property
    def by_alpha_3(self) -> list[tuple]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_name(self) -> list[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def by_scope(self) -> list[tuple]:
        return self._sorted_by_index(index="scope")

    @property
    def by_type(self) -> list[tuple]:
        return self._sorted_by_index(index="type")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="alpha_3")


class LanguageFamilies(ISO):
    @property
    def by_alpha_3(self) -> list[tuple]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_name(self) -> list[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="alpha_3")


class ScriptNames(ISO):
    @property
    def by_alpha_4(self) -> list[tuple]:
        return self._sorted_by_index(index="alpha_4")

    @property
    def by_name(self) -> list[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def by_numeric(self) -> list[tuple]:
        return self._sorted_by_index(index="numeric")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="alpha_4")


countries = Countries("3166-1")
languages = Languages("639-2")
currencies = Currencies("4217")
subdivisions_countries = SubdivisionsCountries("3166-2")
former_countries = FormerCountries("3166-3")
extendend_languages = ExtendedLanguages("639-3")
language_families = LanguageFamilies("639-5")
script_names = ScriptNames("15924")
