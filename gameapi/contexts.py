from datetime import datetime

from flask import jsonify

import spacy
import de_core_news_sm

import gameapi.db as db

nlp = spacy.load('de_core_news_sm')


class InputContext:
    """Context containing information about user input."""

    def __init__(self, request):
        """Initialize a new InputContext by parsing the JSON data received from our Dialogflow webhook."""
        self.data = request.get_json(force=True)

    def get(self, attr):
        """Return the requested InputContext attribute or None if not available"""
        return self.data[attr] if attr in self.data else None

    def check_option_debug(self):
        """Return the debug mode (alpha or beta)."""
        return self.get('parameters')['DebugMode'].lower()

    def selected_option(self, question):
        """Given a Question object, determine which option (position as int) the user selected, or None."""

        def normalized(string):
            import unicodedata
            norm = str(unicodedata.normalize('NFKD', str(string)).encode('ascii', 'ignore'))
            return norm.replace("-", " ")

        def is_match(option, input):
            for alias in option:
                if normalized(input).lower() == normalized(alias).lower():
                    return True
            return False

        def extract_option_index(char):
            """Convert the given letter or digit to an option, or return None if invalid."""
            letters = ['A', 'B', 'C', 'D']
            option_index = -1
            if char.isdigit():
                option_index = int(char) - 1
            elif char.upper() in letters:
                option_index = letters.index(char.upper())
            return option_index if 0 <= option_index < num_options else None

        options = question['wrong_options'].copy()
        options.insert(question['answer_index'], question['answer'])
        num_options = len(options)

        # check entities
        parameters = self.get('parameters')
        if 'Answer' in parameters and parameters['Answer'] != '':
            answer = parameters['Answer']

            # "Antwort A", "Antwort 1"
            if 'Option' in answer:
                option = extract_option_index(answer['Option'])
                if option is not None:
                    return option

            # "Merkel", "CDU"
            for entity, value in answer.items():
                if entity == 'Option':
                    continue
                for index, option in enumerate(options):
                    if is_match(option, value):
                        return index

        # check raw input
        raw_input = self.get('raw_input')
        for word in raw_input.split(' '):
            # "Antwort A", "Antwort 1"
            if len(word) == 1:
                option = extract_option_index(word)
                if option is not None:
                    return option

            # "Merkel", "CDU"
            for index, option in enumerate(options):
                if is_match(option, word):
                    return index

        # check pairs of two consecutive
        words = raw_input.split(' ')
        for a, b in zip(raw_input, raw_input[1:]):
            for index, option in enumerate(options):
                if is_match(option, f"{a} {b}"):
                    return index

        # try whole input
        for index, option in enumerate(options):
            if is_match(option, raw_input):
                return index

        # no match found
        return None

    def parse_assocs(self):
        raw_input = self.get('raw_input')
        doc = nlp(raw_input)
        assocs = []
        for token in doc:
            if token.text.lower() == 'president':  # workaround
                assocs.append("Präsident")
            elif token.pos_ in ['NOUN', 'PROPN']:
                assocs.append(token.text)
        return assocs

    def __str__(self):
        return (f"[InputContext  session_id: ...{self.get('session_id')[-4:]}  action: {self.get('action')}  "
                f"intent: {self.get('intent')}  parameters: {self.get('parameters')}  "
                f"raw_input: {self.get('raw_input')}]")


