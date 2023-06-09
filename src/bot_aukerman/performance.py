import os
import datetime
import appdirs
from typing import Optional, List, NewType

import simpleaudio as sa

from .performer import Performer
from .human_performer import HumanPerformer
from .bot_performer import BotPerformer

from .script_component import ScriptComponent #, SceneHeader, Dialogue, Action
from .scene_header import SceneHeader
from .scene_action import SceneAction
from .dialogue import Dialogue

from .generator import Generator
from .interpreter import Interpreter

from .constants import ScriptFormat, ScriptComponentType
from .logging import warn

from llmber import AutoChatbot

#@TODO Optional[CoquiImp] and Optional[VoskImp] are not working as expected
# when using try/except to import the modules. Bored of trying to debug it.
# try:
from coqui_imp import CoquiImp
# except ImportError:
#     print("WARNING: failed to import coqui; TTS will not be available")
#     CoquiImp = None #@REVISIT architecture

# try:
from vosk_imp import VoskImp
# except ImportError:
#     print("WARNING: failed to import vosk; STT will not be available")
#     VoskImp = None #@REVISIT architecture

class Performance:
    """
    A Performance is a collection of Performers who are performing a script.

    Performers can be humans or bots. Bot dialogue is generated by LLMs and
    optionally performed via TTS. Human dialogue can be interpreted through STT
    via audio input. Dialogue is saved to a script, and can be resumed from a
    script.
    """

    # Script / dialogue history
    working_script: List[ScriptComponent] = []

    # Format of script
    script_format: ScriptFormat = ScriptFormat.FOUNTAIN

    # Number of lines to generate during generate_dialogue()
    num_lines: int = 0

    # Where to save the script
    logdir: str

    # Chatbots to use for generating dialogue
    #@REVISIT consider moving into Generator if we refactor away from classmethod
    chatbots: List[AutoChatbot] = []

    # How many script components each chatbot has in its context
    chatbot_states = []

    # Performance (fallback) chatbot config
    model_config: Optional[dict] = None

    # Index of chatbot in chatbots[] to use for Performance (fallback)
    performance_chatbot_index: int = 0

    # TTS engine
    tts: Optional[CoquiImp] = None

    # STT engine
    stt: Optional[VoskImp] = None

    verbose: bool = False

    # List of performers in the performance
    performers: dict
    bot_performers: list = []
    human_performers: list = []

    # Currently playing audio object
    active_play_obj: Optional[sa.PlayObject] = None

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
        self.performers = {}

        if(not logdir):
            self.logdir = appdirs.user_log_dir("bot-aukerman", "bot-aukerman")
        else:
            self.logdir = logdir

        # Initialize chatbot if model is set
        if model_config:
            # Because we will parse the response and feed it back to chatbot,
            # we want chatbot's unparsed response kept out of context
            model_config["keep_response_in_context"] = False

            # Initialize chatbot, save its index in chatbots[]
            self.performance_chatbot_index = self._init_chatbot(model_config)

        # Save model config in class property #@REVISIT necessary?
        self.model_config = model_config

        # Print logdir
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
        """
        Load dialogue history from a file into working_script.
        """
        if(os.path.isfile(self.logdir + filename)):
            with open(self.logdir + filename, "r") as f:
                dialogue_file_str = f.read()

                # Split on newlines
                file_lines = dialogue_file_str.splitlines()

                script_components = Interpreter.interpret(file_lines)
                self.working_script = script_components

    def initialize_tts(self):
        """
        Initialize TTS engine.
        """

        if(not self.tts and CoquiImp):
            self.tts = CoquiImp("tts_models/multilingual/multi-dataset/your_tts")

    def initialize_stt(self):
        """
        Initialize STT engine.
        """

        if(not self.stt and VoskImp):
            self.stt = VoskImp()

    def _init_chatbot(self, model_config: dict):
        #@TODO move into Generator if we move away from @classmethod
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

        # Attempt to initialize TTS and STT engines
        self.initialize_tts()
        self.initialize_stt()

        if(not self.stt):
            warn("STT engine not initialized; using text input")
            self.start_interactive_text()
        else:
            print("STT engine initialized; using audio input")
            self.start_interactive_audio()

    def start_interactive_text(self):
        """
        Start an interactive performance with human performers using text input.
        """

        if __debug__:
            print("DEBUG: starting interactive performance with text input")

        # Attempt to initialize TTS engines
        self.initialize_tts()

        user_input = ""
        while user_input != "q":
            if __debug__:
                print("DEBUG: running interactive loop")
                print("=" * 50)
                print("=" * 50)

            # Generate dialogue for characters
            dialogue_components = self.generate_dialogue(1)

            # Perform dialogue
            self.perform_components(dialogue_components)

            # Allow user to add dialogue
            user_input = input("")
            if user_input:
                try:
                    self.add_dialogue(user_input)

                except ValueError as e:
                    warn(f"invalid user input dialogue: {user_input}")
                    print(e)

    def start_interactive_audio(self):
        """
        Start an interactive performance with human performers using audio input.
        """

        # Attempt to initialize TTS and STT engines
        self.initialize_tts()
        self.initialize_stt()

        if(not self.stt):
            raise RuntimeError("STT engine not initialized")

        # If no human performers
        if(not self.human_performers):
            raise RuntimeError("No human performers to assign STT to")

        self.stt.run(self.stt_callback)

    def stt_callback(self, text: str):
        """
        Callback function for STT.
        """
        print(f"stt_callback: {text}")

        #@TODO multiple stt instances/engines?
        #@TODO handle multiple performers? voice detection? round-robin?

        # If no human performers
        if(not self.human_performers):
            raise RuntimeError("No human performers to assign STT to")

        # Get the first human performer
        performer = self.human_performers[0]

        if text:
            try:
                # Create dialogue object
                dialogue = Dialogue(performer.character_name, text)
                self.add_dialogue(dialogue)

                # Generate dialogue for bot character(s)
                dialogue_components = self.generate_dialogue(1)

                # Perform dialogue
                self.perform_components(dialogue_components)

            except ValueError as e:
                warn(f"invalid user input dialogue: {text}")
                print(e)

    def add_performer(self, performer: Performer):
        """
        Add a performer to the performance.
        """
        # If the performer is a BotPerformer
        if isinstance(performer, BotPerformer):
            self.add_bot_performer(performer)
        # If the performer is a HumanPerformer
        elif isinstance(performer, HumanPerformer):
            self.add_human_performer(performer)

    def add_bot_performer(self, performer: BotPerformer):
        """
        Add a bot performer to the performance.
        """

        # Add the performer to the list of performers
        self.performers[performer.character_name.upper()] = performer

        # Add the performer to the list of bot performers
        self.bot_performers.append(performer)

        # If BotPerformer has a chatbot model_config
        if performer.model_config:
            # Initialize chatbot
            #@REVISIT best architecture?
            performer.chatbot_index = self._init_chatbot(performer.model_config)

        if not performer.tts and self.tts:
            performer.tts = self.tts
            performer.speaker = self.tts.auto_select_speaker()

    def add_human_performer(self, performer: HumanPerformer):
        """
        Add a human performer to the performance.
        """

        # Add the performer to the list of performers
        self.performers[performer.character_name.upper()] = performer

        # Add the performer to the list of human performers
        self.human_performers.append(performer)

    def set_scene(self, scene_header: str):
        """
        Set the scene for the performance.
        """

        # Add scene header to working script
        # script_component = SceneHeader.from_str(scene_header)
        components = Interpreter.interpret(text = scene_header,
                                           as_type = SceneHeader)

        self.add_component(components[0])

    def add_description(self, description: str):
        """
        Add a scene or character action description to the working script.
        """

        # Add description to working script
        components = Interpreter.interpret(text = description,
                                           as_type = SceneAction)

        self.add_component(components[0])

    # Add one or multiple instances of dialogue to the dialogue history
    def add_dialogue(self, dialogue) -> bool:
        """
        Add dialogue to the working script.
        """

        # If dialogue is a list of lines
        if isinstance(dialogue, list):
            # Add each Dialogue to the dialogue history
            for line in dialogue:
                self.add_dialogue(line)

            return True #@REVISIT kinda ugly architecture
        # If dialogue is a string
        elif isinstance(dialogue, str):
            # Try to convert the string to a Dialogue
            try:
                components = Interpreter.interpret(text = dialogue,
                                                   as_type = Dialogue)
                dialogue = components[0]

            # If the string is not a valid Dialogue
            except ValueError as e:
                print("ERROR: invalid dialogue line: ", dialogue)
                print(e)
                return False

        # If dialogue is a Dialogue
        elif isinstance(dialogue, Dialogue):
            pass

        # If dialogue is not a Dialogue or a string
        else:
            print("ERROR: Invalid dialogue type:", type(dialogue))

        self.add_component(dialogue)

        # Add performer to character_history
        self.character_history.append(dialogue.character_name.upper())

        return True

    def add_component(self, component: ScriptComponent):
        """
        Add a script component to the working script.
        """

        # Add component to working script
        self.working_script.append(component)

        # Write dialogue line to file
        with open(self.logdir + "current-dialogue-history.txt",
                  mode = "a+",
                  encoding = "utf-8") as f:
            f.write(component.to_str())
            f.write(Generator.break_component(self.script_format))

        return True

    def generate_dialogue(self,
                          num_lines = 1,
                          return_as = "list",
                          ) -> List[Dialogue]:
        """
        Generate new dialogue for characters and add it to the working script.
        """

        # Generate dialogue
        dialogue_components = Generator.generate(self, num_lines) #@REVISIT

        # Add dialogue lines to dialogue history
        self.add_dialogue(dialogue_components)

        match return_as:
            case "list":
                return dialogue_components
            case "str" | "string" | "text":
                return self.components_to_str(dialogue_components)

    def components_to_str(self, components: List[ScriptComponentType]) -> str:
        """
        Convert a list of script components to a string.
        """
        return Generator.components_to_str(components, self.script_format)

    def perform(self):
        """
        Run the performance.

        This method will perform each line in the dialogue history.
        """

        # For each line in the dialogue history
        for script_component in self.working_script:
            self.perform_component(script_component)

    def perform_components(self, script_components: List[ScriptComponentType]):
        """
        Perform a list of script components.
        """
        #@REVISIT should we just have one method that takes list or component?

        for script_component in script_components:
            self.perform_component(script_component)

    def perform_component(self, script_component: ScriptComponent):
        """
        Perform a single script component.
        """

        # If line is a scene header
        #@REVISIT should we rather have a ScriptComponent.type attribute?
        if isinstance(script_component, SceneHeader):
            if __debug__:
                print("=====================================")
                print("Performing scene header:", script_component.to_str())
            return

        # If line is scene action
        elif isinstance(script_component, SceneAction):
            if __debug__:
                print("=====================================")
                print("Performing scene action:", script_component.to_str())
            return

        # If line is a dialogue line
        elif isinstance(script_component, Dialogue):
            if __debug__ and self.verbose:
                print("=====================================")
                print("Performing dialogue for",
                      script_component.character_name,
                      ": ",
                      script_component.dialogue)

            # Get performer
            character_name = script_component.character_name
            performer = self.get_performer(character_name)

            # If the performer is a BotPerformer
            if isinstance(performer, BotPerformer):
                # Perform the line
                try:
                    self.perform_dialogue(script_component)
                    # performer.perform(script_component, self.tts)
                except TypeError as e:
                    warn(f"{e}")

                # if(self.tts):
                #     self.tts.say(script_component.dialogue,
                #                  speaker=performer.speaker)
                # else:
                #     print(f"WARNING: No TTS set for bot {performer.speaker}")

    def perform_dialogue(self, dialogue):
        tts = self.tts
        args = {}

        # If dialogue is string
        if isinstance(dialogue, str): #@REVISIT remove; only accept Dialogue?
            args["text"] = dialogue

        elif isinstance(dialogue, Dialogue):
            # Get performer
            performer = self.get_performer(dialogue.character_name)
            args["performer"] = performer

            # Assert performer is a BotPerformer (has tts and speaker attributes)
            assert isinstance(performer, BotPerformer)

            # If performer has a tts
            if performer.tts:
                tts = performer.tts

            # Set speaker #@REVISIT probably will error on single-speaker models
            speaker = performer.speaker

            # Extract speech from dialogue component
            args["text"] = self.extract_speech_from_dialogue(dialogue)

        else:
            raise TypeError(f"Invalid dialogue type: {type(dialogue)}")

        # If a TTS implementation is available
        if tts:
            # Say dialogue
            play_obj = tts.say(**args)

            # Store play_obj for possible interruption
            self.active_play_obj = play_obj
            
            return play_obj

        # If no TTS implementation is available
        else:
            if isinstance(dialogue, Dialogue):
                print(f"WARNING: No TTS for {dialogue.character_name}")
            else:
                print("WARNING: No TTS for dialogue")

    def extract_speech_from_dialogue(self, dialogue: Dialogue):
        # Split dialogue into parentheticals and dialogue
        subcomponents = dialogue.split_parens_and_dialogue()
        
        # Filter out parenthetical subcomponents
        #@TODO allow parentheticals to influence TTS
        spoken_dialogue = ""
        for subcomponent in subcomponents:
            if(subcomponent["type"] == "dialogue"):
                spoken_dialogue += subcomponent["text"]

        #@TODO-4 replace digits with words; replace …; replace & with and,
        #@ replace —; and others not in tts vocab

        return spoken_dialogue

    def get_performer(self, character_name: str) -> Performer:
        # Check if performer exists in performance
        if character_name not in self.performers:
            raise Exception("Performer",
                            character_name,
                            "not found in performance.")

        # Get the performer for the line
        performer = self.performers[character_name]

        return performer

    def log(self, message):
        if __debug__ and self.verbose:
            print(message)

        # If logdir is set, write message to file
        if(self.logdir):
            open(self.logdir + "log.txt",
                 mode = "a",
                 encoding = "utf-8").write(message)
