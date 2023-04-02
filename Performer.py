class Performer:
    def __init__(self, character_name, character_desc = "No description"):
        self.character_name = character_name
        self.character_desc = character_desc

    def perform(self):
        character_name: str
        character_desc: str

        print("Performing", self.character_name)

    #@REVISIT naming:
    def get_description(self):
        description = self.character_name.upper() + ": " + self.character_desc
        return description
