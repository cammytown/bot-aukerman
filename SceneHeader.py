import re

from .ScriptComponent import ScriptComponent

class SceneHeader(ScriptComponent):
    # scene_number: int
    location_prefix: str
    location: str
    time: str

    # location_prefixes = ["INT", "EXT"]

    def __init__(self, location_prefix, location, time):
        super().__init__()

        self.location_prefix = location_prefix
        self.location = location
        self.time = time

    def to_str(self):
        return f"{self.location_prefix} {self.location} - {self.time}"

    def __str__(self):
        return self.to_str()

    @staticmethod
    def from_str(header_string):
        header_string = header_string.strip()

        location_prefix = ""
        location = ""
        time = ""

        # Search for location prefix
        location_prefix_regex = re.compile(r"^(INT|EXT)\.?\s")
        location_prefix_match = location_prefix_regex.search(header_string)
        if(location_prefix_match):
            # Set location prefix
            location_prefix = location_prefix_match.group(1)

            # Remove location prefix from header string
            header_string = header_string[location_prefix_match.end():]

        # Split on dash
        dash_split = header_string.split("-", 1)

        # If there is no dash
        if(len(dash_split) == 1):
            # Set location
            location = dash_split[0].strip()

        # If there is a dash
        elif(len(dash_split) == 2):
            # Set location
            location = dash_split[0].strip()

            # Set time
            time = dash_split[1].strip()

        # If there are more than 2 dashes
        else:
            raise ValueError("more than one dash found in header_string: " \
                             + header_string)

        # Create and return SceneHeader
        return SceneHeader(location_prefix, location, time)
