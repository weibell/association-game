from tinydb import TinyDB, Query

_sessions_db = TinyDB("data/game_state/sessions.json", sort_keys=True, indent=4)
_quiz_questions_db = TinyDB("data/game_state/quiz_questions.json", sort_keys=True, indent=4)
_assoc_questions_db = TinyDB("data/game_state/assoc_questions.json", sort_keys=True, indent=4)
_reasoning_questions_db = TinyDB("data/game_state/reasoning_questions.json", sort_keys=True, indent=4)
_log_db = TinyDB("data/game_state/log.json", sort_keys=True, indent=4)


def session_data(only_valid=True):
    """Returns all (valid) session data."""
    if only_valid:
        sessions = []
        for session in _sessions_db.all():
            if len(session['reasoning_questions']) != 4:
                continue
            for id in session['reasoning_questions']:
                reasoning_question = _reasoning_questions_db.search(Query().id == id)[0]
                if reasoning_question['raw_input'] is None:
                    break
            else:
                # inner loop did not break
                sessions.append(session)

        return sessions
    else:
        return _sessions_db.all()


def session_ids(only_valid=True):
    """Returns all (valid) session IDs."""
    return [session['id'] for session in session_data(only_valid=only_valid)]


def quiz_question_ids(only_valid=True):
    """Returns all (valid) quiz question IDs."""
    question_ids = []
    for session in session_data(only_valid=only_valid):
        question_ids += [question_id for question_id in session['quiz_questions']]
    return question_ids


def quiz_question_data(only_valid=True):
    """Returns all (valid) quiz question data."""
    questions = []
    for question_id in quiz_question_ids(only_valid=only_valid):
        questions += _quiz_questions_db.search(Query().id == question_id)
    return questions


def assoc_question_ids(only_valid=True):
    """Returns all (valid) association question IDs."""
    question_ids = []
    for session in session_data(only_valid=only_valid):
        question_ids += [question_id for question_id in session['assoc_questions']]
    return question_ids


def assoc_question_data(only_valid=True):
    """Returns all (valid) assoc question data."""
    questions = []
    for question_id in assoc_question_ids(only_valid=only_valid):
        questions += _assoc_questions_db.search(Query().id == question_id)
    return questions


def reasoning_question_ids(only_valid=True):
    """Returns all (valid) reasoning question IDs."""
    question_ids = []
    for session in session_data(only_valid=only_valid):
        question_ids += [question_id for question_id in session['reasoning_questions']]
    return question_ids


def reasoning_question_data(only_valid=True):
    """Returns all (valid) reasoning question data."""
    questions = []
    for question_id in reasoning_question_ids(only_valid=only_valid):
        questions += _reasoning_questions_db.search(Query().id == question_id)
    return questions
