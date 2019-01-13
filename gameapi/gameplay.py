import random

import gameapi.questions as questions


def next_interaction(output_context, session_context, input_context):
    """Proceed with the game."""

    class State:
        def __init__(self, name, substates=None, interactive=False, callback=None):
            self.name = name
            self.substates = substates
            self.interactive = interactive
            self.callback = callback

    # game play can be customized here
    state_machine = [
        State('UNINITIALIZED', callback=_uninitialized),
        State('INTRODUCTION', callback=_introduction),
        State('QUIZ', substates=8, callback=_quiz),
        State('QUIZ_EVALUATION', callback=_quiz_evaluation),
        State('EXPLAIN_ASSOC', callback=_explain_assoc),
        State('ASSOCIATIONS', substates=3, callback=_associations),
        State('EXPLAIN_REASONING', callback=_explain_reasoning),
        State('ASSOC_REASONING', substates=4, callback=_assoc_reasoning),
        State('END', callback=_end)
    ]

    # advance between states until the waiting flag is set and the user can reply
    while not (output_context.is_inquiry or output_context.is_closed):

        # find matching state
        for (i, current_state) in enumerate(state_machine):
            if current_state.name == session_context.get('state'):

                # handle game step
                current_state.callback(output_context, session_context, input_context)

                # check if the game should advance to the next (sub-)state
                if session_context.is_advancing:
                    session_context.is_advancing = False
                    next_state = state_machine[i + 1].name

                    if current_state.substates is not None:
                        # next substate
                        current_substate = session_context.get('substate')
                        substates_remaining = current_state.substates - current_substate
                        if substates_remaining > 0:
                            session_context.set('substate', current_substate + 1)
                        else:
                            session_context.set('state', next_state)
                            session_context.set('substate', 0)

                    else:
                        # next state
                        session_context.set('state', next_state)

                    break


def _uninitialized(output_context, session_context, _):
    output_context.say("Herzlich willkommen zu Association Game!")
    session_context.advance_state()


def _introduction(output_context, session_context, _):
    output_context.say("Ich erkläre nun zunächst den Ablauf dieses Spiels")
    output_context.say("Das Spiel besteht aus zwei Spielabschnitten")
    output_context.say("Im ersten Teil stelle ich dir acht multipel Choice-Fragen aus zwei verschiedenen "
                       "Themenbereichen")
    output_context.say("Danach geht es im zweiten Spielabschnitt darum, dass du mir hilfst, Assoziationen zu "
                       "bestimmten Begriffen herzustellen und diese besser zu verstehen")
    output_context.say("Keine Sorge, ich erkläre dir dann, was zu tun ist")
    output_context.say("Okay")
    output_context.say("Dann beginnen wir nun mit dem Quiz")
    session_context.advance_state()


def _quiz(output_context, session_context, input_context):
    current_substate = session_context.get('substate')

    # has a question already been asked?
    if current_substate > 0:
        question = session_context.get_latest_quiz_question()

        # should the question be repeated?
        if input_context.get('action') == 'user.repeat':
            output_context.say("Hier kommt noch einmal die Frage:")
            output_context.inquire(question['output'])
            return

        # did the user indicate that he doesn't know the answer?
        if input_context.get('action') == 'user.not_know':
            output_context.say("Kein Problem, dann überspringen wir diese Frage")
        else:
            # check if the answer was correct
            selected_option = input_context.selected_option(question)

            if selected_option is None:
                output_context.say("Das habe ich nicht verstanden")
                output_context.say("Du kannst übrigens sowohl mit dem Lösungswort als auch zum Beispiel mit 'Antwort "
                                   "A' antworten.")
                output_context.say("Hier noch einmal die Frage")
                output_context.inquire(question['output'])
                return

            is_correct = selected_option == question['answer_index']

            # update session data
            session_context.update_latest_quiz_question({
                'raw_input': input_context.get('raw_input'),
                'answered_correctly': is_correct
            })

            # give feedback
            if is_correct:
                output_context.say(f"Das stimmt, {question['answer'][0]} ist die richtige Antwort")
            else:
                letters = ['A', 'B', 'C', 'D']
                letter = letters[question['answer_index']]
                output_context.say(f"Das ist leider falsch")
                output_context.say(f"Richtig gewesen wäre Antwort {letter} \n\n {question['answer'][0]}")

    # check if another question should be asked
    if current_substate < 8:
        # determine next question
        q = [
            questions.quiz_questions.q_german_chancellor_party,
            questions.quiz_questions.q_german_chancellor_after,
            questions.quiz_questions.q_us_president_after,
            questions.quiz_questions.q_us_president_party,
            questions.quiz_questions.q_geography_country,
            questions.quiz_questions.q_geography_capital,
            questions.quiz_questions.q_geography_country_population_higher,
            questions.quiz_questions.q_geography_population_estimate
        ]
        question = q[current_substate]()

        if current_substate == 0:
            output_context.say("Zunächst stelle ich dir vier Fragen zum Thema Politik")
        elif current_substate == 4:
            output_context.say("Ich stelle dir nun vier Fragen zum Thema Geographie")

        output_context.say(f"Hier kommt Frage {current_substate + 1}")
        # state the question and add its data to the session
        output_context.inquire(question['output'])
        session_context.add_quiz_question(question)

    session_context.advance_state()


