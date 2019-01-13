import random


class QuestionGenerator:
    """Collects all the data required to create a QuizQuestion object."""

    def __init__(self, question=None):
        """Initialize the generator."""
        self.question = question
        self.answer = None
        self.wrong_options = []
        self.type = None

    def ask(self, question):
        """The question to prompt the user with."""
        self.question = question

    def set_type(self, type):
        self.type = type

    def set_answer(self, answer, aliases=None):
        """Set the correct answer (used as one of the options presented to the user). Also accept a list of aliases."""
        if aliases is None:
            aliases = []
        self.answer = [answer] + aliases

    def add_wrong_option(self, option, aliases=None):
        """Add a wrong option including its aliases."""
        if aliases is None:
            aliases = []
        self.wrong_options.append([option] + aliases)

    def create(self, num_options=3, check_sort=None):
        """Create the QuizQuestion object and limit the options to the specified amount."""
        while True:
            # create options
            random.shuffle(self.wrong_options)
            wrong_options = self.wrong_options[:num_options - 1]
            answer_index = random.randint(0, num_options - 1)

            # list options (without aliases)
            all_options_with_aliases = wrong_options.copy()
            all_options_with_aliases.insert(answer_index, self.answer)

            # check_sort() returns True if the answers are sorted correctly
            if check_sort is None or check_sort(all_options_with_aliases):
                break

        all_options = [option[0] for option in all_options_with_aliases]

        options_list = []
        letters = ['A', 'B', 'C', 'D']
        for (i, option) in enumerate(all_options):
            options_list.append(f"Antwort {letters[i]}\n\n{option}")
        separator = "\n\n"  # text-to-speech workaround
        output_options = f"{separator.join(options_list[:-1])}\n\noder {options_list[-1]}"

        # return QuizQuestion object
        return {
            'output': f"{self.question}\n\n{output_options}",
            'answer': self.answer,
            'answer_index': answer_index,
            'wrong_options': wrong_options,
            'type': self.type,
            'id': None,
            'raw_input': None,
            'answered_correctly': None
        }
