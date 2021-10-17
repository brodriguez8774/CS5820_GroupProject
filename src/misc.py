"""

"""

# System Imports.
import sdl2.ext
from abc import ABC, abstractmethod


# Module Variables.
# Here, we point to our image files to render to user.
RESOURCES = sdl2.ext.Resources(__file__, './images/')


class DataManager:
    """
    Stores and manages general data, to minimize values needing to be passed back and forth between classes.
    """
    def __init__(self, world, window, sprite_factory, sprite_renderer, window_data, sprite_data):
        self.world = world
        self.window = window
        self.sprite_factory = sprite_factory
        self.sprite_renderer = sprite_renderer
        self.window_data = window_data
        self.sprite_data = sprite_data