def _quiz_evaluation(output_context, session_context, _):
    output_context.say("Damit haben wir das Ende des ersten Spielabschnitts erreicht")
    output_context.say("Schauen wir uns mal das Ergebnis an")
    score_politics = session_context.count_correct_quiz_answers('politics')
    score_geography = session_context.count_correct_quiz_answers('geography')
    output_context.say(f"Zum Thema Politik hast du {score_politics} von 4 Fragen richtig beantwortet")
    output_context.say(f"Zum Thema Geographie {score_geography} von 4")
    session_context.advance_state()


def _explain_assoc(output_context, session_context, _):
    output_context.say("Damit sind wir auch schon beim zweiten Spielabschnitt angelangt")
    output_context.say("Hier geht es darum, dass du mir hilfst, Assoziationen zu bestimmten Begriffen herzustellen")
    output_context.say("Zum Beispiel assoziiere ich mit dem Begriff")
    output_context.say("Apfel")
    output_context.say("die Wörter\n\nObst\n\nFrucht\n\nBaum\n\nund\n\nKern")
    output_context.say("Ich werde dir nun zunächst einen Begriff nennen und welche Wörter ich damit bereits assoziiere")
    output_context.say("Es kann sein, dass ich Assoziationen erfasst habe, die weniger treffend sind")
    output_context.say("Bitte nenne mir im Anschluss mindestens zwei Assoziatione, die du persönlich für am "
                       "treffendsten hältst")
    output_context.say("Dabei kannst du Assoziationen von mir übernehmen, oder eigene nennen")
    output_context.say("Wichtig ist, dass Assoziationen nicht aus mehreren Wörtern bestehen, sondern nur "
                       "aus möglichst passenden Substantiven")
    session_context.advance_state()


