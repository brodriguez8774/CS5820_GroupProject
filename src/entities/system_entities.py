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
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.north = False
        self.east = False
        self.south = False
        self.west = False

    def calculate_pix_from_tile(self, tile_x, tile_y):
        """
        Computes the corresponding pixel location for the provided tile grid coordinates.
        :param tile_x: Tile column (x-axis) of entity.
        :param tile_y: Tile row (y-axis) of entity.
        :return: Corresponding (x,y) pixel grid coordinates that match tile location.
        """
        pos_x = (tile_x * 50) + self.data_manager.sprite_data['max_pixel_west']
        pos_y = (tile_y * 50) + self.data_manager.sprite_data['max_pixel_north']

        # Return calculated pixel coordinates.
        return pos_x, pos_y
