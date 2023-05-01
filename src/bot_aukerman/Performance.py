import os
import datetime
import random
import re
import appdirs
from typing import Optional, List
from enum import Enum
from importlib import resources

from .Performer import Performer
from .HumanPerformer import HumanPerformer
from .BotPerformer import BotPerformer

from .ScriptComponent import ScriptComponent
from .SceneHeader import SceneHeader
from .SceneAction import SceneAction
from .DialogueLine import DialogueLine

from chatbots import AutoChatbot
from coqui.CoquiImp import CoquiImp

ScriptFormat = Enum("ScriptFormat", "MINIMAL, FOUNTAIN")

class Performance:
    # Script / dialogue history
    working_script: List[ScriptComponent] = []

    # Format of script
    script_format: ScriptFormat = ScriptFormat.FOUNTAIN

    # Maximum number of lines to generate during generate_dialogue()
    max_lines: int = 0

    # Where to save the script
    logdir: str

    # Chatbots to use for generating dialogue
    chatbots: List[AutoChatbot] = []

    # How many script components each chatbot has in its context
    chatbot_states = []

    # Performance (fallback) chatbot config
    model_config: Optional[dict] = None

    # Index of chatbot in chatbots[] to use for Performance (fallback)
    performance_chatbot_index: int = 0

    # TTS engine
    tts: Optional[CoquiImp] = None

    # List of performers in the performance
    performers: dict
    bot_performers: list = []
    human_performers: list = []

    # Characters who have spoken
    character_history: list = []

    #performance_type #@TODO i.e. round-robin, random, personality-dependent, etc.

    def __init__(
        self,
        logdir: str = "",
        model_config: Optional[dict] = None, #@REVISIT consider making config class
        resume_from_log: bool = False,
    ):
        self.working_script = []
        # self.scene_header = ""
        self.performers = {}

        self.logdir = logdir
        self.model_config = model_config

        # self.tts = CoquiImp("tts_models/multilingual/multi-dataset/your_tts")
        self.context_initialized = False

        # Initialize chatbot if model is set
        if model_config:
            self.performance_chatbot_index = self._init_chatbot(model_config)

        # If logdir not set, use appdirs
        if(not self.logdir):
            self.logdir = appdirs.user_log_dir("bot-aukerman", "bot-aukerman")

        print(f"Logs directory: {self.logdir}") #@TODO add info about how to change

        # Create logdir if it doesn't exist
        os.makedirs(self.logdir, exist_ok=True)

        # Load current-dialogue-history.txt into working_script if it exists:
        if(resume_from_log):
            self.load_dialogue_history("current-dialogue-history.txt")
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

    def load_dialogue_history(self, filename: str):
        if(os.path.isfile(self.logdir + filename)):
            with open(self.logdir + filename, "r") as f:
                dialogue_file_str = f.read()

                # Split on newlines
                file_lines = dialogue_file_str.splitlines()

                # Create DialogueLine objects from each line
                for file_line in file_lines:
                    try:
                        dialogue_line = DialogueLine.from_str(file_line)
                        self.working_script.append(dialogue_line)
                    except ValueError as e:
                        print("WARNING: invalid dialogue line in file: ", file_line)
                        print(e)
                        continue

    def _init_chatbot(self, model_config: dict):
        """
        Initialize chatbot.
        """

        #@TODO consider reusing chatbots with identical model_config
        # Load chatbot
        chatbot = AutoChatbot(model_config = model_config)

        # Add chatbot to list of chatbots
        self.chatbots.append(chatbot)

        # Initialize chatbot state
        self.chatbot_states.append(0)

        chatbot_index = len(self.chatbots) - 1

        return chatbot_index

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
            user_input = input("")
            self.add_dialogue(user_input)

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

            # If BotPerformer has a chatbot model_config
            if performer.model_config:
                # Initialize chatbot
                #@REVISIT best architecture?
                performer.chatbot_index = self._init_chatbot(performer.model_config)

        # If the performer is a HumanPerformer
        elif isinstance(performer, HumanPerformer):
            # Add the performer to the list of human performers
            self.human_performers.append(performer)

    def set_scene(self, scene_header: str):
        """
        Set the scene for the performance.
        """

        # Add scene header to working script
        script_component = SceneHeader.from_str(scene_header)
        self.working_script.append(script_component)

    def add_description(self, description: str):
        """
        Add a scene or character action description to the working script.
        """

        # Add description to working script
        script_component = SceneAction.from_str(description)
        self.working_script.append(script_component)

    # Add one or multiple instances of dialogue to the dialogue history
    def add_dialogue(self, dialogue) -> bool:
        """
        Add dialogue to the working script.
        """

        # If dialogue is a list of lines
        if isinstance(dialogue, list):
            # Add each DialogueLine to the dialogue history
            for line in dialogue:
                self.add_dialogue(line)

            return True #@REVISIT kinda ugly architecture

        # If dialogue is a DialogueLine
        if isinstance(dialogue, DialogueLine):
            pass
        # If dialogue is a string
        elif isinstance(dialogue, str):
            # Try to convert the string to a DialogueLine
            try:
                dialogue = DialogueLine.from_str(dialogue)

            # If the string is not a valid DialogueLine
            except ValueError as e:
                print("ERROR: invalid dialogue line: ", dialogue)
                print(e)
                return False

        # If dialogue is not a DialogueLine or a string
        else:
            print("ERROR: Invalid dialogue type:", type(dialogue))

        # Add the DialogueLine to the dialogue history
        self.working_script.append(dialogue)

        # Add performer to character_history
        self.character_history.append(dialogue.character_name.upper())

        # If logdir is set, write to file
        if(self.logdir):
            # Remove empty lines and strip surrounding whitespace from response
            # response = response.replace("\n\n", "\n").strip()

            # Write dialogue line to file
            with open(self.logdir + "current-dialogue-history.txt", "a") as f:
                if isinstance(dialogue, DialogueLine):
                    f.write(dialogue.to_str() + self.break_dialogue_line())
                elif isinstance(dialogue, list):
                    for line in dialogue:
                        f.write(line.to_str() + self.break_dialogue_line())

        return True

    def generate_dialogue(self, max_lines = 0):
        """
        Generate new dialogue for characters and add it to the working script.
        """

        lines = [] #@REVISIT architecture

        #@TODO optionally intelligently decide the next character, maybe
        # with aid of chatbot

        assert len(self.bot_performers) > 0, "No bot performers to generate dialogue for."

        #@TODO combine requests when possible (i.e. loop through characters
        # and determine who shares chatbots, send minimal chatbot queries)
        for line_index in range(max_lines): #@REVISIT architecture
            bot_performer = self.pick_next_bot_performer()

            # Generate dialogue for that performer
            if __debug__:
                print("Generating dialogue for", bot_performer.character_name)

            lines = self.generate_performer_lines(bot_performer, 1)

            # Add dialogue lines to dialogue history
            self.add_dialogue(lines)

        return lines

    def pick_next_bot_performer(self):
        """
        Pick the next bot performer to generate dialogue for.
        """

        # Make a copy of bot_performers
        bot_performers = self.bot_performers.copy() #@REVISIT performance?

        # If bot_performers is empty, start a new copy
        if not bot_performers:
            bot_performers = self.bot_performers.copy()

        # Remove the last performer from the list of bot performers if bot
        #@REVISIT architecture
        last_character_name = self.character_history[-1]
        last_performer = self.performers[last_character_name.upper()]
        if last_performer in bot_performers:
            bot_performers.remove(last_performer)

        # Pick a random bot performer
        bot_performer = random.choice(bot_performers)

        return bot_performer

    def get_performer_chatbot(self, performer):
        """
        Get the chatbot for a performer, or the performance's chatbot if the
        performer does not have its own chatbot.
        """

        #@TODO maybe remove this method if this is all it winds up doing
        return self.chatbots[performer.chatbot_index]

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

        # Prepare prompt
        prompt = self.prepare_chatbot_prompt(next_performer=performer,
                                             max_lines=max_lines)

        #@SCAFFOLDING
        stop_sequences = []
        if max_lines == 1:
            stop_sequences.append({
                "type": "regex",
                "value": r"[\S]+\n"
            })


        chatbot = self.get_performer_chatbot(performer)

        if not chatbot:
            raise Exception("No chatbot for performer or performance; " \
                    + performer.character_name)

        # Log the prompt
        self.log("=== Chatbot Prompt: ===\n" + prompt)

        # Send prompt to chatbot
        response = chatbot.send_message(message=prompt,
                                        stop_sequences=stop_sequences)

        # Log the response
        self.log("=== Chatbot Response: ===\n" + response + "=== END ===")

        # Parse response into dialogue lines
        lines = self.parse_chatbot_response(response,
                                            chatbot=chatbot,
                                            next_performer=performer)

        return lines

    def prepare_chatbot_prompt(self,
                               next_performer: Optional[BotPerformer] = None,
                               max_lines = 0):
        """
        Prepare a prompt for the chatbot to generate dialogue; optionally for a
        specific performer.
        """

        # Get performer or performance chatbot
        # chatbot = self.get_performer_chatbot(next_performer)
        if next_performer:
            #@REVISIT Performer.chatbot_index is currently initialized to 0
            # which is fine as long as the Performance's chatbot index is also 0
            # Otherwise, we don't know which chatbot is at 0 index
            chatbot_index = next_performer.chatbot_index
        else:
            chatbot_index = self.performance_chatbot_index
        chatbot = self.chatbots[chatbot_index]

        prompt = ""

        # If chatbot does not keep track of context or hasn't been initialized
        if not chatbot.keeps_context or self.chatbot_states[chatbot_index] == 0:
            # Add chatbot to chatbot_states
            #@TODO two chatbots of same name with different settings?
            self.chatbot_states[chatbot_index] = len(self.working_script)

            if __debug__:
                print("Initializing chatbot context for", chatbot.name, "...")

            # Initialize chatbot context
            prompt = self.prepare_context(chatbot = chatbot,
                                          max_lines = max_lines)

            # If next_performer is set, prepare a dialogue line for it
            #@REVISIT placement
            if(next_performer):
                prompt += next_performer.character_name.upper() + ": "


        # If chatbot context has been initialized
        else:
            # Determine how far behind chatbot context is
            #@REVISIT optimization
            chatbot_state = self.chatbot_states[chatbot_index]
            context_behind = len(self.working_script) - chatbot_state

            if __debug__:
                print("Chatbot context is", context_behind, "lines behind.")

            # If chatbot context is behind
            if context_behind > 0:
                if __debug__:
                    print("Adding", context_behind, "lines to chatbot prompt...")

                # Add missing lines to prompt
                for line in self.working_script[chatbot_state:]:
                    prompt += line.to_str()
                    prompt += self.break_dialogue_line()

                # If next_performer is set, prepare a dialogue line
                if next_performer:
                    prompt += next_performer.character_name.upper()

                    if self.script_format == ScriptFormat.MINIMAL:
                        prompt += ": "
                    elif self.script_format == ScriptFormat.FOUNTAIN:
                        prompt += "\n"
                    else:
                        # print("Unknown script format:", self.script_format)
                        pass

                # Update chatbot state
                self.chatbot_states[chatbot_index] = len(self.working_script)

        return prompt

    #@REVISIT architecture
    def break_dialogue_line(self):
        """
        Return a string to break up dialogue lines in a chatbot prompt.
        """

        if self.script_format == ScriptFormat.MINIMAL:
            return "\n"
        elif self.script_format == ScriptFormat.FOUNTAIN:
            return "\n\n"
        else:
            # print("Unknown script format:", self.script_format)
            return ""

    def prepare_context(self,
                        chatbot,
                        max_lines = 0):

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
            working_script_string += line.to_str()
            working_script_string += self.break_dialogue_line()

        # If max_lines is set, add it to extra_directions
        if(max_lines):
            extra_directions += "\n\nPlease generate no more than " \
                + str(max_lines) + " lines of dialogue."

        # Prepare placeholders
        replacements = {
            "{{bot_characters}}": bot_characters,
            "{{human_characters}}": human_characters,
            # "{{scene_header}}": self.scene_header,
            "{{working_script}}": working_script_string,
            "\n\n{{extra_directions}}": extra_directions
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
                prompt_string = resources.read_text("bot_aukerman.prompts", "gpt4all.txt")
            case "rwkv":
                prompt_string = resources.read_text("bot_aukerman.prompts", "rwkv-raven.txt")
            case "gpt2":
                prompt_string = resources.read_text("bot_aukerman.prompts", "gpt2.txt")
            case _:
                prompt_string = resources.read_text("bot_aukerman.prompts", "minimal-predict.txt")

        return prompt_string

    # Parse chatbot response and return dialogue string
    def parse_chatbot_response(self,
                               response: str,
                               chatbot: AutoChatbot,
                               next_performer: Optional[Performer] = None):

        dialogue_lines = []

        flags = {
            "ignore_first_char_newline": False,
            "discard_multiple_char_names": False
        }

        match chatbot.name.lower():
            case "gpt2":
                flags["ignore_first_char_newline"] = True
                flags["discard_multiple_char_names"] = True

            case _:
                print("WARNING: No flags set for chatbot", chatbot.name)
                pass

        if flags["ignore_first_char_newline"]:
            # If first character of response is a newline, remove it
            #@REVISIT I'm not clear on why gpt3 sometimes desperately wants to 
            #@ start a newline after a character name. I presume it has encountered
            #@ a lot of dialogue with the format CHARACTER\nDIALOGUE (i.e. .fountain)
            #@ We'll want a better solution for this
            #@TODO make this optional at least?
            if(response[0] == "\n"):
                response = response[1:]

        # If next_performer, prepend name to response to match chatbot query
        if next_performer:
            #@REVISIT ugly architecture
            response = next_performer.character_name.upper() + ": " + response

        # For each line in response
        for line in response.split("\n"):
            # If line contains a colon
            if(":" in line):
                try:
                    if flags["discard_multiple_char_names"]:
                        # Extract character headers from line into list
                        header_regex = r"[A-Z ]+:"
                        character_headers = re.findall(header_regex, line)

                        # If there are multiple character headers
                        if(len(character_headers) > 1):
                            # Split line on instances of character headers
                            inner_lines = re.split(header_regex, line)

                            # Remove text before first character header
                            #@DOUBLE-CHECK
                            inner_lines = inner_lines[1:]

                            if __debug__:
                                print("character_headers:", character_headers)
                                print("inner_lines:", inner_lines)

                            # Attempt to validate each inner line
                            for i, inner_line in enumerate(inner_lines):
                                # If inner line is empty, skip
                                if(inner_line == ""):
                                    continue

                                # Prepend character header to inner line
                                #@REVISIT i-1 is always correct, right?
                                inner_line = character_headers[i-1].strip() \
                                        + inner_line

                                # Parse inner line into a DialogueLine object
                                try:
                                    line_obj = DialogueLine.from_str(inner_line)
                                    dialogue_lines.append(line_obj)
                                except ValueError as e: #@REVISIT ugly
                                    continue

                            # Finished parsing line
                            continue

                    # Parse line into a DialogueLine object
                    line_obj = DialogueLine.from_str(line)
                    dialogue_lines.append(line_obj)
                except ValueError as e:
                    print("WARNING: Invalid dialogue line:", line)
                    print(e)
                    continue

            # If line does not contain a colon
            else:
                continue

        return dialogue_lines

    def perform(self):
        """
        Run the performance.

        This method will perform each line in the dialogue history.
        """

        # For each line in the dialogue history
        for script_component in self.working_script:
            # If line is a scene header
            #@REVISIT should we rather have a ScriptComponent.type attribute?
            if isinstance(script_component, SceneHeader):
                if __debug__:
                    print("=====================================")
                    print("Performing scene header:", script_component.to_str())
                continue

            # If line is scene action
            elif isinstance(script_component, SceneAction):
                if __debug__:
                    print("=====================================")
                    print("Performing scene action:", script_component.to_str())
                continue

            # If line is a dialogue line
            elif isinstance(script_component, DialogueLine):
                # Check if performer exists in performance
                if script_component.character_name not in self.performers:
                    raise Exception("Performer",
                                    script_component.character_name,
                                    "not found in performance.")

                # Get the performer for the line
                performer = self.performers[script_component.character_name]

                if __debug__:
                    print("=====================================")
                    print("Performing line for",
                          script_component.character_name,
                          ": ",
                          script_component.dialogue)

                # If the performer is a BotPerformer
                if isinstance(performer, BotPerformer):
                    # Perform the line
                    # performer.perform(line.dialogue)

                    if(self.tts):
                        self.tts.say(script_component.dialogue, speaker=performer.speaker)

    def log(self, message):
        if __debug__:
            print(message)

        # If logdir is set, write message to file
        if(self.logdir):
            open(self.logdir + "log.txt", "a").write(message)
