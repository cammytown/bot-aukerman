class ScriptComponent:
    def __init__(self):
        pass

    def to_str(self):
        raise NotImplementedError

    def __str__(self):
        return self.to_str()

class Dialogue(ScriptComponent):
    def __init__(self, character_name, dialogue, parenthetical = ""):
        self.character_name = character_name
        self.dialogue = dialogue
        self.parenthetical = parenthetical

    def __str__(self):
        return self.character_name + ": " + self.dialogue

    def __repr__(self):
        return self.__str__()

class Action(ScriptComponent):
    def __init__(self, action):
        self.action = action

    def __str__(self):
        return self.action

    def __repr__(self):
        return self.__str__()

class SceneHeading(ScriptComponent):
    def __init__(self, scene_heading):
        self.scene_heading = scene_heading

    def __str__(self):
        return self.scene_heading

    def __repr__(self):
        return self.__str__()

