class ScriptComponent:
    def __init__(self):
        pass

    def to_str(self):
        raise NotImplementedError

    def __str__(self):
        return self.to_str()
