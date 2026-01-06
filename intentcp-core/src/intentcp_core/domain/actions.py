# domain/actions.py
from enum import Enum
from typing import Callable, Any
from .devices import LogicalDevice

class ActionName(str, Enum):
    ON = "on"
    OFF = "off"
    BRIGHTNESS = "brightness"
    SEQUENCE = "sequence"
    # ...

class SequenceName(str, Enum):
    MOVIE = "movie"
    SLEEP = "sleep"
    MOOD = "mood"
    # ...