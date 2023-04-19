from typing import Optional

class Performer:
    character_name: str
    character_desc: str
    # performance: Optional[Performance] = None

    def __init__(self,
                 character_name,
                 character_desc = "No description",
     ):

        self.character_name = character_name
        self.character_desc = character_desc

    def perform(self, dialogue):
        #@REVISIT
        pass

    #@REVISIT naming:
    def get_description(self):
        description = self.character_name.upper() + ": " + self.character_desc
        return description

    def __str__(self):
        return self.character_name
