from .ScriptComponent import ScriptComponent

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
        return SceneAction(action_str)
