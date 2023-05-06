from typing import List, Optional
import random
from importlib import resources

from .ScriptComponent import ScriptComponent
from .Dialogue import Dialogue
# from .Performance import Performance #@TODO type hinting causes circular import
from .Performer import Performer
from .BotPerformer import BotPerformer
from .HumanPerformer import HumanPerformer
from .Interpreter import Interpreter

from .constants import ScriptFormat, ScriptComponentType

from llmber import AutoChatbot

class Generator():
    performance = None #@TODO type hinting causes circular import
    verbose: bool = True

    def __init__(self, performance):
        self.performance = performance

    #@REVISIT really not sure about this architecture; mostly just doing it to
    #@ stay consistent with Interpreter that uses the same concept; but we might
    #@ want to change one or both. maybe it's fine.
    @classmethod
    def generate(cls,
                 performance,
                 max_lines: int = 0) -> List[Dialogue]:
        """
        Generate a script for a performance.

        Parameters
        ----------
        performance : Performance
            The performance to generate a script for.

        Returns
        -------
        script : list of ScriptComponent
            The generated script.
        """

        # Initialize generator
        generator = cls(performance)

        # Generate script
        script_components = generator.generate_dialogue(max_lines=max_lines)

        return script_components

    def generate_dialogue(self,
                          max_lines = 0) -> List[Dialogue]:
        """
        Generate dialogue for a performance.
        """

        dialogue_components = [] #@REVISIT architecture

        #@TODO optionally intelligently decide the next character, maybe
        # with aid of chatbot

        assert len(self.performance.bot_performers) > 0, "No bot performers"

        #@TODO combine requests when possible (i.e. loop through characters
        # and determine who shares chatbots, send minimal chatbot queries)
        for line_index in range(max_lines): #@REVISIT architecture
            bot_performer = self.pick_next_bot_performer()

            # Generate dialogue for that performer
            if __debug__:
                print("Generating dialogue for", bot_performer.character_name)

            dialogue_components = self.generate_performer_lines(bot_performer, 1)


        return dialogue_components

    def pick_next_bot_performer(self) -> BotPerformer:
        """
        Pick the next bot performer to generate dialogue for.
        """

        # Make a copy of bot_performers
        #@REVISIT performance?
        bot_performers = self.performance.bot_performers.copy()

        # If bot_performers is empty, start a new copy
        if not bot_performers:
            bot_performers = self.performance.bot_performers.copy()

        # Remove the last performer from the list of bot performers if bot
        #@REVISIT architecture
        last_character_name = self.performance.character_history[-1]
        if last_character_name not in self.performance.performers:
            #@TODO handle this better; maybe add character to performers?

            if __debug__:
                print("WARNING: last character not in known performers")

            return random.choice(bot_performers)

        last_performer = self.performance.performers[last_character_name.upper()]
        if last_performer in bot_performers:
            bot_performers.remove(last_performer)

        # Pick a random bot performer
        bot_performer = random.choice(bot_performers)

        return bot_performer

    def generate_performer_lines(self,
                                 performer,
                                 max_lines = 0
                                 ) -> List[Dialogue]:
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
        lines : list of Dialogue
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
        self.performance.log("=== Chatbot Prompt: ===\n" + prompt \
                + "=== END ===")

        # Send prompt to chatbot
        response = chatbot.send_message(message=prompt,
                                        n_tokens=28,
                                        stop_sequences=stop_sequences)

        # Log the response
        self.performance.log("=== Chatbot Response: ===\n" + response \
                + "=== END ===\n")

        # Parse response into dialogue lines
        script_components = self.parse_chatbot_response(response,
                                            chatbot=chatbot,
                                            next_performer=performer)

        # Filter for Dialogue components
        dialogue_components = []
        for component in script_components:
            if isinstance(component, Dialogue):
                dialogue_components.append(component)

            # Not a Dialogue component
            else:
                if __debug__:
                    #@REVISIT
                    print("WARNING: non-Dialogue component ignored:", component)

        return dialogue_components

    def get_performer_chatbot(self, performer) -> AutoChatbot:
        """
        Get the chatbot for a performer, or the performance's chatbot if the
        performer does not have one.
        """

        #@TODO maybe remove this method if this is all it winds up doing
        return self.performance.chatbots[performer.chatbot_index]

    def prepare_chatbot_prompt(self,
                               next_performer: Optional[BotPerformer] = None,
                               max_lines = 0) -> str:
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
            chatbot_index = self.performance.performance_chatbot_index

        chatbot = self.performance.chatbots[chatbot_index]

        prompt = ""

        # If chatbot hasn't been initialized or ignores context
        if self.performance.chatbot_states[chatbot_index] == 0 or not chatbot.keep_context:
            # Update chatbot state
            self.performance.chatbot_states[chatbot_index] = len(self.performance.working_script)

            if __debug__:
                print("Initializing chatbot context for", chatbot.name, "...")

            # Prepare chatbot prompt
            prompt = self.prepare_context(chatbot = chatbot,
                                          max_lines = max_lines)

            # If next_performer is set, prepare a dialogue line for it
            if(next_performer):
                prompt += next_performer.character_name.upper()
                prompt += self.break_character_name()

        # If chatbot context has been initialized
        else:
            # Determine how far behind chatbot context is
            #@REVISIT optimization
            chatbot_state = self.performance.chatbot_states[chatbot_index]
            context_behind = len(self.performance.working_script) - chatbot_state

            if __debug__:
                print("Chatbot context is", context_behind, "lines behind.")

            # If chatbot context is behind
            if context_behind > 0:
                if __debug__:
                    print(f"Adding {context_behind} lines to chatbot prompt...")

                # Add missing lines to prompt
                for i, line in enumerate(self.performance.working_script[chatbot_state:]):
                    # If first line, don't add character name

                    prompt += line.to_str()
                    prompt += self.break_component()

                # If next_performer is set, prepare a dialogue line
                if next_performer:
                    prompt += next_performer.character_name.upper()
                    prompt += self.break_character_name()

                self.queued_performer = next_performer

                # Update chatbot state
                self.performance.chatbot_states[chatbot_index] = len(self.performance.working_script)

        return prompt

    #@REVISIT architecture
    def break_character_name(self) -> str:
        """
        Return the string to break between a character name and dialogue.
        """

        if self.performance.script_format == ScriptFormat.MINIMAL:
            return ": "
        elif self.performance.script_format == ScriptFormat.FOUNTAIN:
            return "\n"
        else:
            raise Exception("Unknown script format:", self.performance.script_format)

    #@REVISIT architecture
    def break_component(self) -> str:
        """
        Return the string to break between script components.
        """

        return self.break_component_in_format(self.performance.script_format)

    @staticmethod
    def break_component_in_format(format: ScriptFormat) -> str:
        """
        Return the string to break between script components in a given format.
        """

        if format == ScriptFormat.MINIMAL:
            return "\n"
        elif format == ScriptFormat.FOUNTAIN:
            return "\n\n"
        else:
            raise Exception("Unknown script format:", format)

    def prepare_context(self,
                        chatbot,
                        max_lines = 0) -> str:
        """
        Prepare a prompt to give a chatbot to generate dialogue.
        """

        # Retrieve chatbot-specific prompt base
        prompt_string = self.retrieve_chatbot_prompt_base(chatbot)

        # Setup search and replace dictionary
        bot_characters = ""
        human_characters = ""
        working_script_string = ""
        extra_directions = ""

        # Iterate through performers
        for character_name, performer in self.performance.performers.items():
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
        for line in self.performance.working_script:
            working_script_string += line.to_str()
            working_script_string += self.break_component()

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


    def retrieve_chatbot_prompt_base(self, chatbot) -> str:
        """
        Load a prompt base for a chatbot from a file.
        """

        prompt_string = ""

        match chatbot.name.lower():
            case "gpt4all":
                prompt_string = resources.read_text("bot_aukerman.prompts",
                                                    "gpt4all.txt")
            case "rwkv":
                prompt_string = resources.read_text("bot_aukerman.prompts",
                                                    "rwkv-raven.txt")
            case "gpt2":
                prompt_string = resources.read_text("bot_aukerman.prompts",
                                                    "gpt2.txt")
            case _:
                prompt_string = resources.read_text("bot_aukerman.prompts",
                                                    "minimal-predict.txt")

        return prompt_string

    # Parse chatbot response and return dialogue string
    def parse_chatbot_response(self,
                               response: str,
                               chatbot: AutoChatbot,
                               next_performer: Optional[Performer] = None
                               ) -> List[ScriptComponent]:
        """
        Parse a chatbot response and return a list of script components.
        """

        # Parser flags
        flags = {
            "ignore_first_char_newline": False,
            "discard_multiple_char_names": False
        }

        # Set flags based on chatbot
        match chatbot.name.lower():
            case "gpt2":
                flags["ignore_first_char_newline"] = True
                flags["discard_multiple_char_names"] = True

            case _:
                if __debug__ and self.verbose:
                    print("WARNING: No flags set for chatbot", chatbot.name)

        # If next_performer, prepend name to response to match chatbot query
        if next_performer:
            #@REVISIT ugly architecture
            character_name = next_performer.character_name.upper() \
                    + self.break_character_name()

            response = character_name + response

        script_components = Interpreter.interpret(response, flags)

        return script_components

    # def parse_single_line(self, line: str, flags: dict):
    #     if flags["discard_multiple_char_names"]:
    #         # Extract character headers from line into list
    #         header_regex = r"[A-Z ]+:"
    #         character_headers = re.findall(header_regex, line)

    #         # If there are multiple character headers
    #         if(len(character_headers) > 1):
    #             # Split line on instances of character headers
    #             inner_lines = re.split(header_regex, line)

    #             # Remove text before first character header
    #             #@DOUBLE-CHECK
    #             inner_lines = inner_lines[1:]

    #             if __debug__:
    #                 print("character_headers:", character_headers)
    #                 print("inner_lines:", inner_lines)

    #             # Attempt to validate each inner line
    #             for i, inner_line in enumerate(inner_lines):
    #                 # If inner line is empty, skip
    #                 if(inner_line == ""):
    #                     continue

    #                 # Prepend character header to inner line
    #                 #@REVISIT i-1 is always correct, right?
    #                 inner_line = character_headers[i-1].strip() \
    #                         + inner_line

    #                 # Parse inner line into a Dialogue object
    #                 try:
    #                     line_obj = Dialogue.from_str(inner_line)
    #                     dialogue_lines.append(line_obj)
    #                 except ValueError as e: #@REVISIT ugly
    #                     continue

    #         # Parse line into a Dialogue object
    #         line_obj = Dialogue.from_str(line)
    #         dialogue_lines.append(line_obj)

    #     return dialogue_lines
    # def parse_single_line(self, line: str, flags: dict):
    #     if flags["discard_multiple_char_names"]:
    #         # Extract character headers from line into list
    #         header_regex = r"[A-Z ]+:"
    #         character_headers = re.findall(header_regex, line)

    #         # If there are multiple character headers
    #         if(len(character_headers) > 1):
    #             # Split line on instances of character headers
    #             inner_lines = re.split(header_regex, line)

    #             # Remove text before first character header
    #             #@DOUBLE-CHECK
    #             inner_lines = inner_lines[1:]

    #             if __debug__:
    #                 print("character_headers:", character_headers)
    #                 print("inner_lines:", inner_lines)

    #             # Attempt to validate each inner line
    #             for i, inner_line in enumerate(inner_lines):
    #                 # If inner line is empty, skip
    #                 if(inner_line == ""):
    #                     continue

    #                 # Prepend character header to inner line
    #                 #@REVISIT i-1 is always correct, right?
    #                 inner_line = character_headers[i-1].strip() \
    #                         + inner_line

    #                 # Parse inner line into a Dialogue object
    #                 try:
    #                     line_obj = Dialogue.from_str(inner_line)
    #                     dialogue_lines.append(line_obj)
    #                 except ValueError as e: #@REVISIT ugly
    #                     continue

    #         # Parse line into a Dialogue object
    #         line_obj = Dialogue.from_str(line)
    #         dialogue_lines.append(line_obj)

    #     return dialogue_lines
