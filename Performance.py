import os
import datetime
import random

from .Performer import Performer
from .HumanPerformer import HumanPerformer
from .BotPerformer import BotPerformer
from .DialogueLine import DialogueLine

from chatbots import Chatbot
from CoquiImp import CoquiImp

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
                        try:
                            dialogue_line = DialogueLine.from_str(file_line)
                            self.dialogue_history.append(dialogue_line)
                        except ValueError as e:
                            print("WARNING: invalid dialogue line in current-dialogue-history.txt: ", file_line)
                            print(e)
                            continue

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
                # performer.perform(line.dialogue)
                self.tts.say(line.dialogue, speaker=performer.speaker)

            # # If the performer is a HumanPerformer
            # elif isinstance(performer, HumanPerformer):
            #     pass

    def set_chatbot(self, chatbot):
        self.chatbot = chatbot

    # Add a performer to the performance
    def add_performer(self, performer: Performer):
        # Add the performer to the list of performers
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

    # def add_user_dialogue(self, character, user_input):
    #     self.add_dialogue(DialogueLine(character, user_input))

    # Add one or multiple instances of dialogue to the dialogue history
    def add_dialogue(self, dialogue):
        # If dialogue is a DialogueLine
        if isinstance(dialogue, DialogueLine):
            # Add the DialogueLine to the dialogue history
            self.dialogue_history.append(dialogue)
        # If dialogue is a list of DialogueLine
        elif isinstance(dialogue, list):
            # Add each DialogueLine to the dialogue history
            for line in dialogue:
                self.dialogue_history.append(line)
        elif isinstance(dialogue, str):
            # Try to parse the string as a DialogueLine
            try:
                dialogue = DialogueLine.from_str(dialogue)

                # Add the DialogueLine to the dialogue history
                self.dialogue_history.append(dialogue)

            except ValueError as e:
                print("ERROR: invalid dialogue line: ", dialogue)
                print(e)
                return
        else:
            print("ERROR: Invalid dialogue type:", type(dialogue))

        # If logdir is set, write response to file
        if(self.logdir):
            # Remove empty lines and strip surrounding whitespace from response
            # response = response.replace("\n\n", "\n").strip()

            # Write response to file
            open(self.logdir + "current-dialogue-history.txt",
                  "a").write(str(dialogue) + "\n")
                 # "a").write(response)

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

        # Generate dialogue for that performer
        lines = self.generate_performer_lines(bot_performer, max_lines)

        # Add dialogue lines to dialogue history
        for line in lines:
            self.dialogue_history.append(line)

        return lines

    def generate_performer_lines(self, performer, max_lines = 0):
        # Prepare prompt
        prompt = self.prepare_chatbot_prompt(performers=[performer],
                                             max_lines=max_lines)

        # Generate dialogue
        # If performer has internal chatbot, use it to generate dialogue
        # If performer has internal chatbot
        if(performer.chatbot):
            response = performer.chatbot.send_message(prompt)

        # If performer has no internal chatbot, use performance's chatbot
        else:
            # If neither has a chatbot, raise exception
            if(not self.chatbot):
                raise Exception("No chatbot for performer or performance; " +
                                performer.character_name)

            # If performance has a chatbot, use it to generate dialogue
            response = self.chatbot.send_message(prompt)
            # response = self.chatbot.request_tokens()

        # Log the response
        self.log(response)

        # Parse response into dialogue lines
        lines = self.parse_chatbot_response(response)

        # Add dialogue to performance
        self.add_dialogue(lines)

        return lines

    # Parse chatbot response and return dialogue string
    def parse_chatbot_response(self, response):
        dialogue_lines = []

        # For each line in response
        for line in response.split("\n"):
            # If line contains a colon
            if(":" in line):
                try:
                    line_obj = DialogueLine.from_str(line)
                    dialogue_lines.append(line_obj)
                except ValueError as e:
                    print("WARNING: Invalid dialogue line:", line)
                    print(e)
                    continue

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
        # prompt_string = open("botimprov/prompts/minimal.txt", "r").read()
        prompt_string = open("botimprov/prompts/minimal-predict.txt", "r").read()

        bot_characters = ""
        human_characters = ""
        dialogue_history_string = ""
        extra_directions = ""

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
        for line in self.dialogue_history:
            dialogue_history_string += str(line) + "\n" #@REVISIT readable?

        # If max_lines is set, add it to extra_directions
        if(max_lines):
            extra_directions += "Please generate no more than " + str(max_lines) + " lines of dialogue."

        # Prepare placeholders
        replacements = {
            "{{bot_characters}}": bot_characters,
            "{{human_characters}}": human_characters,
            "{{setting_description}}": self.setting_description,
            "{{dialogue_history}}": dialogue_history_string,
            "\n{{extra_directions}}": extra_directions
        }

        # Replace placeholders
        for placeholder in replacements:
            replacement = replacements[placeholder]
            prompt_string = prompt_string.replace(placeholder, replacement)

        return prompt_string

    def log(self, message):
        print(message)

        # If logdir is set, write message to file
        if(self.logdir):
            open(self.logdir + "log.txt", "a").write(message + "\n")