class SessionContext:
    """Context for current session information such as game state or questions asked."""

    def __init__(self, session_id):
        """Initialize a new SessionContext with a given session ID."""
        self.is_advancing = False

        self.session = db.get_session(session_id)
        if self.session is None:
            self.session = db.start_session(session_id)

    def get(self, attr):
        """Return the requested SessionContext attribute."""
        return self.session[attr]

    def set(self, attr, value):
        """Update the given attribute to the desired value."""
        db.update_session(self.get('id'), {attr: value})
        self.session[attr] = value

    def advance_state(self):
        """Advance to the next (sub-)state."""
        self.is_advancing = True

    def add_quiz_question(self, question):
        """Add the QuizQuestion object to the session."""
        question_id = db.add_quiz_question(self.get('id'), question)
        self.set('quiz_questions', self.get('quiz_questions') + [question_id])

    def get_latest_quiz_question(self):
        """Return the QuizQuestion object of the latest question asked."""
        question_id = self.get('quiz_questions')[-1]
        return db.get_quiz_question(question_id)

    def update_latest_quiz_question(self, data):
        """Update the latest quiz question data."""
        question_id = self.get('quiz_questions')[-1]
        db.update_quiz_question(question_id, data)

    def add_assoc_question(self, question):
        """Add the AssocQuestion object to the session."""
        question_id = db.add_assoc_question(self.get('id'), question)
        self.set('assoc_questions', self.get('assoc_questions') + [question_id])

    def add_reasoning_question(self, question):
        """Add the ReasoningQuestion object to the session."""
        question_id = db.add_reasoning_question(self.get('id'), question)
        self.set('reasoning_questions', self.get('reasoning_questions') + [question_id])

    def get_latest_assoc_question(self):
        """Return the AssocQuestion object of the latest question asked."""
        question_id = self.get('assoc_questions')[-1]
        return db.get_assoc_question(question_id)

    def get_reasoning_question(self, number):
        """Return the n-th ReasoningQuestion object."""
        question_id = self.get('reasoning_questions')[number]
        return db.get_reasoning_question(question_id)

    def update_assoc_question(self, index, data):
        """Update the n-th assocation question data."""
        question_id = self.get('assoc_questions')[index]
        db.update_assoc_question(question_id, data)

    def update_reasoning_question(self, index, data):
        """Update the n-th reasoning question data."""
        question_id = self.get('reasoning_questions')[index]
        db.update_reasoning_question(question_id, data)

    def update_latest_assoc_question(self, data):
        """Update the latest association question data."""
        question_id = self.get('assoc_questions')[-1]
        db.update_assoc_question(question_id, data)

    def count_correct_quiz_answers(self, type):
        """Count the number of correct answers for a given type."""
        quiz_questions = self.get('quiz_questions')
        score = 0
        for question_id in quiz_questions:
            question = db.get_quiz_question(question_id)
            if question['type'] == type and question['answered_correctly']:
                score += 1
        return score

    def stronger_topic(self):
        if self.count_correct_quiz_answers('geography') > self.count_correct_quiz_answers('politics'):
            return 'geography'
        else:
            return 'politics'

    def total_num_assocs(self):
        """Return the total number of associations given by the user"""
        assoc_questions = self.get('assoc_questions')
        num = 0
        for question_id in assoc_questions:
            question = db.get_assoc_question(question_id)
            num += len(question['parsed_assocs'])

    def get_associations(self):
        assoc_questions = self.get('assoc_questions')
        assocs = []
        for question_id in assoc_questions:
            question = db.get_assoc_question(question_id)
            assocs.append([question['entity'], question['parsed_assocs']])
        return assocs

    def restart_session(self):
        """Restart the session by renaming the previous one and all question IDs associated with it."""
        prefix = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        for question_id in self.get('quiz_questions'):
            db.update_quiz_question(question_id, {'id': f"RENAMED_{prefix}_{question_id}"})
        for question_id in self.get('assoc_questions'):
            db.update_assoc_question(question_id, {'id': f"RENAMED_{prefix}_{question_id}"})
        db.update_session(self.get('id'), {
            'id': f"RENAMED_{prefix}_{self.get('id')}",
            'quiz_questions': [f"RENAMED_{prefix}_{qid}" for qid in self.get('quiz_questions')],
            'assoc_questions': [f"RENAMED_{prefix}_{aid}" for aid in self.get('assoc_questions')]
        })
        self.session = db.start_session(self.get('id'))

    def __str__(self):
        return (f"[SessionContext  session_id: ...{self.get('id')[-4:]}  timestamp: {self.get('timestamp')}  "
                f"state: {self.get('state')}  substate: {self.get('substate')}]")


class OutputContext:
    """Context relating to what is present to the user as output after return from the webhook."""

    def __init__(self):
        """Initialize a new OutputContext."""
        self.messages = []
        self.is_closed = False
        self.is_inquiry = False

    def say(self, message):
        """Add the response to the output buffer, with optional SSML support."""
        self.messages.append(message)

    def close(self):
        """Leave the conversation after responding to the user."""
        self.is_closed = True

    def inquire(self, message=None):
        """Wait for the user to reply."""
        self.is_inquiry = True
        if message is not None:
            self.say(message)

    def jsonify(self):
        """Convert the buffered messages to a single payload to be returned to Dialogflow."""
        return jsonify({
            'output': "\n\n".join(self.messages),
            'end_conversation': self.is_closed
        })

    def __str__(self):
        return f"[OutputContext  is_inquiry: {self.is_inquiry}  is_closed: {self.is_closed}  messages: {self.messages}]"
