# from .interpreter import Interpreter
from .script_component import ScriptComponent
from .logging import warn

class Dialogue(ScriptComponent):
    character_name: str
    dialogue: str
    # parenthetical: str

    # # Static enum for formats
    # Format = Enum("Format", ["SINGLE_LINE", "MULTI_LINE"])

    # # Default format
    # format = Format.SINGLE_LINE

    def __init__(self, character_name, dialogue = ""):
        super().__init__()

        self.character_name = character_name
        self.dialogue = dialogue
        # self.parenthetical = parenthetical

    def to_str(self, multi_line = True):
        # parenthetical = ""
        # if(self.parenthetical):
        #     parenthetical = f"({self.parenthetical})"

        if(multi_line):
            return f"{self.character_name}\n{self.dialogue}"
            # if(parenthetical):
            #     parenthetical = "\n" + parenthetical
            # return f"{self.character_name}{parenthetical}\n{self.dialogue}"
        else:
            return f"{self.character_name}: " + self.dialogue.join("\n")
            # return f"{self.character_name}{parenthetical}: {self.dialogue}"

    def __str__(self):
        return self.to_str()

    # def __repr__(self):
    #     return to_str(self)

    def split_parens_and_dialogue(self) -> list[dict[str, str]]:
        """
        Split dialogue into parentheticals and dialogue.
        """

        # A list of dicts of form { "type": "paren" | "dialogue",
        #                           "text": str }
        subcomponents: list[dict[str, str]] = []
        dialogue = self.dialogue

        # While there is a parenthetical
        while("(" in dialogue):
            # Split on first parenthetical
            split = dialogue.split("(", 1)

            # Add dialogue to subcomponents
            if(split[0]):
                subcomponents.append({
                    "type": "dialogue",
                    "text": split[0]
                })

            # If there is no closing paren
            if not ")" in split[1]:
                warn("no closing parenthetical found in dialogue: " \
                     + dialogue)

                #@REVISIT treat as dialogue or parenthetical?
                subcomponents.append({ "type": "dialogue", "text": split[1] })

                # End loop
                break

            # Split on closing paren
            split = split[1].split(")", 1)

            # Add parenthetical to subcomponents
            subcomponents.append({ "type": "paren", "text": split[0] })

            # Remove parenthetical from dialogue, continue loop
            dialogue = split[1]

        # If there is dialogue left, add it to subcomponents
        if(dialogue):
            subcomponents.append({ "type": "dialogue", "text": dialogue })

        return subcomponents

