from typing import Optional
from .Performer import Performer
from chatbots.Chatbot import Chatbot #@REVISIT

class BotPerformer(Performer):
    chatbot: Optional[Chatbot] = None
    tts = None #@REVISIT
    speaker: str

    def __init__(
        self,
        character_name,
        character_desc = "No description",
        chatbot = None,
        tts = None,
        speaker = None
    ):
        # Initialize Performer:
        super().__init__(character_name, character_desc)

        self.chatbot = chatbot

        self.tts = tts

        if(speaker):
            self.speaker = speaker
        # # If speaker not set, use first speaker in TTS
        # else:
        #     #@REVISIT only for multi-speaker TTS:
        #     if(self.performance.tts.speakers):
        #         self.speaker = self.performance.tts.speakers[0]

    def perform(self, dialogue):
        print("Performing", self.character_name)
        self.tts.say(dialogue, speaker=self.speaker)

        # if(not self.chatbot):
        #     if(self.performance.chatbot):
        #         self.chatbot = self.performance.chatbot
        #     else:
        #         raise Exception("Chatbot not set.")
