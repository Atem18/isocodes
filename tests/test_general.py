from isocodes import countries, languages, currencies


def test_countries():
    assert len(countries) == 249


def test_languages():
    assert len(languages) == 487


def test_currencies():
    assert len(currencies) == 181
