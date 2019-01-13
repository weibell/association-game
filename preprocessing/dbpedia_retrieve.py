import csv
import os

from SPARQLWrapper import SPARQLWrapper, JSON

if not os.path.exists("../data"):
    os.makedirs("../data")
if not os.path.exists("../data/game_data"):
    os.makedirs("../data/game_data")


def store_all():
    """
    german_chancellors()
    german_chancellors_gender()
    german_chancellors_years()
    german_chancellors_party()
    us_presidents()
    us_presidents_gender()
    us_presidents_years()
    us_presidents_party()
    """


def sparql_query(query):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()['results']['bindings']


def save(data, title, columns=None):
    filename = f"../data/game_data/{title}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        if columns is None:
            columns = list(data[0].keys())
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(columns)
        for row in data:
            csvwriter.writerow([row[column]['value'] for column in columns])


def german_chancellors():
    query = """
        PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX  dbp:  <http://dbpedia.org/property/>
        PREFIX  dbc:  <http://dbpedia.org/resource/Category:>
        PREFIX  dct:  <http://purl.org/dc/terms/>
        PREFIX  dbr:  <http://dbpedia.org/resource/>
        
        SELECT  (str(?chancellor_name) AS ?chancellor)
        WHERE
          { ?chancellor_  rdfs:label  ?chancellor_name ;
                      dct:subject  dbc:Chancellors_of_Germany ;
                      dbp:title    dbr:Chancellor_of_Germany
            FILTER ( lang(?chancellor_name) = "de" )
          }
        ORDER BY ?chancellor
    """
    result = sparql_query(query)
    save(result, 'german_chancellors')


def german_chancellors_gender():  #
    query = """
        PREFIX  dbp:  <http://dbpedia.org/property/>
        PREFIX  dbc:  <http://dbpedia.org/resource/Category:>
        PREFIX  dct:  <http://purl.org/dc/terms/>
        PREFIX  dbr:  <http://dbpedia.org/resource/>
        PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX  foaf: <http://xmlns.com/foaf/0.1/>
        
        SELECT  (str(?chancellor_name) AS ?chancellor) (str(?gender_) AS ?gender)
        WHERE
          { ?chancellor_  rdfs:label  ?chancellor_name ;
                      dct:subject  dbc:Chancellors_of_Germany ;
                      dbp:title    dbr:Chancellor_of_Germany ;
                      foaf:gender  ?gender_
            FILTER ( lang(?chancellor_name) = "de" )
          }
        ORDER BY ?chancellor
    """
    result = sparql_query(query)
    save(result, 'german_chancellors_gender', columns=('chancellor', 'gender'))


def german_chancellors_years():
    query = """
        PREFIX  dbo:  <http://dbpedia.org/ontology/>
        PREFIX  dbp:  <http://dbpedia.org/property/>
        PREFIX  dbc:  <http://dbpedia.org/resource/Category:>
        PREFIX  dct:  <http://purl.org/dc/terms/>
        PREFIX  dbr:  <http://dbpedia.org/resource/>
        PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT (MIN(year(?election_date)) AS ?year_begin) (str(?chancellor_name) AS ?chancellor)
        WHERE
          { ?chancellor_  rdfs:label   ?chancellor_name ;
                      dct:subject      dbc:Chancellors_of_Germany ;
                      dbp:title        dbr:Chancellor_of_Germany .
            ?election  dbo:firstLeader  ?chancellor_ ;
                      dbo:startDate    ?election_date
            FILTER ( lang(?chancellor_name) = "de" )
          }
        GROUP BY ?chancellor_name
        ORDER BY ?year_begin
    """
    result = sparql_query(query)

    result.insert(4, {'chancellor': {'value': "Helmut Schmidt"}, 'year_begin': {'value': 1974}})
    for (i, row) in enumerate(result):
        if row['chancellor']['value'] == "Ludwig Erhard":
            row['year_begin']['value'] = 1963
        if row['chancellor']['value'] == "Kurt Georg Kiesinger":
            row['year_begin']['value'] = 1966
        if row['chancellor']['value'] == "Willy Brandt":
            row['year_begin']['value'] = 1969
        if row['chancellor']['value'] == "Helmut Kohl":
            row['year_begin']['value'] = 1982
        if row['chancellor']['value'] == "Angela Merkel":
            row['year_end'] = {'value': ''}

        if i > 0:
            result[i - 1]['year_end'] = {'value': row['year_begin']['value']}

    save(result, 'german_chancellors_years', columns=('year_begin', 'year_end', 'chancellor'))


