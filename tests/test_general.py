from isocodes import languages


def test_languages():
    assert languages.get(name="Spanish")
