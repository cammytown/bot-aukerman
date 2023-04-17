from chatbots import Chatbot
from . import Performance

class Performer:
    character_name: str
    character_desc: str
    performance: Performance
    chatbot: Chatbot

    def __init__(self,
                 character_name,
                 character_desc = None,
                 performance = None,
                 chatbot = None,
     ):
        if(character_name):
            self.character_name = character_name

        if(character_desc):
            self.character_desc = character_desc
        else:
            self.character_desc = "No description"

        if(performance):
            self.performance = performance

        if(chatbot):
            self.chatbot = chatbot

    def perform(self, dialogue):
        #@REVISIT
        pass

    #@REVISIT naming:
    def get_description(self):
        description = self.character_name.upper() + ": " + self.character_desc
        return description

    def generate_dialogue(self, max_lines = 0):
        if(not self.chatbot):
            raise Exception("Performer.generate_dialogue(): chatbot not set")

        if(not self.performance):
            raise Exception("Performer.generate_dialogue(): performance not set")

        # Prepare prompt
        prompt = self.prepare_chatbot_prompt(max_lines)

        # Generate dialogue
        if(self.chatbot):
            response = self.chatbot.send_message(prompt)
        else:
            if(not self.performance.chatbot):
                raise Exception("Performer.generate_dialogue(): chatbot not set")

            response = self.performance.chatbot.send_message(prompt)

        # else:
        #     response = self.chatbot.request_tokens()

        # If logdir is set, write response to file
        #@REVISIT weird architecture; revisit
        if(self.performance.logdir):
            # Remove empty lines and strip surrounding whitespace from response
            response = response.replace("\n\n", "\n").strip()

            # Write response to file
            open(self.performance.logdir + "current-dialogue-history.txt",
                 "a").write(response)

        lines = self.performance.parse_chatbot_response(response)

        return lines

    def prepare_chatbot_prompt(self, max_lines = 0):
        prompt = self.performance.prepare_chatbot_prompt(self, max_lines)
        return prompt

    def __str__(self):
        return self.character_name