def german_chancellors_party():
    query = """
        PREFIX  dbo:  <http://dbpedia.org/ontology/>
        PREFIX  dbp:  <http://dbpedia.org/property/>
        PREFIX  dbc:  <http://dbpedia.org/resource/Category:>
        PREFIX  dct:  <http://purl.org/dc/terms/>
        PREFIX  dbr:  <http://dbpedia.org/resource/>
        PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT  (str(?chancellor_name) AS ?chancellor) (str(?party_abbreviation) AS ?party)
        WHERE
          { ?chancellor_  rdfs:label  ?chancellor_name ;
                      dct:subject  dbc:Chancellors_of_Germany ;
                      dbp:title    dbr:Chancellor_of_Germany ;
                      dbo:party    ?party_

            # Ludwig Erhard
            OPTIONAL
              { ?chancellor_  dbo:otherParty  ?other_party .
                ?other_party  dbp:abbreviation  ?party_abbreviation
              }

            # Angela Merkel
            OPTIONAL
              { ?party_   dbo:wikiPageRedirects  ?party_redirect .
                ?party_redirect
                          dbp:abbreviation      ?party_abbreviation
              }
            OPTIONAL
              { ?party_  dbp:abbreviation  ?party_abbreviation }
            FILTER ( ( str(?party_abbreviation) = "CDU" ) || ( str(?party_abbreviation) = "SPD" ) )
            FILTER ( lang(?chancellor_name) = "de" )
          }
        ORDER BY ?chancellor
    """
    result = sparql_query(query)
    save(result, 'german_chancellors_party', columns=('chancellor', 'party'))


def us_presidents():
    query = """
        PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX  dct:  <http://purl.org/dc/terms/>
        PREFIX  dbc:  <http://dbpedia.org/resource/Category:>
        PREFIX  foaf: <http://xmlns.com/foaf/0.1/>
        
        SELECT  (str(?president_name) AS ?president)
        WHERE
          { ?president_  dct:subject  dbc:Presidents_of_the_United_States ;
                      rdfs:label   ?president_name ;
                      foaf:gender  ?gender_
            FILTER ( lang(?president_name) = "en" )
          }
        ORDER BY ?president
    """
    result = sparql_query(query)
    result.append({'president': {'value': "Donald Trump"}})

    save(result, 'us_presidents')


def us_presidents_gender():
    query = """
        PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX  dct:  <http://purl.org/dc/terms/>
        PREFIX  dbc:  <http://dbpedia.org/resource/Category:>
        PREFIX  foaf: <http://xmlns.com/foaf/0.1/>
        
        SELECT  (str(?president_name) AS ?president) (str(?gender_) AS ?gender)
        WHERE
          { ?president_  dct:subject  dbc:Presidents_of_the_United_States ;
                      rdfs:label   ?president_name ;
                      foaf:gender  ?gender_
            FILTER ( lang(?president_name) = "en" )
          }
        ORDER BY ?president
    """
    result = sparql_query(query)
    result.append({'president': {'value': "Donald Trump"}, 'gender': {'value': 'male'}})

    save(result, 'us_presidents_gender', columns=('president', 'gender'))


def us_presidents_years():
    query = """
        PREFIX  dbo:  <http://dbpedia.org/ontology/>
        PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX  dbp:  <http://dbpedia.org/property/>
        PREFIX  dct:  <http://purl.org/dc/terms/>
        PREFIX  dbc:  <http://dbpedia.org/resource/Category:>
        
        SELECT  (MAX(?year_start) AS ?year_begin) (str(?president_name) AS ?president)
        WHERE
          { ?president_  dct:subject  dbc:Presidents_of_the_United_States ;
                      rdfs:label     ?president_name ;
                      dbo:birthDate  ?birth_date
            OPTIONAL
              { ?president_  dbp:presidentStart  ?year_start }
            OPTIONAL
              { ?president_  dbp:presidentDate  ?year_start }
            OPTIONAL
              { ?president_  dbo:activeYearsStartDate  ?year_start }
            FILTER ( lang(?president_name) = "en" )
          }
        GROUP BY ?president_name
        ORDER BY ?year_begin
    """

    result = sparql_query(query)

    result.append({'president': {'value': "Grover Cleveland"}, 'year_begin': {'value': 1885}})
    result.append({'president': {'value': "Donald Trump"}, 'year_begin': {'value': 2017}, 'year_end': {'value': ''}})

    for row in result:
        if row['president']['value'] == "George Washington":
            row['year_begin'] = {'value': 1789}
        if row['president']['value'] == "Theodore Roosevelt":
            row['year_begin'] = {'value': 1901}
        if row['president']['value'] == "Dwight D. Eisenhower":
            row['year_begin'] = {'value': 1953}
        if row['president']['value'] == "Richard Nixon":
            row['year_begin'] = {'value': 1969}
        if row['president']['value'] == "Jimmy Carter":
            row['year_begin'] = {'value': 1977}

        # force 4-digit year
        year = row['year_begin']['value']
        if isinstance(year, str):
            row['year_begin']['value'] = int(year[:4])

    def pres_sort(row):
        """Some presidents were only in office for one year"""
        if row['president']['value'] in ("William Henry Harrison", "James A. Garfield"):
            return row['year_begin']['value'] - .5
        else:
            return row['year_begin']['value']

    result.sort(key=pres_sort)

    for (i, row) in enumerate(result):
        if i > 0:
            result[i - 1]['year_end'] = {'value': row['year_begin']['value']}

    save(result, 'us_presidents_years', columns=('year_begin', 'year_end', 'president'))


