import os
import datetime

from chatbots.Chatbot import Chatbot

from .HumanPerformer import HumanPerformer
from .BotPerformer import BotPerformer

class Performance:
    dialogue_history: str
    setting_description: str
    max_lines: int = 0
    logdir: str = None

    chatbot: Chatbot

    # List of performers in the performance:
    performers: dict
    # performers = []

    multibot: bool = False #@REVISIT naming; maybe unnecessary

    #performance_type #@TODO i.e. round-robin, random, personality-dependent, etc.
    def __init__(self, logdir = None, multibot = False):
        self.dialogue_history = ""
        self.setting_description = ""
        self.performers = {
            "human": [],
            "bot": []
        }
        self.logdir = logdir

        # If logdir is set and dialogue_history.txt exists, rename it:
        if(self.logdir):
            # Ensure logdir ends with a slash:
            if(self.logdir[-1] != "/"):
                self.logdir += "/"

            if(os.path.isfile(self.logdir + "current-dialogue-history.txt")):
                # Rename file to dialogue-history_[file creation time].txt:
                #@REVISIT i let github copilot do its thing here; clean up:
                file_creation_time = datetime.datetime.fromtimestamp(os.path.getctime(self.logdir + "current-dialogue-history.txt")).strftime("%Y-%m-%d_%H-%M-%S")
                os.rename(self.logdir + "current-dialogue-history.txt", self.logdir + "dialogue-history_" + file_creation_time + ".txt")

    def set_chatbot(self, chatbot):
        self.chatbot = chatbot

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
        if(not self.multibot):
            if(self.dialogue_history == ""): #@REVISIT better check?
                # Prepare chatbot prompt:
                prompt_string = self.prepare_singlebot_prompt()

                print("Prompt:")
                print(prompt_string)

                # Send request to chatbot:
                response = self.chatbot.send_message(prompt_string)
            else:
                response = self.chatbot.request_tokens()

            # Add response to dialogue history:
            self.dialogue_history += response

            if(self.logdir):
                open(self.logdir + "current-dialogue-history.txt", "a").write(response)

        # If multiple chatbots generate dialogue for individual characters:
        else:
            #@TODO
            raise Exception("Multibot performance not yet implemented.")

            # Feed dialogue history to each BotPerformer's chatbot:
            for performer in self.performers:
                performer.chatbot.generate_dialogue()

    # Prepare context for single-bot performance:
    def prepare_singlebot_prompt(self):
        #@TODO adjust prompt based on chatbot

        # Prepare context:
        # Load prompts/gpt4all.txt and replace placeholders:
        #@REVISIT relies on file structure:
        prompt_string = open("botimprov/prompts/gpt4all.txt", "r").read()


        bot_performers = ""
        for bot_performer in self.performers["bot"]:
            bot_performers += bot_performer.get_description()
            # Add newline if not last performer:
            if(bot_performer != self.performers["bot"][-1]):
                bot_performers += "\n"

        human_performers = ""
        for human_performer in self.performers["human"]:
            human_performers += human_performer.get_description()
            # Add newline if not last performer: #@REVISIT redundancy
            if(human_performer != self.performers["human"][-1]):
                human_performers += "\n"

        prompt_string = prompt_string.replace("{{dialogue_history}}", self.dialogue_history)
        prompt_string = prompt_string.replace("{{setting_description}}", self.setting_description)
        prompt_string = prompt_string.replace("{{bot_characters}}", bot_performers)
        prompt_string = prompt_string.replace("{{human_characters}}", human_performers)

        return prompt_string

