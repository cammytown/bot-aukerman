class DialogueLine:
    character_name: str
    dialogue: str
    parenthetical: str

    def __init__(self, character_name, dialogue, parenthetical = ""):
        self.character_name = character_name
        self.dialogue = dialogue
        self.parenthetical = parenthetical

    def __str__(self):
        parenthetical = ""
        if(self.parenthetical):
            parenthetical = f"({self.parenthetical})"

        return f"{self.character_name}{parenthetical}: {self.dialogue}"

    # def __repr__(self):
    #     return to_str(self)

    @staticmethod
    def from_str(dialogue_line_str):
        # Split on colon
        colon_split = dialogue_line_str.split(":", 1)

        # If there is no colon
        if(len(colon_split) == 1):
            #@TODO attempt to parse anyway
            raise ValueError("DialogueLine.from_str(): no colon found in dialogue_line_str: " + dialogue_line_str)

        parenthetical = ""

        # Check for parenthetical
        if("(" in colon_split[0]):
            character_name = colon_split[0].split("(")[0].strip()
            parenthetical = colon_split[0].split("(")[1].split(")")[0].strip()
        elif("[" in colon_split[0]):
            character_name = colon_split[0].split("[")[0].strip()
            parenthetical = colon_split[0].split("[")[1].split("]")[0].strip()
        # If no parenthetical
        else:
            character_name = colon_split[0]

        # Convert character_name to uppercase
        character_name = character_name.upper().strip()

        dialogue = colon_split[1].strip()

        # If there is no dialogue
        if(len(dialogue) == 0):
            raise ValueError("DialogueLine.from_str(): no dialogue found in dialogue_line_str: " + dialogue_line_str)

        # Check for parenthetical in dialogue
        #@TODO redundant code
        if("(" in dialogue):
            parenthetical = dialogue.split("(")[1].split(")")[0].strip()
            dialogue = dialogue.split("(")[0].strip()
        elif("[" in dialogue):
            parenthetical = dialogue.split("[")[1].split("]")[0].strip()
            dialogue = dialogue.split("[")[0].strip()

        # If dialogue is wrapped in quotes, remove them
        if(dialogue[0] == "\"" and dialogue[-1] == "\""):
            dialogue = dialogue[1:-1]

        # Return DialogueLine object
        return DialogueLine(character_name, dialogue, parenthetical)

