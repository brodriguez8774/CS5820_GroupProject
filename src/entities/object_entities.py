"""
Living entities that have sprites and display to renderer window.
"""

# System Imports.
import sdl2.ext

# User Imports.
from .system_entities import Movement


class Roomba(sdl2.ext.Entity):
    """
    A roomba/vacuum entity.
    """
    def __init__(self, world, sprite, pos_x=0, pos_y=0):
        self.sprite = sprite
        # self.tile =
        self.sprite.position = pos_x, pos_y
        self.movement = Movement()


# class Roomba:
#     """
#     The roomba/vacuum entity that does the work.
#     """
#     def __init__(self, world, sprite, tile_pos_x=0, tile_pos_y=0, pix_pos_x=0, pix_pos_y=0):
#         self.sprite = sprite
#         self.sprite.tile = 0, 0                         # Set starting tile location in window.
#         self.sprite.pix_position = pix_pos_x, pix_pos_y     # Set starting pixel location in window.
#         self.sprite.depth = 2   # Set drawing order. 0 is bottom, higher numbers is above other sprites.
#
#
# class TrashBall(BaseEntity):
#     """
#     An instance of "trash" occupying a single square.
#     """
#     def __init__(self, world, data_manager, tile_x_pos, tile_y_pos, sprite=None):
#         # Call parent logic.
#         super().__init__(world, data_manager, tile_x_pos, tile_y_pos, sprite=sprite)
#
#         # Set drawing order.
#         self.sprite.depth = 1
