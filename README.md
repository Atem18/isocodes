# isocodes

isocodes gives you the ISO standards — countries, subdivisions, languages,
currencies and scripts — as plain Python data, with no runtime dependencies.

- **Loads on demand.** Importing the package is cheap; each standard is parsed
  the first time you actually touch it.
- **Dict *and* attribute access.** Every record is a real `dict` and also
  supports `record.name`.
- **Translated names in 163 languages**, all included, with a command to
  drop the ones you do not need.
- **A command line interface**, with table, JSON and CSV output, and optional
  tolerance for misspellings.
- **Works inside frozen applications** — a PyInstaller hook is included.
- **Covers ISO 639-2**, alongside 639-3 and 639-5.

The data comes from https://salsa.debian.org/iso-codes-team/iso-codes, many
thanks to them.

# Installation

    pip install isocodes

Everything is included: all eight standards and translations in 163 languages.

If package size matters — a container image, a Lambda bundle — you can drop the
languages you do not use:

    isocodes locales                    # list what is installed
    isocodes locales --keep fr,en       # preview the removal
    isocodes locales --keep fr,en --yes # apply it

| | Size on disk |
| --- | --- |
| as installed | ~19 MB |
| after `--keep fr,en` | ~750 KB |

In a Dockerfile, prune in the same layer as the install, or the files stay in
the image:

    RUN pip install isocodes && isocodes locales --keep fr,en --yes

The removal is not permanent: `pip install --upgrade isocodes` restores every
language, as does `pip install --force-reinstall isocodes`.

# Usage

## Countries (ISO 3166)

### Dot Notation Access

```python
>>> from isocodes import countries
>>> usa = countries.get(alpha_2="US")

# Dot notation:
>>> usa.name
'United States'
>>> usa.flag
'🇺🇸'
>>> usa.alpha_3
'USA'
>>> usa.official_name
'United States of America'

# Dictionary access:
>>> usa["name"]
'United States'
>>> usa.get("alpha_3")
'USA'
>>> isinstance(usa, dict)
True
```

### Enhanced Search Methods

#### Fast Exact Lookup with `find()`

```python
>>> # O(1) performance for common lookups
>>> germany = countries.find(alpha_2="DE")
>>> germany.name
'Germany'
>>> germany.flag
'🇩🇪'
```

#### Flexible Search with `search()`

```python
>>> # Find all countries with "Island" in the name
>>> island_countries = countries.search(name="Island")
>>> for country in island_countries[:3]:
...     print(f"{country.name} - {country.flag}")
Cook Islands - 🇨🇰
Bouvet Island - 🇧🇻
Faroe Islands - 🇫🇴
```

Word order does not matter, which matters because ISO stores many names in
inverted form. Results are ranked, so the closest match comes first:

```python
>>> [c.name for c in countries.search(name="Republic of Korea")]
['Korea, Republic of', "Korea, Democratic People's Republic of"]
```

#### Misspellings with `search_fuzzy()`

`search()` never guesses. When you want tolerance for typos, ask for it:

```python
>>> [c.name for c in countries.search_fuzzy("Germny")]
['Germany', 'Guernsey']
>>> [c.name for c in countries.search_fuzzy("Untied Kingdom")]
['United Kingdom']
>>> countries.search_fuzzy("xyzzy not a place")
[]
```

A correctly spelled query is answered by `search()` and never reaches the
approximate matching, so reaching for this by default is safe:

```python
>>> [c.name for c in countries.search_fuzzy("Kingdom")]
['United Kingdom']
```

`cutoff` controls how close a match has to be, and `limit` caps the results.
On the command line the same behaviour sits behind `--fuzzy`:

    isocodes countries --name Germny --fuzzy

#### Fast Dictionary Access

```python
>>> by_code = countries.by_alpha_2_dict
>>> canada = by_code["CA"]
>>> canada.name
'Canada'
>>> canada.flag
'🇨🇦'
```

#### Get method

You can access one country by using the method get with the parameters being the json keys of the .json files in the share/iso-codes/json folder

##### Example

```python
>>> from isocodes import countries
>>> countries.get(name="Germany")
{'alpha_2': 'DE', 'alpha_3': 'DEU', 'flag': '🇩🇪', 'name': 'Germany', 'numeric': '276', 'official_name': 'Federal Republic of Germany'}
```

### Items property

