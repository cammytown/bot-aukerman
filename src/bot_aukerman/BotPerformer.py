from typing import Optional
from .Performer import Performer
from .ScriptComponent import ScriptComponent
from .Dialogue import Dialogue
# from llmber import AutoChatbot

from coqui.CoquiImp import CoquiImp #@REVISIT

class BotPerformer(Performer):
    # chatbot: Optional[AutoChatbot] = None
    chatbot_index: int = 0
    model_config: Optional[dict] = None

    tts: Optional[CoquiImp] = None #@REVISIT
    speaker: Optional[str] = None

    def __init__(
        self,
        character_name,
        character_desc = "No description",
        # chatbot = None,
        model_config = None,
        tts = None,
        speaker = None
    ):
        # Initialize Performer:
        super().__init__(character_name, character_desc)

        # self.chatbot = chatbot
        self.model_config = model_config

        # If tts is set, use it
        if(tts):
            self.set_tts(tts)

        if(speaker):
            self.speaker = speaker

    def set_tts(self, tts: CoquiImp):
        self.tts = tts

        # If speaker not set, use first speaker in TTS
        if(not self.speaker):
            self.speaker = self.tts.auto_select_speaker()

    def perform(self,
                script_component: ScriptComponent,
                fallback_tts: Optional[CoquiImp] = None): #@REVISIT fallback_tts

        # If script_component is not instance of Dialogue
        if not isinstance(script_component, Dialogue):
            raise TypeError(f"cannot perform {type(script_component)}")

        if not self.tts and fallback_tts:
            self.set_tts(fallback_tts)

        if self.tts:
            self.tts.say(script_component.dialogue, speaker=self.speaker)
        else:
            print(f"WARNING: No TTS for {self.character_name}")
