from typing import Optional
from .performer import Performer
from .script_component import ScriptComponent
from .dialogue import Dialogue
# from llmber import AutoChatbot

from coqui_imp import CoquiImp #@REVISIT

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

    # def perform(self,
    #             script_component: ScriptComponent,
    #             fallback_tts: Optional[CoquiImp] = None): #@REVISIT fallback_tts

    #     # If script_component is not instance of Dialogue
    #     if not isinstance(script_component, Dialogue):
    #         raise TypeError(f"cannot perform {type(script_component)}")

    #     # If no tts, use fallback_tts
    #     if not self.tts and fallback_tts:
    #         self.set_tts(fallback_tts)

    #     # Split dialogue into parentheticals and dialogue
    #     subcomponents = script_component.split_parens_and_dialogue()
        
    #     # Remove parentheticals
    #     #@TODO allow parentheticals to influence TTS
    #     #@TODO-4 replace digits with words; replace …; replace & with and,
    #     #@ replace —; and others not in tts vocab
    #     spoken_dialogue = ""
    #     for subcomponent in subcomponents:
    #         if(subcomponent["type"] == "dialogue"):
    #             spoken_dialogue += subcomponent["text"]

    #     if self.tts:
    #         self.tts.say(spoken_dialogue,
    #                      speaker=self.speaker)
    #     else:
    #         print(f"WARNING: No TTS for {self.character_name}")
