from chatbots.Chatbot import Chatbot

from .HumanPerformer import HumanPerformer
from .BotPerformer import BotPerformer

class Performance:
    dialogue_history: str
    setting_description: str
    max_lines: int = 0

    chatbot: Chatbot

    # List of performers in the performance:
    performers: dict
    # performers = []

    multibot: bool = False #@REVISIT naming; maybe unnecessary

    #performance_type #@TODO i.e. round-robin, random, personality-dependent, etc.
    def __init__(self):
        self.dialogue_history = ""
        self.setting_description = ""
        self.performers = {
            "human": [],
            "bot": []
        }

    # Add a performer to the performance:
    def add_performer(self, performer):
        # Check if performer is HumanPerformer:
        if isinstance(performer, HumanPerformer):
            self.performers["human"].append(performer)
        # Check if performer is BotPerformer:
        elif isinstance(performer, BotPerformer):
            self.performers["bot"].append(performer)
        else:
            raise Exception("Invalid performer type.")

    # Add a setting description to the performance:
    def add_setting(self, setting_description):
        #@TODO improve architecture:
        self.setting_description = setting_description

    def add_dialog(self, performer, dialogue):
        # Add new dialogue to script:
        self.dialogue_history += performer.character_name + ": " + dialogue + "\n"

        # Send new dialogue history to chatbot:

        # If PerformerBot has own chatbot value

    # Generate new dialogue for characters from dialogue history:
    def generate_dialogue(self):
        # If single chatbot generates dialogue for all characters:
        if(not multibot):
            # Prepare chatbot prompt:
            prompt_string = prepare_singlebot_prompt()

            # Send request to chatbot:
            response = chatbot.send_request(prompt_string)

        # If multiple chatbots generate dialogue for individual characters:
        else:
            #@TODO
            raise Exception("Multibot performance not yet implemented.")

            # Feed dialogue history to each BotPerformer's chatbot:
            for performer in self.performers:
                performer.chatbot.generate_dialogue()

    # Prepare context for single-bot performance:
    def prepare_singlebot_prompt(self):
        # Prepare context:
        prompt_string = ""

        # Append  description to context:
        prompt_string += "Please generate dialogue for the following characters:\n"

        for bot_performer in self.performers["bot"]:
            prompt_string += bot_performer.get_description() + "\n"
        prompt_string += "\n"

        prompt_string += "The following are characters played by humans; "
        prompt_string += "please do not generate dialogue for these characters:\n"
        for human_performer in self.performers["human"]:
            prompt_string += human_performer.get_description() + "\n"

        prompt_string += "\n"

        # Append setting description to context:
        prompt_string += "The setting of the scene is as follows:\n"
        prompt_string += self.setting_description + "\n"
        prompt_string += "\n"

        # Append dialogue history to context:
        if(self.dialogue_history != ""):
            prompt_string += "The following dialogue has already been spoken:\n"
            prompt_string += self.dialogue_history
            prompt_string += "\n"

        prompt_string += "Each line of dialogue should take the following form:\n"
        prompt_string += "CHARACTER NAME: Dialogue\n"

        prompt_string += "\n"

        # Set max_lines to number of bot chars (one each) if max_lines is not set:
        max_lines = self.max_lines if self.max_lines else len(self.performers["bot"])

        # Generate {max_lines} lines of dialogue:
        prompt_string += f"Please generate no more than {max_lines} lines dialogue.\n"
        #@REVISIT maybe 'generate no more than x lines of dialogue per char'

        return prompt_string

