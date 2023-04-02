from .Performer import Performer
from chatbots.Chatbot import Chatbot #@REVISIT

class BotPerformer(Performer):
    chatbot: Chatbot

    def __init__(self, character_name, character_description):
        # Initialize Performer:
        super().__init__(character_name, character_description)
