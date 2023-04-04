class Performer:
    def __init__(self,
                 character_name,
                 character_desc = None,
                 performance = None,
     ):
        self.character_name = character_name
        self.character_desc = character_desc
        self.performance = performance

        if(not self.character_desc):
            self.character_desc = "No description"


    def perform(self, dialogue):
        #@REVISIT
        pass

    #@REVISIT naming:
    def get_description(self):
        description = self.character_name.upper() + ": " + self.character_desc
        return description
