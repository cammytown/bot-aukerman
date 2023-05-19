from .script_component import ScriptComponent

class SceneAction(ScriptComponent):
    action: str

    def __init__(self, action):
        super().__init__()

        self.action = action

    def to_str(self):
        return f"{self.action}"

    def __str__(self):
        return self.to_str()

    @staticmethod
    def from_str(action_str):
        if action_str.isupper():
            #@REVISIT might want a more complex check; can action ever be all caps?
            #@ we might need to look at next line
            raise ValueError(f"action_str is all uppercase: {action_str}")

        return SceneAction(action_str)
