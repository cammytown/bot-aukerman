from .Performer import Performer
from chatbots.Chatbot import Chatbot #@REVISIT

class BotPerformer(Performer):
    chatbot: Chatbot
    tts = None #@REVISIT
    speaker: str

    def __init__(
        self,
        character_name,
        character_desc = None,
        performance = None,
        chatbot = None,
        tts = None,
        speaker = None
    ):
        # Initialize Performer:
        super().__init__(character_name, character_desc, performance)

        if(chatbot):
            self.chatbot = chatbot

        if(tts):
            self.tts = tts

        if(speaker):
            self.speaker = speaker

        if(not self.performance):
            raise Exception("Performer Performance not set.")

        if(not self.tts):
            if(self.performance.tts):
                self.tts = self.performance.tts
            else:
                raise Exception("TTS not set.")

        if(not self.speaker):
            #@REVISIT only for multi-speaker TTS:
            if(self.performance.tts.speakers):
                self.speaker = self.performance.tts.speakers[0]

    def perform(self, dialogue):
        print("Performing", self.character_name)
        self.tts.say(dialogue, speaker=self.speaker)

        # if(not self.chatbot):
        #     if(self.performance.chatbot):
        #         self.chatbot = self.performance.chatbot
        #     else:
        #         raise Exception("Chatbot not set.")
