# isocodes

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

# Develop

Don't forget to clone the submodules as well and execute update.sh to update the debian's iso-codes repo.