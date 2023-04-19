from .Performer import Performer

class HumanPerformer(Performer):
    def __init__(self,
        character_name,
        character_desc = None,
    ):
        super().__init__(
                character_name = character_name,
                character_desc = character_desc,
        )

