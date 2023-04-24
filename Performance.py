import os
import datetime
import random
from typing import Optional

from .Performer import Performer
from .HumanPerformer import HumanPerformer
from .BotPerformer import BotPerformer
from .DialogueLine import DialogueLine

from chatbots import Chatbot
from coqui.CoquiImp import CoquiImp

class Performance:
    # Script / dialogue history
    working_script: list = []

    # Setting / scene description
    setting_description: str

    # Maximum number of lines to generate during generate_dialogue()
    max_lines: int = 0

    # Where to save the script
    logdir: str = ""

    # Chatbot to use for generating dialogue
    chatbot: Chatbot

    # Chatbot states #@TODO improve naming
    chatbot_states: dict = {}

    # Whether the chatbot has been prompted yet #@REVISIT
    # context_initialized: bool = False

    # TTS engine
    tts: Optional[CoquiImp] = None

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
        self.working_script = []
        self.setting_description = ""
        self.performers = {}
        self.logdir = logdir
        # self.tts = CoquiImp("tts_models/multilingual/multi-dataset/your_tts")
        # self.multibot = multibot
        self.context_initialized = False
        # self.next_performer = None

        if(resume_from_log):
            # Load current-dialogue-history.txt into working_script if it exists:
            if(os.path.isfile(self.logdir + "current-dialogue-history.txt")):
                with open(self.logdir + "current-dialogue-history.txt", "r") as f:
                    dialogue_file_str = f.read()

                    # Split on newlines
                    file_lines = dialogue_file_str.splitlines()

                    # Create DialogueLine objects from each line
                    for file_line in file_lines:
                        try:
                            dialogue_line = DialogueLine.from_str(file_line)
                            self.working_script.append(dialogue_line)
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
                file_creation_time = datetime.datetime.fromtimestamp(
                    os.path.getctime(self.logdir + "current-dialogue-history.txt")
                ).strftime("%Y-%m-%d_%H-%M-%S")

                os.rename(self.logdir + "current-dialogue-history.txt",
                          f"{self.logdir}dialogue-history_{file_creation_time}.txt")


    def set_chatbot(self, chatbot):
        self.chatbot = chatbot

    def add_performer(self, performer: Performer):
        """
        Add a performer to the performance.
        """

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

    def set_scene(self, scene_header: str):
        """
        Set the scene for the performance.
        """

        self.working_script.append("\n\n" + scene_header + "\n")
        # self.setting_description = setting_description
        return True

    def add_description(self, description: str):
        """
        Add a scene or character action description to the working script.
        """

        self.working_script.append(description + "\n")
        return True

    # Add one or multiple instances of dialogue to the dialogue history
    def add_dialogue(self, dialogue):
        # If dialogue is a DialogueLine
        if isinstance(dialogue, DialogueLine):
            # Add the DialogueLine to the dialogue history
            self.working_script.append(dialogue)
        # If dialogue is a list of DialogueLine
        elif isinstance(dialogue, list):
            # Add each DialogueLine to the dialogue history
            for line in dialogue:
                self.working_script.append(line)
        elif isinstance(dialogue, str):
            # Try to parse the string as a DialogueLine
            try:
                dialogue = DialogueLine.from_str(dialogue)

                # Add the DialogueLine to the dialogue history
                self.working_script.append(dialogue)

            except ValueError as e:
                print("ERROR: invalid dialogue line: ", dialogue)
                print(e)
                return
        else:
            print("ERROR: Invalid dialogue type:", type(dialogue))

        # If logdir is set, write to file
        if(self.logdir):
            # Remove empty lines and strip surrounding whitespace from response
            # response = response.replace("\n\n", "\n").strip()

            # Write dialogue line to file
            with open(self.logdir + "current-dialogue-history.txt", "a") as f:
                if isinstance(dialogue, DialogueLine):
                    f.write(str(dialogue) + "\n")
                elif isinstance(dialogue, list):
                    for line in dialogue:
                        f.write(str(line) + "\n")

    def start_interactive(self):
        """
        Start an interactive performance with human performers.
        """

        user_input = ""
        while user_input != "q":
            # Generate dialogue for characters
            self.generate_dialogue(1)
            # user_input = input()

            # Allow user to add dialogue
            user_input = input("Enter dialogue:\n")
            self.add_dialogue(user_input)

    def generate_dialogue(self, max_lines = 0):
        """
        Generate new dialogue for characters and add it to the working script.
        """

        lines = [] #@REVISIT architecture

        # If the next performer is already known
        # if(self.next_performer):
        #     # Generate dialogue for that performer
        #     lines = self.next_performer.generate_dialogue(max_lines)
        #     max_lines -= len(lines)
        # else:
        #@TODO optionally intelligently decide the next character, maybe
        # with aid of chatbot

        assert len(self.bot_performers) > 0, "No bot performers to generate dialogue for."

        # Make a copy of bot_performers
        bot_performers = self.bot_performers.copy() #@REVISIT performance?

        #@TODO combine requests when possible (i.e. loop through characters
        # and determine who shares chatbots, send minimal chatbot queries)
        for line_index in range(max_lines): #@REVISIT architecture
            # If bot_performers is empty, start a new copy
            if not bot_performers:
                bot_performers = self.bot_performers.copy()

            # For now, just pick a random bot performer
            bot_performer = random.choice(bot_performers)
            bot_performers.remove(bot_performer)

            # Generate dialogue for that performer
            if __debug__:
                print("Generating dialogue for", bot_performer.character_name)

            lines = self.generate_performer_lines(bot_performer, 1)

            # Add dialogue lines to dialogue history
            self.add_dialogue(lines)

        return lines

    def generate_performer_lines(self, performer, max_lines = 0):
        """
        Generate dialogue for a performer.

        This method will generate dialogue for a performer, using the
        performance's chatbot if the performer does not have its own chatbot.

        Parameters
        ----------
        performer : Performer
            The performer to generate dialogue for.

        max_lines : int
            The maximum number of lines to generate. If 0, generate as many
            lines as possible.

        Returns
        -------
        lines : list of DialogueLine
            The generated dialogue lines.
        """

        chatbot = performer.chatbot if performer.chatbot else self.chatbot

        if not chatbot:
            raise Exception("No chatbot for performer or performance; " +
                    performer.character_name)

        # Prepare prompt
        prompt = self.prepare_chatbot_prompt(chatbot=chatbot,
                                             max_lines=max_lines)

        #@SCAFFOLDING
        # stop_sequences = []
        stop_regex = None
        if max_lines == 1:
            stop_regex = r"[\S]+\n"
            # stop_sequences = ["\n"]

        response = chatbot.send_message(message=prompt,
                                        stop_regex=stop_regex)
        #@TODO when possible, stream tokens and do advanced processing
        # response = self.chatbot.request_tokens()

        # Log the response
        # self.log(response)

        # Parse response into dialogue lines
        lines = self.parse_chatbot_response(response)

        return lines

    def prepare_chatbot_prompt(self, chatbot = None, max_lines = 0):
        """
        Prepare a prompt for the chatbot to generate dialogue.
        """

        #@TODO adjust prompt based on chatbot

        chatbot = chatbot if chatbot else self.chatbot
        prompt = ""

        # If chatbot has no entry in chatbot_states yet
        if chatbot.name not in self.chatbot_states:
            # Add chatbot to chatbot_states
            #@TODO two chatbots of same name with different settings?
            self.chatbot_states[chatbot.name] = len(self.working_script)

            if __debug__:
                print("Initializing chatbot context for", chatbot.name, "...")

            # Initialize chatbot context
            prompt = self.prepare_chatbot_context(chatbot = chatbot,
                                                  max_lines = max_lines)

        # If chatbot context has been initialized
        else:
            # Determine how far behind chatbot context is
            #@REVISIT optimization
            chatbot_state = self.chatbot_states[chatbot.name]
            context_behind = len(self.working_script) - chatbot_state

            if __debug__:
                print("Chatbot context is", context_behind, "lines behind.")

            # If chatbot context is behind
            if context_behind > 0:
                if __debug__:
                    print("Adding", context_behind, "lines to chatbot prompt...")

                # Add lines to prompt
                for line in self.working_script[chatbot_state:]:
                    prompt += str(line) + "\n"

                # Update chatbot state
                self.chatbot_states[chatbot.name] = len(self.working_script)

        return prompt
        
    def prepare_chatbot_context(self, chatbot, max_lines = 0):
        # Retrieve chatbot-specific prompt base
        prompt_string = self.retrieve_chatbot_prompt_base(chatbot)

        # Setup search and replace dictionary
        bot_characters = ""
        human_characters = ""
        working_script_string = ""
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

        # Convert working_script to string
        for line in self.working_script:
            working_script_string += str(line) + "\n" #@REVISIT readable?

        # If max_lines is set, add it to extra_directions
        if(max_lines):
            extra_directions += "Please generate no more than " + str(max_lines) + " lines of dialogue."

        # Prepare placeholders
        replacements = {
            "{{bot_characters}}": bot_characters,
            "{{human_characters}}": human_characters,
            "{{setting_description}}": self.setting_description,
            "{{working_script}}": working_script_string,
            "{{extra_directions}}": extra_directions
        }

        # Replace placeholders
        for placeholder in replacements:
            replacement = replacements[placeholder]
            prompt_string = prompt_string.replace(placeholder, replacement)

        return prompt_string


    def retrieve_chatbot_prompt_base(self, chatbot):
        """
        Load a prompt base for a chatbot from a file.
        """

        prompt_string = ""

        match chatbot.name.lower():
            case "gpt4all":
                #@REVISIT relies on file structure
                prompt_string = open("botimprov/prompts/gpt4all.txt", "r").read()
            case "rwkv":
                prompt_string = open("botimprov/prompts/rwkv-raven.txt", "r").read()
            case "gpt2":
                prompt_string = open("botimprov/prompts/pygmalion.txt", "r").read()
                # prompt_string = open("botimprov/prompts/gpt2.txt", "r").read()
            # case "openai":
            #     prompt_string = open("botimprov/prompts/chatgpt.txt", "r").read()
            # case "llamacpp":
            #     prompt_string = open("botimprov/prompts/llamacpp.txt", "r").read()
            case _:
                # prompt_string = open("botimprov/prompts/chatgpt.txt", "r").read()
                # prompt_string = open("botimprov/prompts/minimal.txt", "r").read()
                prompt_string = open("botimprov/prompts/minimal-predict.txt", "r").read()

        return prompt_string

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

    def perform(self):
        """
        Run the performance.

        This method will perform each line in the dialogue history.
        """

        # For each line in the dialogue history
        for line in self.working_script:
            # Check if performer exists in performance
            if line.character_name not in self.performers:
                raise Exception("Performer",
                                line.character_name,
                                "not found in performance.")

            # Get the performer for the line
            performer = self.performers[line.character_name]

            print("=====================================")
            print("Performing line for", line.character_name, ":", line.dialogue)

            # If the performer is a BotPerformer
            if isinstance(performer, BotPerformer):
                # Perform the line
                # performer.perform(line.dialogue)

                if(self.tts):
                    self.tts.say(line.dialogue, speaker=performer.speaker)

            # # If the performer is a HumanPerformer
            # elif isinstance(performer, HumanPerformer):
            #     pass

    def log(self, message):
        print(message)

        # If logdir is set, write message to file
        if(self.logdir):
            open(self.logdir + "log.txt", "a").write(message + "\n")
