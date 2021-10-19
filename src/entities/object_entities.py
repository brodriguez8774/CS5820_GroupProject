"""
Living entities that have sprites and display to renderer window.

Sprite Depth Values (0 is lowest. Higher values will display ontop of lower ones):
 * Roomba: 3
 * Active Wall: 2
 * Floor Tile: 1
 * Hidden/Unused Sprites: 0
"""

# System Imports.
import sdl2.ext

# User Imports.
from .system_entities import Movement, Walls


# Module Variables.
# Here, we point to our image files to render to user.
RESOURCES = sdl2.ext.Resources(__file__, '../images/')


class Roomba(sdl2.ext.Entity):
    """
    A roomba/vacuum entity.
    """
    def __init__(self, world, sprite, data_manager, tile_x=0, tile_y=0):
        # Set entity display image.
        self.sprite = sprite

        # Define world systems which affect entity.
        self.movement = Movement(data_manager)

        # Set entity location tracking.
        self.sprite.tile = tile_x, tile_y
        self.sprite.position = self.movement.calculate_pix_from_tile(tile_x, tile_y)

        # Set entity depth mapping.
        self.sprite.depth = 3


class Tile(sdl2.ext.Entity):
    """
    A single tile, representing a single location in the environment.
    """
    def __init__(self, world, sprite, data_manager, tile_x=0, tile_y=0):
        # Set entity display image.
        self.sprite = sprite

        # Define world systems which affect entity.
        self.movement = Movement(data_manager)

        # Set entity location tracking.
        self.sprite.tile = tile_x, tile_y
        self.sprite.position = self.movement.calculate_pix_from_tile(tile_x, tile_y)

        # Set entity depth mapping.
        self.sprite.depth = 1

        # Initialize tile wall data.
        wall_sprite_north = data_manager.sprite_factory.from_image(RESOURCES.get_path('wall_north.png'))
        wall_sprite_east = data_manager.sprite_factory.from_image(RESOURCES.get_path('wall_east.png'))
        wall_sprite_south = data_manager.sprite_factory.from_image(RESOURCES.get_path('wall_south.png'))
        wall_sprite_west = data_manager.sprite_factory.from_image(RESOURCES.get_path('wall_west.png'))
        wall_data = {
            'north': TileWall(world, wall_sprite_north, data_manager, tile_x=tile_x, tile_y=tile_y),
            'east': TileWall(world, wall_sprite_east, data_manager, tile_x=tile_x, tile_y=tile_y),
            'south': TileWall(world, wall_sprite_south, data_manager, tile_x=tile_x, tile_y=tile_y),
            'west': TileWall(world, wall_sprite_west, data_manager, tile_x=tile_x, tile_y=tile_y),
        }
        self.walls = Walls(data_manager, tile_x, tile_y, wall_data)


class TileWall(sdl2.ext.Entity):
    """
    A single wall on a tile.
    Represents a barrier in one of the four directions (north, south, east, west).
    """
    def __init__(self, world, sprite, data_manager, tile_x=0, tile_y=0):
        # Set entity display image.
        self.sprite = sprite

        # Define world systems which affect entity.
        self.movement = Movement(data_manager)

        # Set entity location tracking.
        self.sprite.tile = tile_x, tile_y
        self.sprite.position = self.movement.calculate_pix_from_tile(tile_x, tile_y)

        # Set entity depth mapping. Defaults to 0 so it's hidden from view.
        self.sprite.depth = 0


class TileSet:
    """
    Holds/Generates set of all sprite tiles.
    """
    def __init__(self, data_manager):
        """
        :param data_manager: Data manager data structure. Consolidates useful program data to one location.
        """
        # Save class variables.
        self.sprite_renderer = data_manager.sprite_renderer
        self.window_data = data_manager.window_data
        self.sprite_data = data_manager.sprite_data
        self.tiles = []

        # Initialize all tiles.
        for row_index in range(self.sprite_data['sprite_h_count']):

            # Initialize row of tiles.
            curr_row = []

            # Initialize each tile in row.
            for col_index in range(self.sprite_data['sprite_w_count']):
                curr_row.append(
                    Tile(
                        data_manager.world,
                        data_manager.sprite_factory.from_image(RESOURCES.get_path('background.png')),
                        data_manager,
                        tile_x=col_index,
                        tile_y=row_index,
                    )
                )

            # Set full row to tile set.
            self.tiles.append(curr_row)


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
