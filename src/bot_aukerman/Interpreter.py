from typing import List
from .ScriptComponent import ScriptComponent
from .SceneHeader import SceneHeader
from .Dialogue import Dialogue
from .SceneAction import SceneAction

#@TODO rename and move to isolated module; dramaparse,parsedrama,rescribe
class Interpreter:
    context: str = "none"
    working_component: dict = {}

    #@REVISIT architecture between this and parse_text
    @classmethod
    def interpret(cls, text, flags = {}) -> List[ScriptComponent]:
        """
        Interpret text as a script.
        """
        interpreter = cls()

        script_components = interpreter.parse_text(text, flags = flags)

        return script_components

    #@REVISIT architecture between this and interpret
    def parse_text(self, text, flags = {}) -> List[ScriptComponent]:
        # Reset interpreter state
        self.reset_state()

        if flags["ignore_first_char_newline"]:
            # If first character of response is a newline, remove it
            #@TODO make this optional at least?
            if(text[0] == "\n"):
                text = text[1:]

        if __debug__:
            print("Interpreting lines…")

        # Loop through lines
        lines = text.split("\n")
        script_components = self.parse_lines(lines)

        if __debug__:
            print("Finished interpreting lines. Results:")
            for component in script_components:
                print(component)
            print("End interpreter results.")

        return script_components

        # # If there is no character name
        # if(len(character_name) == 0):
        #     raise ValueError("no character name found in dialogue_string: " \
        #                      + dialogue_string)

        # # If there is no dialogue
        # if(len(dialogue) == 0):
        #     raise ValueError("no dialogue found in dialogue_string: " \
        #                      + dialogue_string)

        # # If dialogue is wrapped in quotes, remove them
        # #@TODO redundant
        # if(len(dialogue) > 2 and dialogue[0] == "\"" and dialogue[-1] == "\""):
        #     dialogue = dialogue[1:-1]


            # # If line contains a colon
            # try:
            #     if(":" in line):
            #         self.parse_single_line(line, flags)
            #     # If line does not contain a colon
            #     else:
            # except ValueError as e:
            #     print("WARNING: Invalid dialogue line:", line)
            #     print(e)
            #     continue

    def reset_state(self):
        self.context = "none"
        self.working_component = {}

    @staticmethod
    def auto_create_component(text) -> ScriptComponent:
        component_classes = [SceneHeader, Dialogue] #, SceneAction]

        for component_class in component_classes:
            try:
                component = component_class.from_str(text)
                return component
            except ValueError:
                pass

        raise ValueError("could not auto create component from text: " + text)

    def parse_lines(self, lines) -> List[ScriptComponent]:
        script_components = []

        for line_index, line in enumerate(lines):
            line = line.strip()

            if __debug__:
                print("context:", self.context, " | line:", line)

            match self.context:
                case "none":
                    # If line is empty
                    if(len(line) == 0):
                        continue

                    # Try to create script component from line
                    try:
                        component = Interpreter.auto_create_component(line)
                        script_components.append(component)

                    except ValueError:
                        print("WARNING: could not auto create component from " \
                                + "line: " + line)

                        # If all uppercase #@TODO hacky solution  
                        if(line.isupper()):
                            # Assume character name
                            self.working_component["character_name"] = line
                            self.context = "dialogue"
                        else:
                            #@TODO check if in character list; etc.
                            pass

                # case "character_name":
                #     # If line is empty
                #     if(len(line) == 0):
                #         continue

                case "dialogue" | "dialogue_continued":
                    # If line is empty
                    if(len(line) == 0):
                        # If expecting initial dialogue (none encountered yet)
                        if(self.context == "dialogue"):
                            # If last line was also blank
                            if(line_index > 0 and len(lines[line_index - 1]) == 0):
                                # Reset context after two blank lines
                                self.context = "none"

                        # If expecting more dialogue (some already supplied)
                        elif(self.context == "dialogue_continued"):
                            #@REVISIT
                            # Create component from working component dict
                            component = self.close_working_component()
                            script_components.append(component)
                            self.context = "none"

                    # If line is not empty
                    else:
                        # If line is all uppercase
                        if(line.isupper()):
                            print("WARNING: dialogue line is all uppercase: " \
                                    + line)

                        # If line is parenthetical
                        #@TODO multi-line parentheticals
                        elif(line[0] == "(" and line[-1] == ")"):
                            self.working_component["parenthetical"] = line[1:-1]
                            self.context = "dialogue"
                            continue

                        # If line is dialogue
                        else:
                            self.working_component["dialogue"] = line
                            self.context = "dialogue_continued"

                case _:
                    raise ValueError("invalid context: " + self.context)

        component = self.close_working_component()
        if component is not None:
            script_components.append(component)

        return script_components

    def close_working_component(self):
        match self.context:
            case "dialogue_continued":
                # Filter out empty values
                param_names = ["character_name", "dialogue", "parenthetical"]
                params = {
                        k: v for k,
                        v in self.working_component.items() if k in param_names
                        }
                return Dialogue(**params)
            case _:
                #@TODO double-check and remove warning
                print("WARNING: could not close working component with " \
                        + "context: " + self.context)

                return None

    #@REVISIT not currently in use
    def parse_single_line(self, text, flags):
        # Split on colon
        colon_split = text.split(":", 1)

        # If there is no colon
        if(len(colon_split) == 1):
            #@TODO attempt to parse anyway
            raise ValueError("no colon found in dialogue_line_str: " \
                             + text)

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
                    + text)

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

