"""
Living entities that change during program execution.
"""

# User Imports.
from .abstract import BaseEntity


class Roomba(BaseEntity):
    """
    The roomba/vacuum entity that does the work.
    """
    def __init__(self, sprite_factory, sprite_renderer, sprite_data, tile_x_pos, tile_y_pos, sprite='roomba.png'):
        # Call parent logic.
        super().__init__(sprite_factory, sprite_renderer, sprite_data, tile_x_pos, tile_y_pos, sprite=sprite)

        # Set drawing order.
        self.sprite.depth = 2


class TrashBall(BaseEntity):
    """
    An instance of "trash" occupying a single square.
    """
    def __init__(self, sprite_factory, sprite_renderer, sprite_data, tile_x_pos, tile_y_pos, sprite=None):
        # Call parent logic.
        super().__init__(sprite_factory, sprite_renderer, sprite_data, tile_x_pos, tile_y_pos, sprite=sprite)

        # Set drawing order.
        self.sprite.depth = 1