def us_presidents_party():
    query = """
        PREFIX  dbo:  <http://dbpedia.org/ontology/>
        PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX  dct:  <http://purl.org/dc/terms/>
        PREFIX  dbc:  <http://dbpedia.org/resource/Category:>
        
        SELECT  (str(?president_name) AS ?president) (str(?party_name) AS ?party)
        WHERE
          { ?president_  dct:subject  dbc:Presidents_of_the_United_States ;
                      rdfs:label     ?president_name ;
                      dbo:birthDate  ?birth_date ;
                      dbo:party      ?party_ .
            ?party_   rdfs:label     ?party_name
            FILTER ( ( str(?party_name) = "Republican Party (United States)" )
                || ( str(?party_name) = "Democratic Party (United States)" ) 
                || ( str(?party_name) = "Democratic-Republican Party" ) )
            FILTER ( lang(?president_name) = "en" )
            FILTER ( lang(?party_name) = "en" )
          }
        GROUP BY ?president_name ?party_name
        ORDER BY ?president
    """

    result = sparql_query(query)
    exclude = ("Ulysses S. Grant", "John Tyler", "Martin Van Buren", "William Henry Harrison")
    result = [row for row in result if row['president']['value'] not in exclude]

    for row in result:
        if row['party']['value'] == "Republican Party (United States)":
            row['party']['value'] = "Republican"
        if row['party']['value'] == "Democratic Party (United States)":
            row['party']['value'] = "Democratic"
        if row['party']['value'] == "Democratic-Republican Party":
            row['party']['value'] = "Democratic-Republican"

    for president in ["Martin Van Buren"]:
        result.append({'president': {'value': president}, 'party': {'value': "Democratic"}})
    for president in ["Ulysses S. Grant", "Donald Trump"]:
        result.append({'president': {'value': president}, 'party': {'value': "Republican"}})
    for president in []:
        result.append({'president': {'value': president}, 'party': {'value': "Democratic-Republican"}})
    for president in ["George Washington", "John Tyler"]:
        result.append({'president': {'value': president}, 'party': {'value': ""}})
    for president in ["John Adams"]:
        result.append({'president': {'value': president}, 'party': {'value': "Federalist"}})
    for president in ["William Henry Harrison", "Zachary Taylor", "Millard Fillmore"]:
        result.append({'president': {'value': president}, 'party': {'value': "Whig"}})

    result.sort(key=lambda row: row['president']['value'])

    save(result, 'us_presidents_party', columns=('president', 'party'))


def geography():
    query = """
        PREFIX  :     <http://dbpedia.org/resource/>
        PREFIX  dbo:  <http://dbpedia.org/ontology/>
        PREFIX  rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX  dbp:  <http://dbpedia.org/property/>
        PREFIX  db:   <http://dbpedia.org/>
        
        SELECT DISTINCT  (str(?country_) AS ?country) (str(?capital_) AS ?capital) ?population
        WHERE
          { ?ca  rdfs:label            ?capital_ .
            ?co  rdfs:label            ?country_ ;
                 a                     dbo:Country ;
                 dbo:capital           ?ca ;
                 dbp:callingCode       ?cc ;
                 dbo:populationTotal   ?population
            FILTER ( ?population > 10000000 )
            FILTER ( lang(?country_) = "de" )
            FILTER ( lang(?capital_) = "de" )
          }
        ORDER BY ?population
    """
    result = sparql_query(query)

    save(result, 'geography', columns=('country', 'capital', 'population'))
    # minor edits were performed by hand, e.g. "Republik China (Taiwan)" -> "Taiwan"


if __name__ == "__main__":
    # store_all()
    geography()