You can get a list from the .json files in the share/iso-codes/json folder with the items property. Each item supports both dictionary and dot notation access:

##### Example

```python
>>> from isocodes import countries
>>> for country in countries.items:
...     print(f"{country.name} - {country.flag}")
...     print(country["alpha_2"])
...
Aruba - 🇦🇼
AW
Afghanistan - 🇦�
AF
Angola - 🇦�
AO
...
```

### by_xxx property

You can get a list with sorted data by one of the property with the by_xxx property, xxx being one of the data key (alpha_2, name, numeric, etc.).

##### Example

```python
>>> countries.by_numeric[0]
('004', <Country: Afghanistan>)
>>> country = countries.by_numeric[0][1]
>>> country.name
'Afghanistan'
>>> country.flag
'🇦🇫'
```

### Former country names lookup

You can look up countries by their former names using the `get_by_former_name` method.

##### Example

```python
>>> from isocodes import countries

>>> eswatini = countries.get_by_former_name("Swaziland")
>>> eswatini.name
'Eswatini'
>>> eswatini.flag
'🇸🇿'
>>> f"{eswatini.name} ({eswatini.alpha_2})"
'Eswatini (SZ)'

>>> myanmar = countries.get_by_former_name("Burma")
>>> f"{myanmar.name} - {myanmar.flag}"
'Myanmar - 🇲🇲'

>>> countries.get_former_names_info("Czechoslovakia")
{'alpha_2': None, 'alpha_3': None, 'current_name': None, 'change_date': '1993-01-01', 'comment': 'Split into Czech Republic (CZ/CZE) and Slovakia (SK/SVK)'}

>>> countries.former_names[:5]
['Swaziland', 'Burma', 'Zaire', 'Czechoslovakia', 'Yugoslavia']
```


## Other ISO Standards

### Languages (ISO 639-2)

```python
>>> from isocodes import languages
>>> english = languages.get(alpha_3="eng")
>>> english.name
'English'
>>> romance_langs = languages.search(name="French")
```

### Currencies (ISO 4217)

```python
>>> from isocodes import currencies
>>> usd = currencies.find(alpha_3="USD")
>>> usd.name
'US Dollar'
>>> usd.numeric
'840'
```

### Countries and Subdivisions (ISO 3166-2)

```python
>>> from isocodes import subdivisions_countries
>>> california = subdivisions_countries.find(code="US-CA")
>>> california.name
'California'
```

### Former countries (ISO 3166-3)

```python
>>> from isocodes import former_countries
>>> yugoslavia = former_countries.get(alpha_3="YUG")
>>> yugoslavia.name
'Yugoslavia'
```

### Extended languages (ISO 639-3)

```python
>>> from isocodes import extended_languages
>>> mandarin = extended_languages.find(alpha_3="cmn")
>>> mandarin.name
'Mandarin Chinese'
```

### Language families (ISO 639-5)

```python
>>> from isocodes import language_families
>>> indo_european = language_families.find(alpha_3="ine")
>>> indo_european.name
'Indo-European languages'
```

### Script names (ISO 15924)

```python
>>> from isocodes import script_names
>>> latin = script_names.find(alpha_4="Latn")
>>> latin.name
'Latin'
```

# Command Line Interface

isocodes includes a powerful command-line interface for quick ISO data lookups and searches.

## Installation

After installing isocodes, the CLI is available as the `isocodes` command:

```bash
pip install isocodes
isocodes --help
```

## Basic Usage

### Countries

```bash
# Find country by code
isocodes countries --code US
isocodes countries --code DEU

# Search by name
isocodes countries --name Germany --exact
isocodes countries --name Island

# Find by former name
isocodes countries --former-name Burma

# List all countries
isocodes countries --list-all
```

### Languages

```bash
# Find language by code
isocodes languages --code en
isocodes languages --code deu

# Search by name
isocodes languages --name French
```

### Currencies

```bash
# Find currency by code
isocodes currencies --code USD

# Search by name
isocodes currencies --name Euro

# Find by numeric code
isocodes currencies --numeric 840
```

### Country Subdivisions

```bash
# Find subdivision by code
isocodes subdivisions --code US-CA

# List subdivisions for a country
isocodes subdivisions --country US
```

### Former Countries

```bash
# Find former country
isocodes former-countries --code YUG
isocodes former-countries --name Yugoslavia
```

### Script Names

