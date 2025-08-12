# isocodes

isocodes provides you access to lists of various ISO standards (e.g. country, language, language scripts, and currency names) with **modern Python dot notation support** and **enhanced performance**.

The data is coming from https://salsa.debian.org/iso-codes-team/iso-codes, many thanks to them.

## ✨ New Features

- **🎯 Dot notation access** - Access data with modern `country.name` syntax
- **⚡ Enhanced performance** - Fast O(1) lookups with indexed search
- **🔍 New search methods** - Find and filter data with ease
- **🔄 100% backward compatible** - All existing code continues to work unchanged

# Installation

    pip install isocodes

# Usage

## Countries (ISO 3166)

### Modern Dot Notation Access (New!)

Access country data using intuitive dot notation while maintaining full dictionary compatibility:

```python
>>> from isocodes import countries
>>> usa = countries.get(alpha_2="US")

# Modern dot notation (new):
>>> usa.name
'United States'
>>> usa.flag
'🇺🇸'
>>> usa.alpha_3
'USA'
>>> usa.official_name
'United States of America'

# Traditional dictionary access (still works):
>>> usa["name"]
'United States'
>>> usa.get("alpha_3")
'USA'
>>> isinstance(usa, dict)
True
```

### Enhanced Search Methods (New!)

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
Åland Islands - 🇦🇽
Bouvet Island - 🇧🇻
Cocos (Keeling) Islands - 🇨🇨
```

#### Fast Dictionary Access (New!)

```python
>>> # Direct dictionary access for power users
>>> by_code = countries.by_alpha_2_dict
>>> canada = by_code["CA"]
>>> canada.name
'Canada'
>>> canada.flag
'🇨🇦'
```

### Traditional Methods (Fully Compatible)

All existing methods continue to work exactly as before:

#### Get method

You can access one country by using the method get with the parameters being the json keys of the .json files in the share/iso-codes/json folder

##### Example

```python
>>> from isocodes import countries
>>> countries.get(name="Germany")
{'alpha_2': 'DE', 'alpha_3': 'DEU', 'flag': '🇩🇪', 'name': 'Germany', 'numeric': '276', 'official_name': 'Federal Republic of Germany'}

# Now with dot notation access:
>>> germany = countries.get(name="Germany")
>>> germany.name
'Germany'
>>> germany.flag
'🇩🇪'
```

### Items property

You can get a list from the .json files in the share/iso-codes/json folder with the items property. Each item now supports both dictionary and dot notation access:

##### Example

```python
>>> from isocodes import countries
>>> for country in countries.items:
...     print(f"{country.name} - {country.flag}")  # Dot notation
...     print(country["alpha_2"])                   # Dict access
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
('004', <Country: Afghanistan>)  # Now returns enhanced objects
>>> country = countries.by_numeric[0][1]
>>> country.name
'Afghanistan'
>>> country.flag
'🇦🇫'
```

### Former country names lookup (Enhanced!)

You can look up countries by their former names using the `get_by_former_name` method. Now with full dot notation support!

##### Example

```python
>>> from isocodes import countries

# Look up Eswatini by its former name (now with dot notation):
>>> eswatini = countries.get_by_former_name("Swaziland")
>>> eswatini.name
'Eswatini'
>>> eswatini.flag
'🇸🇿'
>>> f"{eswatini.name} ({eswatini.alpha_2})"
'Eswatini (SZ)'

# Look up Myanmar by its former name:
>>> myanmar = countries.get_by_former_name("Burma")
>>> f"{myanmar.name} - {myanmar.flag}"
'Myanmar - 🇲🇲'

# Get information about former names (including dissolved countries):
>>> countries.get_former_names_info("Czechoslovakia")
{'alpha_2': None, 'alpha_3': None, 'current_name': None, 'change_date': '1993-01-01', 'comment': 'Split into Czech Republic (CZ/CZE) and Slovakia (SK/SVK)'}

# Get list of all available former names:
>>> countries.former_names[:5]
['Swaziland', 'Burma', 'Zaire', 'Czechoslovakia', 'Yugoslavia']
```


## Other ISO Standards

All other ISO datasets now support the same enhanced functionality with dot notation access and performance improvements:

### Languages (ISO 639-2)

```python
>>> from isocodes import languages
>>> english = languages.get(alpha_3="eng")
>>> english.name
'English'
>>> # Search for languages
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
>>> from isocodes import extendend_languages  # Note: typo preserved for compatibility
>>> mandarin = extendend_languages.find(alpha_3="cmn")
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

## Performance Benefits

The enhanced implementation provides significant performance improvements:

- **O(1) lookups** with `find()` method for common fields (alpha_2, alpha_3, name, numeric)
- **Indexed dictionaries** for direct access: `countries.by_alpha_2_dict["US"]`
- **Search functionality** for flexible filtering: `countries.search(name="Island")`
- **Memory efficient** - reasonable overhead for substantial capability gains

## Backward Compatibility

**100% backward compatible** - All existing code continues to work:

```python
# All these still work exactly as before:
country = countries.get(alpha_2="US")
print(country["name"])           # Dictionary access
print(country.get("alpha_3"))    # .get() method  
print("flag" in country)         # 'in' operator
print(len(country))              # len() function
print(isinstance(country, dict)) # isinstance() check

# Plus new dot notation:
print(country.name)              # New! Dot notation
print(country.flag)              # New! Direct attribute access
```

## Translations

Translations are included in this project with gettext support. The domain names are to be found on https://salsa.debian.org/iso-codes-team/iso-codes

### Example

    >>> import gettext
    >>> import isocodes
    >>> french = gettext.translation('iso_639-2', isocodes.LOCALES_DIR, languages=['fr'])
    >>> french.install()
    >>> _("French")
    'français'

# Develop

## Update iso-codes version

    bash update.sh