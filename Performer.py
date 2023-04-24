from typing import Optional
from chatbots import Chatbot

class Performer:
    character_name: str
    character_desc: str
    chatbot: Optional[Chatbot] = None
    # performance: Optional[Performance] = None

    def __init__(self,
                 character_name,
                 character_desc = "No description",
                 chatbot = None
     ):

        self.character_name = character_name
        self.character_desc = character_desc
        self.chatbot = chatbot

    # def perform(self, dialogue):
    #     #@REVISIT
    #     pass

    #@REVISIT naming:
    def get_description(self):
        description = self.character_name.upper() + ": " + self.character_desc
        return description

    def __str__(self):
        return self.character_name
