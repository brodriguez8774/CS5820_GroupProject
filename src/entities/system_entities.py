"""
System entities that hold general system/world data in some manner.
"""

# System Imports.
import sdl2.ext

# User Imports.


class Movement:
    """
    Holds movement tick data for an entity.
    """
    def __init__(self):
        self.north = False
        self.east = False
        self.south = False
        self.west = False
