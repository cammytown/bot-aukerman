from typing import List
from .script_component import ScriptComponent
from .scene_header import SceneHeader
from .dialogue import Dialogue
from .scene_action import SceneAction
from .logging import warn

#@TODO rename and move to isolated module; dramaparse,parsedrama,rescribe
class Interpreter:
    context: str = "none"
    working_component: dict = {}

    verbose: bool = True

    #@REVISIT architecture between this and parse_text
    @classmethod
    def interpret(cls,
                  text,
                  flags = [],
                  as_type = None
                  ) -> List[ScriptComponent]:
        """
        Interpret text as a script.
        """
        interpreter = cls()

        script_components = interpreter.parse_text(text, flags = flags)

        # If as_type specified, filter out other types
        if as_type:
            valid_components = []
            for component in script_components:
                if isinstance(component, as_type):
                    valid_components.append(component)
                else:
                    warn(f"Component {component} is not of type {as_type}.")

            if len(valid_components) > 1:
                warn("Multiple components of type {as_type} found.")

            script_components = valid_components

        return script_components

    #@REVISIT architecture between this and interpret
    def parse_text(self, text, flags = []) -> List[ScriptComponent]:
        # Reset interpreter state
        self.reset_state()

        if "ignore_first_char_newline" in flags:
            # If first character of response is a newline, remove it
            #@TODO make this optional at least?
            if(text[0] == "\n"):
                text = text[1:]

        if __debug__ and self.verbose:
            print("Interpreting lines…")

        # Loop through lines
        lines = text.split("\n")
        script_components = self.parse_lines(lines)

        # Debug printing results
        if __debug__ and self.verbose:
            print("Finished interpreting lines. Results:")
            for component in script_components:
                print(component)
            print("End interpreter results.")

        return script_components

    def reset_state(self):
        self.context = "none"
        self.working_component = {}

    def parse_lines(self,
                    lines,
                    ) -> List[ScriptComponent]:
        components = []

        for line_index, line in enumerate(lines):
            line = line.strip()

            if __debug__ and self.verbose:
                print("context:", self.context, " | line:", line)

            match self.context:
                case "none":
                    # If line is empty
                    if(len(line) == 0):
                        continue

                    # Attempt to parse as scene header
                    try:
                        component = SceneHeader.from_str(line)
                        components.append(component)
                        continue
                    except ValueError as e:
                        warn(f"{e}")

                    # Attempt to parse as single line dialogue
                    try:
                        component = self.parse_single_line_dialogue(line)
                        components.append(component)
                        continue
                    except ValueError as e:
                        warn(f"{e}")

                    try:
                        component = SceneAction.from_str(line)
                        components.append(component)
                        continue
                    except ValueError as e:
                        warn(f"{e}")

                    # Attempt to parse as character name
                    # If all uppercase #@TODO hacky solution  
                    if(line.isupper()):
                        # Assume character name
                        self.working_component["character_name"] = line

                        # Await dialogue
                        self.context = "dialogue"
                    else:
                        #@TODO check if in character list; etc.
                        pass

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
                            components.append(component)
                            self.context = "none"

                    # If line is not empty
                    else:
                        # If line is all uppercase
                        if(line.isupper()):
                            if __debug__ and self.verbose:
                                warn(f"dialogue is all uppercase: {line}")

                        # Add line to dialogue
                        if(self.context == "dialogue"):
                            self.working_component["dialogue"] = line
                            self.context = "dialogue_continued"
                        else:
                            self.working_component["dialogue"] += "\n" + line

                case _:
                    raise ValueError("invalid context: " + self.context)

        component = self.close_working_component()
        if component is not None:
            components.append(component)

        return components

    def close_working_component(self):
        match self.context:
            case "dialogue" | "dialogue_continued":
                # Filter out empty values
                param_names = ["character_name", "dialogue", "parenthetical"]

                params = {
                        k: v for k,
                        v in self.working_component.items() if k in param_names
                        }

                return Dialogue(**params)
            case _:
                #@TODO double-check and remove warning
                if __debug__ and self.verbose:
                    warn(f"could not close component with context: {self.context}")

                return None

    #@REVISIT not currently in use
    def parse_single_line_dialogue(self, text):
        # Split on colon
        colon_split = text.split(":", 1)

        # If there is no colon
        if(len(colon_split) == 1):
            #@TODO attempt to parse anyway
            raise ValueError("no colon found in dialogue_line_str: " \
                             + text)

        parenthetical = ""

        # Check for parenthetical before colon
        #@REVISIT should we try to handle more than one?
        if("(" in colon_split[0] and ")" in colon_split[0]):
            character_name = colon_split[0].split("(")[0].strip()
            parenthetical = colon_split[0].split("(")[1].split(")")[0].strip()
        elif("[" in colon_split[0] and "]" in colon_split[0]):
            character_name = colon_split[0].split("[")[0].strip()
            parenthetical = colon_split[0].split("[")[1].split("]")[0].strip()

        # If no parenthetical
        else:
            character_name = colon_split[0]

        # Convert character_name to uppercase
        character_name = character_name.upper().strip()

        dialogue = colon_split[1].strip()

        # If paren in character name, prepend to dialogue
        if parenthetical:
            dialogue = f"{parenthetical} {dialogue}"

        # If there is no dialogue
        if(len(dialogue) == 0):
            raise ValueError(f"no dialogue found in dialogue_line_str: {text}")

        return Dialogue(character_name, dialogue)

    # def parse_single_line(self, line: str, flags: dict):
    #     if flags["discard_multiple_char_names"]:
    #         # Extract character headers from line into list
    #         header_regex = r"[A-Z ]+:"
    #         character_headers = re.findall(header_regex, line)

    #         # If there are multiple character headers
    #         if(len(character_headers) > 1):
    #             # Split line on instances of character headers
    #             inner_lines = re.split(header_regex, line)

    #             # Remove text before first character header
    #             #@DOUBLE-CHECK
    #             inner_lines = inner_lines[1:]

    #             if __debug__:
    #                 print("character_headers:", character_headers)
    #                 print("inner_lines:", inner_lines)

    #             # Attempt to validate each inner line
    #             for i, inner_line in enumerate(inner_lines):
    #                 # If inner line is empty, skip
    #                 if(inner_line == ""):
    #                     continue

    #                 # Prepend character header to inner line
    #                 #@REVISIT i-1 is always correct, right?
    #                 inner_line = character_headers[i-1].strip() \
    #                         + inner_line

    #                 # Parse inner line into a Dialogue object
    #                 try:
    #                     line_obj = Dialogue.from_str(inner_line)
    #                     dialogue_lines.append(line_obj)
    #                 except ValueError as e: #@REVISIT ugly
    #                     continue

    #         # Parse line into a Dialogue object
    #         line_obj = Dialogue.from_str(line)
    #         dialogue_lines.append(line_obj)

    #     return dialogue_lines

