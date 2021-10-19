"""
Living entities that have sprites and display to renderer window.
"""

# System Imports.
import sdl2.ext

# User Imports.
from .system_entities import Movement


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
        self.sprite.depth = 2


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
        self.sprite.depth = 0

        # Handle for edge tile walls.
        self.has_walls = False
        self.has_wall_north = False
        self.has_wall_east = False
        self.has_wall_south = False
        self.has_wall_west = False

        if tile_y == 0:
            self.has_walls = True
            self.has_wall_north = True
            wall_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('wall_north.png'))
            TileWall(world, wall_sprite, data_manager, tile_x=tile_x, tile_y=tile_y)

        if tile_x == (data_manager.sprite_data['sprite_w_count'] - 1):
            self.has_walls = True
            self.has_wall_east = True
            wall_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('wall_east.png'))
            TileWall(world, wall_sprite, data_manager, tile_x=tile_x, tile_y=tile_y)

        if tile_y == (data_manager.sprite_data['sprite_h_count'] - 1):
            self.has_walls = True
            self.has_wall_south = True
            wall_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('wall_south.png'))
            TileWall(world, wall_sprite, data_manager, tile_x=tile_x, tile_y=tile_y)

        if tile_x == 0:
            self.has_walls = True
            self.has_wall_west = True
            wall_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('wall_west.png'))
            TileWall(world, wall_sprite, data_manager, tile_x=tile_x, tile_y=tile_y)


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

        # Set entity depth mapping.
        self.sprite.depth = 1


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
        self.tile_set = []

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
            self.tile_set.append(curr_row)


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
