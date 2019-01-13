import random

from tinydb import TinyDB, Query

from gameapi.helpers import assoc

wiki_associations = TinyDB("data/game_data/wiki_assoc.json", sort_keys=True, indent=4, separators=(',', ': '))


class AssocQuestion:

    def __init__(self, question, suggested_associations):
        self.question = question
        self.suggested_associations = suggested_associations
        self.chosen_associations = self.suggested_associations


def get_next_assoc_question(number):
    """
    Return the next association question, with number between [0, 2]
    """
    entities = [
        "Angela Merkel",
        "Donald Trump",
        "Barack Obama"
    ]
    entity = entities[number]
    associations = suggested_associations(entity)

    # select 5 associations
    selected_assocs = associations[1:4]
    as_text = ', '.join(selected_assocs)

    query_question = f"Welche der folgenden Assoziationen zu {entity} erscheinen dir am wichtigsten?"

    output = f"{query_question}\n\n{as_text}"

    q = assoc.create_question(query_entity=entity, query_associations=selected_assocs, output=output)
    return q


def suggested_associations(title):
    entry = Query()
    row = wiki_associations.search(entry.title == title)
    if row is None:
        return None
    else:
        return row[0]['associations']
