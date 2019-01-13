import csv
import os


def load(title):
    """
    Load CSV data from the given file name.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))

    filename = f"{dir_path}/data/game_data/{title}.csv"
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            data = [row for row in csvreader]
    except FileNotFoundError:
        filename = f"{dir_path}/../../data/game_data/{title}.csv"
        with open(filename, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            data = [row for row in csvreader]
    return data


def get_german_chancellors_set():
    """Return the unordered set of names of German Chancellors. """
    data = load('german_chancellors')
    return set(row['chancellor'] for row in data)


def get_german_chancellors_list():
    """Return the ordered list of names of German Chancellors, sorted by year of inauguration. """
    data = load('german_chancellors_years')
    return [row['chancellor'] for row in data]


def get_german_chancellors_gender(chancellor):
    """Given the name of a German Chancellor, return his or her gender, or None if not found. """
    data = load('german_chancellors_gender')
    for row in data:
        if row['chancellor'] == chancellor:
            return row['gender']
    return None


def get_german_chancellors_party(chancellor):
    """Given the name of a German Chancellor, return his or her party, or None if not found. """
    data = load('german_chancellors_party')
    for row in data:
        if row['chancellor'] == chancellor:
            return row['party']
    return None


def get_german_chancellors_parties_set():
    """Return the set of parties that German Chancellors belonged to."""
    data = load('german_chancellors_party')
    return set(row['party'] for row in data)


def get_german_chancellors_years(chancellor):
    """Given the name of a German Chancellor, return a tuple of his or her start and end year. If currently serving,
    return None as end year. """
    data = load('german_chancellors_years')
    for row in data:
        if row['chancellor'] == chancellor:
            if row['year_end'] != '':
                return int(row['year_begin']), int(row['year_end'])
            else:
                return int(row['year_begin']), None
    return None


def get_us_presidents_set():
    """Return the unordered set of names of US Presidents. """
    data = load('us_presidents')
    return set(row['president'] for row in data)


def get_us_presidents_list():
    """Return the ordered list of names of US Presidents, sorted by year of inauguration. Note that George Cleveland,
    who served two non-consecutive terms, is listed twice. """
    data = load('us_presidents_years')
    return [row['president'] for row in data]


def get_us_presidents_gender(president):
    """Given the name of a US President, return his gender, or None if not found. """
    data = load('us_president_gender')
    for row in data:
        if row['president'] == president:
            return row['gender']
    return None


def get_us_presidents_party(president):
    """Given the name of a US President, return his party, or None if not found. Unaffiliated Presidents return an
    empty string. """
    data = load('us_presidents_party')
    for row in data:
        if row['president'] == president:
            return row['party']
    return None


def get_us_presidents_parties_set():
    """Return the set of parties that US Presidents belonged to."""
    data = load('us_presidents_party')
    return set(row['party'] for row in data)


def get_us_presidents_years(president):
    """Given the name of a US President, return a tuple of his start and end year. If currently serving, return None
    as end year. For Grover Cleveland, return data for the first term. """
    data = load('us_presidents_years')
    for row in data:
        if row['president'] == president:
            if row['year_end'] != '':
                return int(row['year_begin']), int(row['year_end'])
            else:
                return int(row['year_begin']), None
    return None


def get_geography_capitals_set():
    """Get a set of capitals"""
    data = load('geography')
    return set(row['capital'] for row in data)


def get_geography_countries_list():
    """Get a list of countries ordered by population size."""
    data = load('geography')
    return [row['country'] for row in data]


def get_geography_capital(country):
    data = load('geography')
    for row in data:
        if row['country'] == country:
            return row['capital']
    return None


def get_geography_population(country):
    data = load('geography')
    for row in data:
        if row['country'] == country:
            return row['population']
    return None
