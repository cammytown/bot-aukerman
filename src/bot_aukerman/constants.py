from enum import Enum
from typing import TypeVar
from .script_component import ScriptComponent

ScriptFormat = Enum("ScriptFormat", "MINIMAL, FOUNTAIN")

ScriptComponentType = TypeVar("ScriptComponentType", bound=ScriptComponent)
