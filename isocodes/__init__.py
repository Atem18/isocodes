import inspect
import json
import os
import sys
from typing import Dict, Generator, List


def get_script_dir(follow_symlinks=True):
    if getattr(sys, "frozen", False):  # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


BASE_DIR = get_script_dir()

LOCALES_DIR = f"{BASE_DIR}/share/locale"


class ISO:
    def __init__(self, iso_key: str) -> None:
        self.iso_key: str = iso_key
        with open(
            f"{BASE_DIR}/share/iso-codes/json/iso_{self.iso_key}.json", encoding="utf-8"
        ) as iso_file:
            self.data: List[Dict] = json.load(iso_file)[self.iso_key]

    def __len__(self) -> int:
        return len(self.data)

    def _name_from_index(self, index: str) -> Generator[tuple, None, None]:
        return ((element[index], element["name"]) for element in self.data)

    def _sorted_by_index(self, index: str) -> List[tuple]:
        return sorted(((element[index], element) for element in self.data))

    def get(self, **kwargs) -> Dict[str, str]:
        key: str = next(iter(kwargs))
        try:
            return [
                element
                for element in self.data
                if key in element and element[key] == kwargs[key]
            ][0]
        except IndexError:
            return {}

    @property
    def items(self) -> List[Dict]:
        return self.data


class Countries(ISO):
    @property
    def by_alpha_2(self) -> List[tuple]:
        return self._sorted_by_index(index="alpha_2")

    @property
    def by_alpha_3(self) -> List[tuple]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_common_name(self) -> List[tuple]:
        return self._sorted_by_index(index="common_name")

    @property
    def by_name(self) -> List[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def by_numeric(self) -> List[tuple]:
        return self._sorted_by_index(index="numeric")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="alpha_2")


class Languages(ISO):
    @property
    def by_alpha_3(self) -> List[tuple]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_name(self) -> List[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="alpha_3")


class Currencies(ISO):
    @property
    def by_alpha_3(self) -> List[tuple]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_name(self) -> List[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def by_numeric(self) -> List[tuple]:
        return self._sorted_by_index(index="numeric")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="alpha_3")


class SubdivisionsCountries(ISO):
    @property
    def by_code(self) -> List[tuple]:
        return self._sorted_by_index(index="code")

    @property
    def by_name(self) -> List[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def by_type(self) -> List[tuple]:
        return self._sorted_by_index(index="type")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="code")


class FormerCountries(ISO):
    @property
    def by_alpha_2(self) -> List[tuple]:
        return self._sorted_by_index(index="alpha_2")

    @property
    def by_alpha_3(self) -> List[tuple]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_alpha_4(self) -> List[tuple]:
        return self._sorted_by_index(index="alpha_4")

    @property
    def by_name(self) -> List[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def by_numeric(self) -> List[tuple]:
        return self._sorted_by_index(index="numeric")

    @property
    def by_withdrawal_date(self) -> List[tuple]:
        return self._sorted_by_index(index="withdrawal_date")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="alpha_2")


class ExtendedLanguages(ISO):
    @property
    def by_alpha_3(self) -> List[tuple]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_name(self) -> List[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def by_scope(self) -> List[tuple]:
        return self._sorted_by_index(index="scope")

    @property
    def by_type(self) -> List[tuple]:
        return self._sorted_by_index(index="type")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="alpha_3")


class LanguageFamilies(ISO):
    @property
    def by_alpha_3(self) -> List[tuple]:
        return self._sorted_by_index(index="alpha_3")

    @property
    def by_name(self) -> List[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def name(self) -> Generator[tuple, None, None]:
        return self._name_from_index(index="alpha_3")


class ScriptNames(ISO):
    @property
    def by_alpha_4(self) -> List[tuple]:
        return self._sorted_by_index(index="alpha_4")

    @property
    def by_name(self) -> List[tuple]:
        return self._sorted_by_index(index="name")

    @property
    def by_numeric(self) -> List[tuple]:
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
