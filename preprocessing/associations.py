import requests
import re
import os

import wikipediaapi
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query

import gameapi.questions.facts as facts

if not os.path.exists("../data"):
    os.makedirs("../data")
if not os.path.exists("../data/game_data"):
    os.makedirs("../data/game_data")

wiki_associations = TinyDB("../data/game_data/wiki_assoc.json", sort_keys=True, indent=4, separators=(',', ': '))


def store_all():
    def run(list_):
        for entry in list_:
            if wiki_associations.search(Query().title == entry):
                print(f"{entry} already stored")
                continue
            else:
                print(f"Getting assocations for {entry}")
                assoc = suggested_associations(entry)
                wiki_associations.insert({
                    'title': entry,
                    'associations': assoc
                })

    german_chancellors = facts.get_german_chancellors_list()
    us_presidents = facts.get_us_presidents_list()
    geography = [
        "Deutschland",
        "Vereinigte Staaten",
        "Europa"
    ]

    run(german_chancellors)
    run(us_presidents)
    run(geography)


def suggested_associations(wiki_title, language='de'):
    """Given a Wikipedia page title, return a list of suggested associations for this entry."""

    # The main heuristic to determine relevant associations for a given Wikipedia entry is to first gather all
    # articles that this entry's summary links to.
    wiki = wikipediaapi.Wikipedia(language)
    article = wiki.page(wiki_title)
    links = article.links

    # We encounter two problems:
    # 1. links is a dictionary, so we lose information about the order in which links appear in the article
    # 2. We are only interested in links appearing in the article's summary.
    # We can overcome this by scraping the article's page ourselves and parsing it.
    url = article.fullurl
    html = requests.get(url)
    bs = BeautifulSoup(html.text, "html.parser")

    # The summary comprises all p-elements located before (but in the same hierarchy level as) the table of contents.
    toc = bs.find(id='toc')
    summary_ps = toc.find_all_previous('p')

    # They are currently in reverse order.
    summary_ps = list(reversed(summary_ps))

    # Collect all links.
    summary_as = []
    for p in summary_ps:
        summary_as += [a for a in p.find_all('a')]

    # The link text itself may be an inflection of the article name, which can be accessed by through the 'title'
    # attribute.
    summary_references = []
    for a in summary_as:
        # Not all links point to a Wikipedia article, but those that do have a 'title' attribute.
        if a.has_attr('title'):
            title = a['title']
            if title in links:
                summary_references.append(links[title])

    # 'summary_links' now contains the list of Wikipedia articles reference in the summary and in the order of their
    # appearance.
    associations = [article.title for article in summary_references]

    # We can further improve the quality of the titles by filtering out irrelevant articles.
    irrelevant = [
        "^Liste",
        "^Hilfe:",
        "^Datei:",
        ".*Kalender$",
        ".*\d{4}.*",
        "^\d{1,2}\. \w+$"
    ]
    keep_associations = []
    for assoc in associations:
        keep = True
        for pattern in irrelevant:
            regex = re.compile(pattern)
            if regex.match(assoc):
                keep = False
                break
        if keep:
            keep_associations.append(assoc)

    associations = keep_associations

    # remove any words in parenthesis
    for (i, assoc) in enumerate(associations):
        if '(' in assoc:
            associations[i] = re.sub(" \(.*\)", '', assoc)

    return associations


if __name__ == "__main__":
    store_all()
