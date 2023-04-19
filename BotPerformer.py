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

        # If speaker not set, use first speaker in TTS
        else:
            #@REVISIT only for multi-speaker TTS:
            if(self.performance.tts.speakers):
                self.speaker = self.performance.tts.speakers[0]

        if(not self.tts):
            if(self.performance.tts):
                self.tts = self.performance.tts
            else:
                raise Exception("TTS not set.")

    def generate_dialogue(self, max_lines = 0):
        if(not self.chatbot):
            raise Exception("Performer.generate_dialogue(): chatbot not set")

        if(not self.performance):
            raise Exception("Performer.generate_dialogue(): performance not set")

        # Prepare prompt
        prompt = self.prepare_chatbot_prompt(max_lines)

        # Generate dialogue
        # If performer has internal chatbot, use it to generate dialogue
        if(self.chatbot):
            response = self.chatbot.send_message(prompt)

        # If performer has no internal chatbot, use performance's chatbot
        else:
            # If neither has a chatbot, raise exception
            if(not self.performance.chatbot):
                raise Exception("Performer.generate_dialogue(): chatbot not set")

            # If performance has a chatbot, use it to generate dialogue
            response = self.performance.chatbot.send_message(prompt)
            # response = self.chatbot.request_tokens()

        # Log the response
        self.performance.log(response)

        # Parse response into dialogue lines
        lines = self.performance.parse_chatbot_response(response)

        # Add dialogue to performance
        self.performance.add_dialogue(lines)

        return lines

    def prepare_chatbot_prompt(self, max_lines = 0):
        prompt = self.performance.prepare_chatbot_prompt(self, max_lines)
        return prompt

    def perform(self, dialogue):
        print("Performing", self.character_name)
        self.tts.say(dialogue, speaker=self.speaker)

        # if(not self.chatbot):
        #     if(self.performance.chatbot):
        #         self.chatbot = self.performance.chatbot
        #     else:
        #         raise Exception("Chatbot not set.")