```bash
# Find script by code
isocodes scripts --code Latn

# Find by numeric code
isocodes scripts --numeric 215
```

## Output Formats

### Table Format (Default)

```bash
isocodes countries --code US
# Output:
# alpha_2 | alpha_3 | flag | name          | numeric | official_name
# -----------------------------------------------------------------------------
# US      | USA     | 🇺🇸   | United States | 840     | United States of America
```

### JSON Format

```bash
isocodes --format json countries --code US
# Output:
# [
#   {
#     "alpha_2": "US",
#     "alpha_3": "USA",
#     "flag": "🇺🇸",
#     "name": "United States",
#     "numeric": "840",
#     "official_name": "United States of America"
#   }
# ]
```

### CSV Format

```bash
isocodes --format csv countries --code US
# Output:
# alpha_2,alpha_3,flag,name,numeric,official_name
# US,USA,🇺🇸,United States,840,United States of America
```

## Advanced Options

### Limit Results

```bash
# Show only first 5 results
isocodes --limit 5 countries --name Island
```

### Select Specific Fields

```bash
# Show only name and flag
isocodes --fields name,flag countries --code US
# Output:
# name          | flag
# --------------------
# United States | 🇺🇸
```

### Combining Options

```bash
# JSON output with specific fields and limit
isocodes --format json --fields name,flag --limit 3 countries --name Island
```

## CLI Examples

```bash
# Quick country lookup
isocodes countries --code FR

# Find countries with "United" in name
isocodes countries --name United

# Get all US states in CSV format
isocodes --format csv subdivisions --country US > us_states.csv

# Find all currencies in JSON
isocodes --format json currencies --list-all > currencies.json

# Search for Romance languages
isocodes languages --name French

# Look up former country by modern name reference
isocodes countries --former-name "Soviet Union"
```

## Translations

Names are available in 163 languages, all shipped with the package. `translate()` takes a record or a plain
name and returns the translated name, falling back to the original when no
catalogue exists for that language:

    >>> from isocodes import countries, currencies
    >>> germany = countries.find(alpha_2="DE")
    >>> countries.translate(germany, "fr")
    'Allemagne'
    >>> countries.translate(germany, "ja")
    'ドイツ'
    >>> countries.translate("France", "de")
    'Frankreich'
    >>> currencies.translate(currencies.find(alpha_3="EUR"), "fr")
    'Euro'

Use `translator()` when translating many names into the same language — it
returns a reusable callable:

    >>> to_spanish = countries.translator("es")
    >>> [to_spanish(c.name) for c in countries.search(name="Island")[:2]]
    ['Islas Cook', 'Isla Bouvet']

`available_languages()` lists the languages currently installed, which is all
163 unless you have pruned them:

    >>> from isocodes import available_languages
    >>> len(available_languages())
    163

The underlying gettext catalogues remain available directly. The domain names
are listed at https://salsa.debian.org/iso-codes-team/iso-codes

    >>> import gettext
    >>> import isocodes
    >>> french = gettext.translation('iso_639-2', isocodes.LOCALE_PATH, languages=['fr'])
    >>> french.install()
    >>> _("French")
    'Français'

# Develop

## Tests and coverage

    uv run --group test pytest

The suite is held at 100% by `fail_under` in `pyproject.toml`:

    COVERAGE_PROCESS_START=pyproject.toml \
      uv run --group test --with coverage coverage run -m pytest -q
    uv run --with coverage coverage combine
    uv run --with coverage coverage report

`COVERAGE_PROCESS_START` is what lets the CLI tests that shell out be measured.

## Update iso-codes version

Upstream dropped autotools in 4.19.0 and builds with meson now, so refreshing
the bundled data needs `git`, `meson` and `ninja`:

    ./update.sh              # the version pinned in the script
    ./update.sh v4.20.1      # or an explicit tag

The script clones upstream into a temporary directory, builds it, replaces
`isocodes/share`, then prunes the JSON schemas, the pkg-config file and the
deprecated XML files, which the Python package does not ship.

Upstream installs every catalogue twice, under a current and an obsolete
filename (`iso_3166.mo` alongside `iso_3166-1.mo`). Those are symlinks in the
source tree but a wheel materialises them into full copies, so `update.sh`
deletes them. The obsolete domain names are mapped onto the current ones in
`isocodes/__init__.py` instead, so nothing that used them breaks.

    bash update.sh
