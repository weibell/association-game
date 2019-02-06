from collections import Counter, OrderedDict

import postprocessing.db as db


def relevancy(assocation, entity):
    """Applies the proposed relevancy formula and returns a relevancy score."""

    def score(q):
        """Scores user's competence in topic surrounding the association's topic."""
        topic = 'politics' if q['entity'] in ['Angela Merkel', 'Barack Obama', 'Donald Trump'] else 'geography'

        session = [session for session in db.session_data() if q['id'] in session['assoc_questions']][0]
        quiz_question_ids = session['quiz_questions']
        quiz_questions = [q for q in db.quiz_question_data()
                          if q['id'] in quiz_question_ids and q['type'] == topic]
        num_correct = len([q for q in quiz_questions if q['answered_correctly']])
        num_total = len(quiz_questions)

        # return scoring function
        return (1 + num_correct) / (1 + num_total)

    # filter association questions by entity and assocation
    U_ae = [q for q in db.assoc_question_data()
            if q['entity'] == entity and assocation in q['parsed_assocs']]
    alpha = 1 / 4
    beta = 3 / 4

    return alpha * len(U_ae) + beta * sum([score(q) for q in U_ae])


def session_validity_stats():
    """Output statistics about how many sessions were valid."""
    valid = db.session_data(only_valid=True)
    all = db.session_data(only_valid=False)
    print("Session Validity stats")
    print(f"total:   {len(all)}")
    print(f"valid:   {len(valid)}")
    print(f"invalid: {len(all) - len(valid)}")
    print("\n")


def quiz_questions_stats():
    """Output statistics about quiz questions."""
    c = Counter([q['answered_correctly'] for q in db.quiz_question_data()])
    total = sum(c.values())
    print("Quiz Question stats")
    print(f"total:   {total}")
    print(f"correct: {c[True]} ({c[True] / total:.2%})")
    print(f"wrong:   {c[False]} ({c[False] / total:.2%})")
    print(f"skipped: {c[None]} ({c[None] / total:.2%})")
    print("\n")


def quiz_questions_stats_detail(type):
    """Output statistics about specific quiz questions."""
    c = Counter([q['answered_correctly'] for q in db.quiz_question_data() if q['type'] == type])
    total = sum(c.values())
    print(f"Quiz Question stats for type: {type}")
    print(f"total:   {total}")
    print(f"correct: {c[True]} ({c[True] / total:.2%})")
    print(f"wrong:   {c[False]} ({c[False] / total:.2%})")
    print(f"skipped: {c[None]} ({c[None] / total:.2%})")
    print("\n")


def assoc_questions_stats():
    """Output statistics about association questions."""
    questions = db.assoc_question_data()
    print("Association Questions stats")

    politics = [q for q in questions if q['entity'] in ['Angela Merkel', 'Donald Trump', 'Barack Obama']]
    geography = [q for q in questions if q['entity'] in ['Deutschland', 'Europa', 'Vereinigte Staaten']]
    print(f"politics:  {len(politics)}")
    print(f"geography: {len(geography)}")
    print()

    entity_assocs = {}
    for q in questions:
        entity = q['entity']
        assocs = q['parsed_assocs']
        if entity not in entity_assocs:
            entity_assocs[entity] = []
        entity_assocs[entity] += assocs

    for entity, assocs in entity_assocs.items():
        print(f"Entity: {entity}")
        print(f"Number of assocations: {len(assocs)} (unique: {len(set(assocs))})")
        c = Counter(assocs)
        top_assocs = {assoc: count for assoc, count in c.items() if count >= 1}  # chose threshold
        top_assocs = reversed(sorted(top_assocs.items(), key=lambda x: x[1]))
        for assoc, count in top_assocs:
            print(count, assoc)
        print()

    print("\n")


def reasoning_questions_stats():
    """Output statistics about association questions."""
    questions = db.reasoning_question_data()
    q_why = [q for q in questions if q['type'] == "why"]
    q_explain = [q for q in questions if q['type'] == "explain"]
    print("Reasoning Question stats")
    print(f"total:     {len(questions)}")
    print(f"'why':     {len(q_why)}")
    print(f"'explain': {len(q_explain)}")
    print()

    # calculate sentence lengths
    why_lengths = Counter([len(q['raw_input'].split(' ')) for q in q_why])
    explain_lengths = Counter([len(q['raw_input'].split(' ')) for q in q_explain])
    print("why-length counter: " + str(sorted(why_lengths.items())))
    print("explain-length counter: " + str(sorted(explain_lengths.items())))
    print()

    first_word_why = Counter([q['raw_input'].split(' ')[0] for q in q_why])
    first_word_explain = Counter([q['raw_input'].split(' ')[0] for q in q_explain])
    print("First why-word: " + str(first_word_why))
    print("First explain-word: " + str(first_word_explain))
    print()

    longest_responses = [q['raw_input'] for q in questions if len(q['raw_input'].split(' ')) > 8]
    print("longest responses: ")
    print(longest_responses)
    print("\n")


def relevancy_score_stats():
    """Output statistics about the relevancy score."""
    questions = db.assoc_question_data()
    print("Relevancy Score stats")

    # politics = [q for q in questions if q['entity'] in ['Angela Merkel', 'Donald Trump', 'Barack Obama']]
    # geography = [q for q in questions if q['entity'] in ['Deutschland', 'Europa', 'Vereinigte Staaten']]

    entity_assocs = {}
    for q in questions:
        entity = q['entity']
        assocs = q['parsed_assocs']
        if entity not in entity_assocs:
            entity_assocs[entity] = []
        entity_assocs[entity] += assocs

    for entity, assocs in entity_assocs.items():
        print(f"Entity: {entity}")
        assoc_scores = {assoc: relevancy(assoc, entity) for assoc in assocs}
        for assoc, score in reversed(sorted(assoc_scores.items(), key=lambda x: x[1])):
            print(f"{assoc}: {score}")

        print()


def word_cloud_data():
    """Output data to be used for word cloud generators."""
    questions = db.reasoning_question_data()
    trump = ' '.join([q['raw_input'] for q in questions if q['entity'] == 'Donald Trump'])
    merkel = ' '.join([q['raw_input'] for q in questions if q['entity'] == 'Angela Merkel'])
    obama = ' '.join([q['raw_input'] for q in questions if q['entity'] == 'Barack Obama'])
    print(f"Word cloud data: Trump\n\n{trump}\n\n\n")
    print(f"Word cloud data: Obama\n\n{obama}\n\n\n")
    print(f"Word cloud data: Merkel\n\n{merkel}\n\n\n")
    print("\n")


if __name__ == '__main__':
    session_validity_stats()
    quiz_questions_stats()
    quiz_questions_stats_detail('politics')
    quiz_questions_stats_detail('geography')
    assoc_questions_stats()
    reasoning_questions_stats()
    word_cloud_data()
    relevancy_score_stats()
