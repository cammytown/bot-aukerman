from .script_component import ScriptComponent

class Dialogue(ScriptComponent):
    character_name: str
    dialogue: str
    parenthetical: str

    # # Static enum for formats
    # Format = Enum("Format", ["SINGLE_LINE", "MULTI_LINE"])

    # # Default format
    # format = Format.SINGLE_LINE

    def __init__(self, character_name, dialogue, parenthetical = ""):
        super().__init__()

        self.character_name = character_name
        self.dialogue = dialogue
        self.parenthetical = parenthetical

    def to_str(self, multi_line = True):
        parenthetical = ""
        if(self.parenthetical):
            parenthetical = f"({self.parenthetical})"

        if(multi_line):
            if(parenthetical):
                parenthetical = "\n" + parenthetical
            return f"{self.character_name}{parenthetical}\n{self.dialogue}"
        else:
            return f"{self.character_name}{parenthetical}: {self.dialogue}"

    def __str__(self):
        return self.to_str()

    # def __repr__(self):
    #     return to_str(self)

    @staticmethod
    def from_str(dialogue_line_str):
        # Try to parse as single line
        try:
            return Dialogue.from_single_line(dialogue_line_str)
        except ValueError:
            pass

        # Try to parse as multi-line
        try:
            return Dialogue.from_multi_line(dialogue_line_str)
        except ValueError:
            pass

        # If neither works, raise error
        raise ValueError("dialogue_line_str could not be parsed: " \
                + dialogue_line_str)

    @staticmethod
    def from_single_line(dialogue_line_str):
        # Split on colon
        colon_split = dialogue_line_str.split(":", 1)

        # If there is no colon
        if(len(colon_split) == 1):
            #@TODO attempt to parse anyway
            raise ValueError("no colon found in dialogue_line_str: " \
                             + dialogue_line_str)

        parenthetical = ""

        # Check for parenthetical before colon
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
            raise ValueError("no dialogue found in dialogue_line_str: " \
                    + dialogue_line_str)

        # Check for parenthetical after colon
        #@TODO redundant code
        if("(" in dialogue):
            parenthetical = dialogue.split("(")[1].split(")")[0].strip()
            dialogue = dialogue.split("(")[0].strip() #@REVISIT seems wrong
        elif("[" in dialogue):
            parenthetical = dialogue.split("[")[1].split("]")[0].strip()
            dialogue = dialogue.split("[")[0].strip() #@REVISIT seems wrong

        # If dialogue is wrapped in quotes, remove them
        if(len(dialogue) > 2 and dialogue[0] == "\"" and dialogue[-1] == "\""):
            dialogue = dialogue[1:-1]

        return Dialogue(character_name, dialogue, parenthetical)

    @staticmethod
    def from_multi_line(dialogue_string):
        # Split on newline
        lines = dialogue_string.split("\n")

        # If there are no lines
        if(len(lines) == 0):
            raise ValueError("no lines found in dialogue_string: " \
                             + dialogue_string)

        # If there is only one line
        if(len(lines) == 1):
            raise ValueError("only one line found in dialogue_string: " \
                             + dialogue_string)

        parser_state = "character_name"
        character_name = ""
        dialogue = ""
        parenthetical = ""

        # Loop through lines
        for line in lines:

            match parser_state:
                case "character_name":
                    # If line is empty
                    if(len(line.strip()) == 0):
                        continue
                    # If all uppercase
                    #@TODO hacky solution to gauge likelihood of being a
                    #character name probably do more; at least check if non-caps
                    #name is in character list
                    elif(line.isupper()):
                        character_name = line
                        parser_state = "dialogue"
                    else:
                        #@TODO check if in character list
                        continue

                case "dialogue" | "dialogue_continued":
                    # If line is empty
                    if(len(line.strip()) == 0):
                        if(parser_state == "dialogue_continued"):
                            #@REVISIT
                            parser_state = "character_name"

                    # If all uppercase
                    if(line.isupper()):
                        print("WARNING: dialogue line is all uppercase: " \
                                + line)

                    # If line is parenthetical
                    #@TODO multi-line parentheticals
                    elif(line[0] == "(" and line[-1] == ")"):
                        parenthetical = line[1:-1]
                        parser_state = "dialogue"
                        continue

                    else:
                        dialogue += line + " "
                        parser_state = "dialogue_continued"

        # If there is no character name
        if(len(character_name) == 0):
            raise ValueError("no character name found in dialogue_string: " \
                             + dialogue_string)

        # If there is no dialogue
        if(len(dialogue) == 0):
            raise ValueError("no dialogue found in dialogue_string: " \
                             + dialogue_string)

        # If dialogue is wrapped in quotes, remove them
        #@TODO redundant
        if(len(dialogue) > 2 and dialogue[0] == "\"" and dialogue[-1] == "\""):
            dialogue = dialogue[1:-1]

        return Dialogue(character_name, dialogue, parenthetical)
