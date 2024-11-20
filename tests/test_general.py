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
)


@pytest.fixture
def countries():
    return Countries("3166-1")


@pytest.fixture
def languages():
    return Languages("639-2")


@pytest.fixture
def currencies():
    return Currencies("4217")


@pytest.fixture
def subdivisions_countries():
    return SubdivisionsCountries("3166-2")


@pytest.fixture
def former_countries():
    return FormerCountries("3166-3")


@pytest.fixture
def extended_languages():
    return ExtendedLanguages("639-3")


@pytest.fixture
def language_families():
    return LanguageFamilies("639-5")


@pytest.fixture
def script_names():
    return ScriptNames("15924")


def test_countries_by_alpha_2(countries):
    result = countries.by_alpha_2
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) for item in result)


def test_languages_by_alpha_3(languages):
    result = languages.by_alpha_3
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) for item in result)


def test_currencies_by_alpha_3(currencies):
    result = currencies.by_alpha_3
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) for item in result)


def test_subdivisions_countries_by_code(subdivisions_countries):
    result = subdivisions_countries.by_code
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) for item in result)


def test_former_countries_by_alpha_2(former_countries):
    result = former_countries.by_alpha_2
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) for item in result)


def test_extended_languages_by_alpha_3(extended_languages):
    result = extended_languages.by_alpha_3
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) for item in result)


def test_language_families_by_alpha_3(language_families):
    result = language_families.by_alpha_3
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) for item in result)


def test_script_names_by_alpha_4(script_names):
    result = script_names.by_alpha_4
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) for item in result)
