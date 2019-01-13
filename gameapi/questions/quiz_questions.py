import math

import gameapi.questions.facts as facts

from .quiz_helpers import *


def q_german_chancellor_party():
    """Ask which party a German Chancellor was or is affiliated with."""
    question = QuestionGenerator()
    question.set_type('politics')

    # select chancellor for question
    all_chancellors = facts.get_german_chancellors_list()
    chancellor = random.choice(all_chancellors)

    # formulate question
    is_current = facts.get_german_chancellors_years(chancellor)[1] is None
    is_male = 'male' == facts.get_german_chancellors_gender(chancellor)
    word_gehoert = "gehört" if is_current else "gehörte"
    word_kanzler = "Bundeskanzler" if is_male else "Bundeskanzlerin"
    question.ask(f"Welcher Partei {word_gehoert} {word_kanzler} {chancellor} an")

    # answer
    party = facts.get_german_chancellors_party(chancellor)
    question.set_answer(party)

    # other options
    other_parties = facts.get_german_chancellors_parties_set().difference([party])
    for party in other_parties:
        question.add_wrong_option(party)
    question.add_wrong_option("FDP")

    return question.create(num_options=3)


def q_german_chancellor_after():
    """Ask who succeeded a German Chancellor."""
    question = QuestionGenerator()
    question.set_type('politics')

    # select chancellor for question
    all_chancellors = facts.get_german_chancellors_list()
    chancellor = random.choice(all_chancellors[:-1])  # skip current

    # formulate question
    question.ask(f"Welcher Bundeskanzler folgte nach {chancellor}")

    # answer (use last name as alias)
    successor = all_chancellors[all_chancellors.index(chancellor) + 1]
    question.set_answer(successor, aliases=[successor.split()[-1]])

    # other options (use last name as alias)
    other_chancellors = [c for c in all_chancellors if c != chancellor and c != successor]
    for chancellor in other_chancellors:
        question.add_wrong_option(chancellor, aliases=[chancellor.split()[-1]])

    return question.create(num_options=3)


def q_us_president_party():
    """Ask which party a US President was or is affiliated with."""
    question = QuestionGenerator()
    question.set_type('politics')

    # select chancellor for question
    presidents_selection = facts.get_us_presidents_list()[-12:]
    president = random.choice(presidents_selection)

    # formulate question
    is_current = facts.get_us_presidents_years(president)[1] is None
    word_war = "Ist" if is_current else "War"
    question.ask(f"{word_war} U S Präsident {president.replace('.', '')} Republikaner oder Demokrat")

    # answer
    party = facts.get_us_presidents_party(president)
    print(party)
    question.set_answer("Republikaner" if party == 'Republican' else "Demokrat")

    # other options
    question.add_wrong_option("Republikaner" if party != 'Republican' else "Demokrat")

    # make sure the answers are sorted
    def is_sorted(options):
        return options[0][0] == "Republikaner"

    return question.create(num_options=2, check_sort=is_sorted)


def q_us_president_after():
    """Ask who succeeded a US President."""
    question = QuestionGenerator()
    question.set_type('politics')

    # select president for question
    presidents_selection = facts.get_us_presidents_list()[-15:]  # only recent
    president = random.choice(presidents_selection[:-1])  # skip current

    # formulate question
    question.ask(f"Welcher U S Präsident folgte nach {president.replace('.', '')}")

    # answer (use last name as alias)
    successor = presidents_selection[presidents_selection.index(president) + 1]
    question.set_answer(successor.replace('.', ''), aliases=[successor, successor.split()[-1]])

    # other options (use last name as alias)
    other_presidents = [p for p in presidents_selection if p != president and p != successor]
    for president in other_presidents:
        question.add_wrong_option(president.replace('.', ''), aliases=[president, president.split()[-1]])

    return question.create(num_options=3)


def q_geography_capital():
    """Ask what the capital of a given country is."""
    question = QuestionGenerator()
    question.set_type('geography')

    # select country
    all_countries = facts.get_geography_countries_list()
    country = random.choice(all_countries)

    # formulate question
    question.ask(f"Was ist die Hauptstadt von {country}")

    # answer
    capital = facts.get_geography_capital(country)
    question.set_answer(capital)

    # other options
    other_capitals = [c for c in facts.get_geography_capitals_set() if c != capital]
    for c in other_capitals:
        question.add_wrong_option(c)

    return question.create(num_options=3)


def q_geography_country():
    """Ask of which  of a given country is."""
    question = QuestionGenerator()
    question.set_type('geography')

    # select country and capital
    all_countries = facts.get_geography_countries_list()
    country = random.choice(all_countries)
    capital = facts.get_geography_capital(country)

    # formulate question
    question.ask(f"Von welchem Land ist {capital} die Hauptstadt")

    # answer
    question.set_answer(country)

    # other options
    other_countries = [c for c in all_countries if c != country]
    for c in other_countries:
        question.add_wrong_option(c)

    return question.create(num_options=3)


def q_geography_country_population_higher():
    """Ask which country has a higher population than a given country."""
    question = QuestionGenerator()
    question.set_type('geography')

    # select country and capital
    all_countries = facts.get_geography_countries_list()
    country = random.choice(all_countries[10:-10])  # the correct answer will be after (higher)

    # formulate question
    question.ask(f"Welches dieser Länder hat mehr Einwohner als {country}")

    # answer
    index = all_countries.index(country)
    higher = all_countries[index + 1 + 3:]
    question.set_answer(random.choice(higher))

    # other options
    lower = all_countries[:index - 3]
    for country in lower:
        question.add_wrong_option(country)

    return question.create(num_options=3)


def q_geography_population_estimate():
    """Ask a question about estimating the coutry's population."""

    def millify(n):
        """https://stackoverflow.com/a/3155023"""
        millnames = ['', ' Tausend', ' Million', ' Milliarde', ' Billion']
        n = float(n)
        millidx = max(0, min(len(millnames) - 1,
                             int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

        word = millnames[millidx]
        num_formatted = '{:.0f}'.format(n / 10 ** (3 * millidx))
        if int(num_formatted) > 1 and millidx >= 2:
            word += "en"
        return '{:.0f}{}'.format(n / 10 ** (3 * millidx), word)

    def millify_int(n):
        millnames = ['', '000', '000000', '000000000', '000000000000']
        n = float(n)
        millidx = max(0, min(len(millnames) - 1,
                             int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

        return int('{:.0f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx]))

    question = QuestionGenerator()
    question.set_type('geography')

    # select country and capital
    all_countries = facts.get_geography_countries_list()
    country = random.choice(all_countries)

    # formulate question
    question.ask(f"Wie viele Einwohner hat {country}")

    # answer
    exact_pop = int(facts.get_geography_population(country))
    question.set_answer(millify(exact_pop), aliases=[millify_int(exact_pop)])

    # other options
    multipliers = [.6, .7, .8, 1.2, 1.4, 1.6, 1.8]
    random.shuffle(multipliers)
    for m in multipliers[:2]:
        question.add_wrong_option(millify(m * exact_pop), aliases=[millify_int(m * exact_pop)])

    # make sure the answers are sorted
    def is_sorted(options):
        for i in range(len(options) - 1):
            if options[i][1] > options[i + 1][1]:  # check alias
                return False
        return True

    return question.create(num_options=3, check_sort=is_sorted)
