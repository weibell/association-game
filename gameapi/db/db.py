import os
from datetime import datetime
from tinydb import TinyDB, Query

if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists("data/game_state"):
    os.makedirs("data/game_state")

_sessions_db = TinyDB("data/game_state/sessions.json", sort_keys=True, indent=4)
_quiz_questions_db = TinyDB("data/game_state/quiz_questions.json", sort_keys=True, indent=4)
_assoc_questions_db = TinyDB("data/game_state/assoc_questions.json", sort_keys=True, indent=4)
_reasoning_questions_db = TinyDB("data/game_state/reasoning_questions.json", sort_keys=True, indent=4)
_log_db = TinyDB("data/game_state/log.json", sort_keys=True, indent=4)


def log(input_context, session_context):
    _log_db.insert({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'session_id': input_context.get('session_id'),
        'raw_text': input_context.get('raw_input'),
        'action': input_context.get('action'),
        'intent': input_context.get('intent'),
        'state': session_context.get('state'),
        'substate': session_context.get('substate')
    })


"""
A Session object contains the following information:
- id (str): the session ID provided by Dialogflow
- timestamp (str): the time when the session was first initialized
- state (str): the current game state
- substate (int): substate counter, randing from 0 (= uninitialized) to the number of substates 
- quiz_questions (list): a list of question IDs corresponding to QuizQuestion objects that have been asked
- assoc_questions (list): a list of question IDs corresponding to AssocQuestion objects that have been asked
- reasoning_questions (list): a list of question IDs corresponding to ReasoningQuestion objects that have been asked
"""


def start_session(session_id):
    """Start a new session by creating, storing and returning a new Session object."""
    session = {
        'id': session_id,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'state': 'UNINITIALIZED',
        'substate': 0,
        'quiz_questions': [],
        'assoc_questions': [],
        'reasoning_questions': []
    }
    _sessions_db.insert(session)
    return session


def get_session(session_id):
    """Return a Session object corresponding to the current session ID or None if it hasn't been initialized."""
    rows = _sessions_db.search(Query().id == session_id)
    if not rows:
        return None
    else:
        return rows[0]


def update_session(session_id, data):
    """Update the data in sessions.json"""
    _sessions_db.update(data, Query().id == session_id)


"""
A QuizQuestion object contains the following information:
- id (str): a unique QuizQuestion ID
- output (str): the text output given to the user
- answer (list): a list of the correct answer and its (optional) aliases
- answer_index (int): the position of the correct answer in the list of options (starting with 0)
- wrong_options (list): a list of wrong options, each entry being a list of the option and its (optional) aliases
- type (str): the question type (geography or politics) 
- raw_input (str): the input given by the user to answer this question
- answered_correctly (bool): True if the user the user gave was correct
"""


def add_quiz_question(session_id, question):
    """Add a QuizQuestion object to quiz_questions.json and return a unique question ID."""
    question['id'] = f"{session_id}_quiz_{len(get_session(session_id)['quiz_questions'])}"
    _quiz_questions_db.insert(question)
    return question['id']


def get_quiz_question(question_id):
    """Return a QuizQuestion object corresponding to the given question ID."""
    rows = _quiz_questions_db.search(Query().id == question_id)
    return rows[0]


def update_quiz_question(question_id, data):
    """Update the data in quiz_questions.json."""
    _quiz_questions_db.update(data, Query().id == question_id)


"""
An AssocQuestion object contains the following information:
- id (str): a unique AssocQuestion ID
- entity (str): the entity about which this question is about
- output (str): the text output given to the user
- raw_input (str): the input given by the user to answer this question
- parsed_assocs (list): list of assocations that were gathered
"""


def add_assoc_question(session_id, question):
    """Add a AssocQuestion object to assoc_questions.json and return a unique question ID."""
    question['id'] = f"{session_id}_assoc_{len(get_session(session_id)['assoc_questions'])}"
    _assoc_questions_db.insert(question)
    return question['id']


def get_assoc_question(question_id):
    """Return a AssocQuestion object corresponding to the given question ID."""
    rows = _assoc_questions_db.search(Query().id == question_id)
    return rows[0]


def update_assoc_question(question_id, data):
    """Update the data in assoc_questions.json."""
    _assoc_questions_db.update(data, Query().id == question_id)


"""
A ReasoningQuestion object contains the following information:
- id (str): a unique ReasoningQuestion ID
- association (str): the assocation describing the entity
- entity (str): the entity the association is about
- type (str): the qustion type ('why' or 'explain')
- output (str): the text output given to the user
- raw_input (str): the input given by the user to answer this question
"""


def add_reasoning_question(session_id, question):
    """Add a ReasoningQuestion object to reasoning_questions.json and return a unique question ID."""
    question['id'] = f"{session_id}_reasoning_{len(get_session(session_id)['reasoning_questions'])}"
    _reasoning_questions_db.insert(question)
    return question['id']


def get_reasoning_question(question_id):
    """Return a ReasoningQuestion object corresponding to the given question ID."""
    rows = _reasoning_questions_db.search(Query().id == question_id)
    return rows[0]


def update_reasoning_question(question_id, data):
    """Update the data in reasoning_questions.json."""
    _reasoning_questions_db.update(data, Query().id == question_id)
