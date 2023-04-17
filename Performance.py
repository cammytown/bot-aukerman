import os
import datetime
import random

from .Performer import Performer
from .HumanPerformer import HumanPerformer
from .BotPerformer import BotPerformer

from chatbots import Chatbot
from CoquiImp import CoquiImp

class DialogueLine:
    character_name: str
    dialogue: str
    parenthetical: str

    def __init__(self, character_name, dialogue, parenthetical = ""):
        self.character_name = character_name
        self.dialogue = dialogue
        self.parenthetical = parenthetical

    def __str__(self):
        return self.character_name + ": " + self.dialogue
        # return to_str(self)

    # def __repr__(self):
    #     return to_str(self)

    @staticmethod
    def from_str(dialogue_line_str):
        # Split on colon
        colon_split = dialogue_line_str.split(":", 1)

        # If there is no colon
        if(len(colon_split) == 1):
            #@TODO attempt to parse anyway
            return False
            # raise Exception("DialogueLine.from_str(): colon not found in dialogue_line_str: " + dialogue_line_str)

        parenthetical = ""

        # Check for parenthetical
        if("(" in colon_split[0]):
            character_name = colon_split[0].split("(")[0].strip()
            parenthetical = colon_split[0].split("(")[1].split(")")[0].strip()
        elif("[" in colon_split[0]):
            character_name = colon_split[0].split("[")[0].strip()
            parenthetical = colon_split[0].split("[")[1].split("]")[0].strip()
        # If no parenthetical
        else:
            character_name = colon_split[0]

        # Convert character_name to uppercase
        character_name = character_name.upper()

        dialogue = colon_split[1]

        # Check for parenthetical in dialogue
        #@TODO redundant code
        if("(" in dialogue):
            parenthetical = dialogue.split("(")[1].split(")")[0].strip()
            dialogue = dialogue.split("(")[0].strip()
        elif("[" in dialogue):
            parenthetical = dialogue.split("[")[1].split("]")[0].strip()
            dialogue = dialogue.split("[")[0].strip()

        # Remove whitespace
        character_name = character_name.strip()
        dialogue = dialogue.strip()

        # If dialogue is wrapped in quotes, remove them
        if(dialogue[0] == "\"" and dialogue[-1] == "\""):
            dialogue = dialogue[1:-1]

        # Return DialogueLine object
        return DialogueLine(character_name, dialogue)