def _associations(output_context, session_context, input_context):
    current_substate = session_context.get('substate')

    # has a question already been asked?
    if current_substate > 0:

        question = session_context.get_latest_assoc_question()

        combined = question['parsed_assocs'] + input_context.parse_assocs()
        # get unique
        user_assocs = []
        for assoc in combined:
            if assoc not in user_assocs:
                user_assocs.append(assoc)

        # should the question be repeated?
        if input_context.get('action') == 'user.repeat':
            output_context.say("Ich wiederhole noch einmal die letzte Frage")
            output_context.inquire(question['output'])
            return

        # did the user indicate that he doesn't know the answer?
        if input_context.get('action') == 'user.not_know' or len(user_assocs) < 1:
            output_context.say("Wenn du dich schwer tust, kannst du auch einfach meine vorgeschlagenen Assoziationen "
                               "übernehmen")
            output_context.inquire(question['output'])
            return

        session_context.update_latest_assoc_question({
            'raw_input': f"{question['raw_input']}  {input_context.get('raw_input')}".strip(),  # append
            'parsed_assocs': user_assocs
        })

        if len(user_assocs) < 2:
            output_context.say(f"Ich habe nur 'eine' Assoziation erkannt\n\n{user_assocs[0]}\n\nBitte nenne noch "
                               f"mindestens, eine weitere Assoziation")
            output_context.inquire()
            return

        thanks = [
            "Vielen Dank",
            "Okay"
        ]
        output_context.say(random.choice(thanks))
        output_context.say("Ich habe mir notiert: ")
        for assoc in user_assocs[:-1]:
            output_context.say(assoc)
        output_context.say(f"und {user_assocs[-1]}")

    # check if another question should be asked
    if current_substate < 3:
        stronger_topic = session_context.stronger_topic()

        if current_substate == 0:
            if stronger_topic == 'politics':
                output_context.say("Ich stelle dir nun drei Assoziations-Fragen aus dem Bereich Politik")
            else:
                output_context.say("Ich stelle dir nun drei Assoziations-Fragen aus dem Bereich Geographie")

        output_context.say(f"Hier kommt Assoziations-Frage Nummer {current_substate + 1}")

        # taken from wiki_assocs.json
        q_politics = [
            ["Barack Obama", ["Honolulu", "Hawaii", "Politiker", "Rechtsanwalt"]],
            ["Donald Trump", ["Queens", "Unternehmer", "Unterhaltungsk\u00fcnstler", "Mischkonzern"]],
            ["Angela Merkel", ["Hamburg", "Deutschland", "Politiker", "Bundeskanzler"]]
        ]
        q_geography = [
            ["Deutschland", ["Bundesstaat", "Mitteleuropa", "Land", "Sozialstaat"]],
            ["Vereinigte Staaten", ["Amerika", "Bundesstaat", "Territorium", "Alaska"]],
            ["Europa", ["Erdteil", "Eurasien", "Subkontinent", "Asien"]]
        ]

        topic = q_politics if stronger_topic == 'politics' else q_geography
        entity = topic[current_substate][0]
        assocs = topic[current_substate][1]

        output = []

        if stronger_topic == 'politics':
            output.append(f"Es geht um {entity}")
        else:
            output.append(f"Es geht um den Begriff {entity}")

        output.append(f"Mir sind folgende Assoziationen zu {entity} bekannt")
        for assoc in assocs[:-1]:
            output.append(assoc)
        output.append(f"und {assocs[-1]}")

        if current_substate < 1:
            output.append(f"Bitte nenne mir nun mindestens zwei Assoziationen, die du persönlich für besonders passend "
                          f"hältst, wenn du an {entity} denkst")
        else:
            output.append(f"Was verbindest du mit {entity} \n\nBitte nenne mindestens zwei Assoziationen")

        output = '\n\n'.join(output)
        output_context.say(output)
        session_context.add_assoc_question({
            'id': None,
            'entity': entity,
            'output': output,
            'raw_input': '',
            'parsed_assocs': []
        })

        output_context.inquire()

    session_context.advance_state()


def _explain_reasoning(output_context, session_context, _):
    output_context.say("Zum Abschluss möchte ich dich noch zu einigen deiner Assoziationen befragen")
    output_context.say("Hier kannst du ruhig etwas freier antworten")
    session_context.advance_state()


def _assoc_reasoning(output_context, session_context, input_context):
    current_substate = session_context.get('substate')

    # first, prepare reasoning questions
    if current_substate == 0:
        assoc_data = session_context.get_associations()
        entity_associations = [[a[0], a[1][0]] for a in assoc_data] + [[a[0], a[1][1]] for a in assoc_data]
        random.shuffle(entity_associations)

        # why questions
        for a in entity_associations[:2]:
            entity = a[0]
            association = a[1]
            session_context.add_reasoning_question({
                'id': None,
                'association': association,
                'entity': entity,
                'type': 'explain',
                'output': f"Bitte erläutere den Zusammenhang zwischen deiner Assoziation \n{association} \nund dem "
                f"Begriff \n{entity}",
                'raw_input': None
            })

        # explain question
        for a in entity_associations[2:4]:
            entity = a[0]
            association = a[1]
            session_context.add_reasoning_question({
                'id': None,
                'association': association,
                'entity': entity,
                'type': 'why',
                'output': f"Wieso hast du die Assoziation\n\n{association}\n\nmit\n\n{entity}\n\n in Verbindung "
                f"gebracht",
                'raw_input': None
            })

    if current_substate > 0:
        session_context.update_reasoning_question(current_substate - 1, {
            'raw_input': input_context.get('raw_input'),
        })
        output_context.say("Vielen Dank!")

    if current_substate < 4:
        question = session_context.get_reasoning_question(current_substate)
        output_context.inquire(question['output'])

    session_context.advance_state()


def _end(output_context, session_context, _):
    output_context.say("Alles klar, das war's!")
    output_context.say("Vielen Dank und auf Wiedersehen!")
    output_context.close()
