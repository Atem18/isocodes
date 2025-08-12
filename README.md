# isocodes

isocodes provides you access to lists of various ISO standards (e.g. country, language, language scripts, and currency names).

The data is coming from https://salsa.debian.org/iso-codes-team/iso-codes, many thanks to them.

# Installation

    pip install isocodes

# Usage

## Countries (ISO 3166)

### Get method

You can acces one country by using the method get with the parameters being the json keys of the .json files in the share/iso-codes/json folder

#### Example

    >>> from isocodes import countries
    >>> countries.get(name="Germany")
    {'alpha_2': 'DE', 'alpha_3': 'DEU', 'flag': '🇩🇪', 'name': 'Germany', 'numeric': '276', 'official_name': 'Federal Republic of Germany'}

### Items property

You can get a json parsed list from the .json files in the share/iso-codes/json folder with the items property.

That list contains each countries in the form of the dictionary that you can get with the method get.

#### Example

    >>> from isocodes import countries
    >>> for country in countries.items:
    ...     print(country)
    ...
    {'alpha_2': 'AW', 'alpha_3': 'ABW', 'flag': '🇦🇼', 'name': 'Aruba', 'numeric': '533'}
    {'alpha_2': 'AF', 'alpha_3': 'AFG', 'flag': '🇦🇫', 'name': 'Afghanistan', 'numeric': '004', 'official_name': 'Islamic Republic of Afghanistan'}
    {'alpha_2': 'AO', 'alpha_3': 'AGO', 'flag': '🇦🇴', 'name': 'Angola', 'numeric': '024', 'official_name': 'Republic of Angola'}
    {'alpha_2': 'AI', 'alpha_3': 'AIA', 'flag': '🇦🇮', 'name': 'Anguilla', 'numeric': '660'}
    {'alpha_2': 'AX', 'alpha_3': 'ALA', 'flag': '🇦🇽', 'name': 'Åland Islands', 'numeric': '248'}

### by_xxx property

You can get a list with sorted data by one of the property with the by_xxx property, xxx being one of the data key (alpha_2, name, numeric, etc.).

#### Example

    >>> countries.by_numeric[0]
    ('004', {'alpha_2': 'AF', 'alpha_3': 'AFG', 'flag': '🇦🇫', 'name': 'Afghanistan', 'numeric': '004', 'official_name': 'Islamic Republic of Afghanistan'})

### Former country names lookup

You can look up countries by their former names using the `get_by_former_name` method. This is useful for countries that have changed names over time but kept their country codes.

#### Example

    >>> from isocodes import countries
    >>> # Look up Eswatini by its former name
    >>> countries.get_by_former_name("Swaziland")
    {'alpha_2': 'SZ', 'alpha_3': 'SWZ', 'flag': '🇸🇿', 'name': 'Eswatini', 'numeric': '748', 'official_name': 'Kingdom of Eswatini'}
    
    >>> # Look up Myanmar by its former name
    >>> countries.get_by_former_name("Burma")
    {'alpha_2': 'MM', 'alpha_3': 'MMR', 'flag': '🇲🇲', 'name': 'Myanmar', 'numeric': '104', 'official_name': 'Republic of the Union of Myanmar'}
    
    >>> # Get information about former names (including dissolved countries)
    >>> countries.get_former_names_info("Czechoslovakia")
    {'alpha_2': None, 'alpha_3': None, 'current_name': None, 'change_date': '1993-01-01', 'comment': 'Split into Czech Republic (CZ/CZE) and Slovakia (SK/SVK)'}
    
    >>> # Get list of all available former names
    >>> countries.former_names
    ['Swaziland', 'Burma', 'Zaire', 'Czechoslovakia', 'Yugoslavia', 'Soviet Union', 'USSR']


## Languages (ISO 639-2)

Same as countries but you replace countries by languages

## Currencies (ISO 4217)

Same as countries but you replace countries by currencies

## Countries and Subdivisions (ISO 3166-2)

Same as countries but you replace countries by subdivisions_countries

## Former countries (ISO 3166-3)

Same as countries but you replace countries by former_countries

## Extended languages (ISO 639-3)
Same as countries but you replace countries by extendend_languages

## Language families (ISO 639-5)
Same as countries but you replace countries by language_families

## Script names (ISO 15924)
Same as countries but you replace countries by script_names

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