class Performance:
    # Script / dialogue history
    dialogue_history: list = []

    # Setting / scene description
    setting_description: str

    # Maximum number of lines to generate during generate_dialogue()
    max_lines: int = 0

    # Where to save the script
    logdir: str

    # Chatbot to use for generating dialogue
    chatbot: Chatbot

    # Whether the chatbot has been prompted yet #@REVISIT
    context_initialized: bool

    # TTS engine
    tts: CoquiImp

    # List of performers in the performance
    performers: dict
    bot_performers: list = []
    human_performers: list = []

    # The next performer intended to deliver a line
    # next_performer: Performer

    #performance_type #@TODO i.e. round-robin, random, personality-dependent, etc.
    def __init__(
        self,
        logdir: str = "",
        resume_from_log = False,
        # multibot = False
    ):
        self.dialogue_history = []
        self.setting_description = ""
        self.performers = {}
        self.logdir = logdir
        self.tts = CoquiImp("tts_models/multilingual/multi-dataset/your_tts")
        # self.multibot = multibot
        self.context_initialized = False
        # self.next_performer = None

        if(resume_from_log):
            # Load current-dialogue-history.txt into dialogue_history if it exists:
            if(os.path.isfile(self.logdir + "current-dialogue-history.txt")):
                with open(self.logdir + "current-dialogue-history.txt", "r") as f:
                    dialogue_file_str = f.read()

                    # Split on newlines
                    file_lines = dialogue_file_str.splitlines()

                    # Create DialogueLine objects from each line
                    for file_line in file_lines:
                        dialogue_line = DialogueLine.from_str(file_line)
                        if(dialogue_line):
                            self.dialogue_history.append(dialogue_line)

        # If logdir is set and current-dialogue-history.txt exists, rename it:
        elif(self.logdir):
            # Ensure logdir ends with a slash
            if(self.logdir[-1] != "/"):
                self.logdir += "/"

            if(os.path.isfile(self.logdir + "current-dialogue-history.txt")):
                # Rename file to dialogue-history_[file creation time].txt:
                #@REVISIT i let github copilot do its thing here; clean up:
                file_creation_time = datetime.datetime.fromtimestamp(os.path.getctime(self.logdir + "current-dialogue-history.txt")).strftime("%Y-%m-%d_%H-%M-%S")
                os.rename(self.logdir + "current-dialogue-history.txt", self.logdir + "dialogue-history_" + file_creation_time + ".txt")

    def perform(self):
        # For each line in the dialogue history
        for line in self.dialogue_history:
            performer = self.performers[line.character_name]

            print("=====================================")
            print("Performing line for", line.character_name, ":", line.dialogue)

            # If the performer is a BotPerformer
            if isinstance(performer, BotPerformer):
                # Perform the line
                performer.perform(line.dialogue)
            # # If the performer is a HumanPerformer
            # elif isinstance(performer, HumanPerformer):
            #     pass

    def set_chatbot(self, chatbot):
        self.chatbot = chatbot

    # Add a performer to the performance
    def add_performer(self, performer: Performer):
        self.performers[performer.character_name.upper()] = performer

        # If the performer is a BotPerformer
        if isinstance(performer, BotPerformer):
            # Add the performer to the list of bot performers
            self.bot_performers.append(performer)
        # If the performer is a HumanPerformer
        elif isinstance(performer, HumanPerformer):
            # Add the performer to the list of human performers
            self.human_performers.append(performer)

    # Add a setting description to the performance
    def add_setting(self, setting_description):
        #@TODO improve architecture
        self.setting_description = setting_description

    # def add_dialog(self, performer, dialogue):

    # Generate new dialogue for characters from dialogue history
    def generate_dialogue(self, max_lines = 0):
        lines = [] #@REVISIT architecture

        # If the next performer is already known
        # if(self.next_performer):
        #     # Generate dialogue for that performer
        #     lines = self.next_performer.generate_dialogue(max_lines)
        #     max_lines -= len(lines)
        # else:
        #@TODO optionally intelligently decide the next character, maybe
        # with aid of chatbot

        # For now, just pick a random bot performer
        bot_performer = random.choice(self.bot_performers)

        # If performer has internal chatbot
        if(bot_performer.chatbot):
            # Generate dialogue for that performer
            lines = bot_performer.generate_dialogue(max_lines)
            max_lines -= len(lines)

        # Add dialogue lines to dialogue history
        for line in lines:
            self.dialogue_history.append(line)

        return lines

    # Parse chatbot response and return dialogue string
    def parse_chatbot_response(self, response):
        dialogue_lines = []

        # For each line in response
        for line in response.split("\n"):
            # If line contains a colon
            if(":" in line):
                line_obj = DialogueLine.from_str(line)
                dialogue_lines.append(line_obj)

            # If line does not contain a colon, skip: #@REVISIT
            else:
                continue

        return dialogue_lines

    # Prepare context for single-bot performance
    def prepare_chatbot_prompt(self, performers = None, max_lines = 0):
        #@TODO adjust prompt based on chatbot

        # Prepare context
        # Load prompts/gpt4all.txt and replace placeholders
        #@REVISIT relies on file structure
        # prompt_string = open("botimprov/prompts/gpt4all.txt", "r").read()
        # prompt_string = open("botimprov/prompts/chatgpt.txt", "r").read()
        prompt_string = open("botimprov/prompts/minimal.txt", "r").read()

        bot_characters = ""
        human_characters = ""

        # Iterate through performers
        for character_name in self.performers:
            performer = self.performers[character_name]

            # If performer is a bot
            if isinstance(performer, BotPerformer):
                # Add newline if not first performer
                if(bot_characters != ""):
                    bot_characters += "\n"

                bot_characters += performer.get_description()

            # If performer is a human
            elif isinstance(performer, HumanPerformer):
                # Add newline if not first performer
                if(human_characters != ""):
                    human_characters += "\n"

                human_characters += performer.get_description()

            else:
                raise Exception("Invalid performer type.")

        # Convert dialogue_history to string
        dialogue_history_string = ""
        for line in self.dialogue_history:
            dialogue_history_string += str(line) + "\n" #@REVISIT readable?
            # dialogue_history_string += line.character_name + ": " + line.dialogue + "\n"

        # Prepare placeholders
        replacements = {
            "{{dialogue_history}}": dialogue_history_string,
            "{{setting_description}}": self.setting_description,
            "{{bot_characters}}": bot_characters,
            "{{human_characters}}": human_characters
        }

        # Replace placeholders
        for placeholder in replacements:
            replacement = replacements[placeholder]
            prompt_string = prompt_string.replace(placeholder, replacement)

        return prompt_string
