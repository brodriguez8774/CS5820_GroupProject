"""
Tiles classes to store tile object data.
Used to manage state and handle displaying data to user.
"""

# System Imports.
import sdl2.ext

# User Imports.
from .entities import Roomba


# Module Variables.
# Here, we point to our image files to render to user.
RESOURCES = sdl2.ext.Resources(__file__, './images/')


class TileSet:
    """
    Holds set of all sprite tiles.
    """
    def __init__(self, data_manager, roomba):
        """
        :param sprite_factory: Generates sprite objects for SDL2 display.
        :param sprite_renderer: Renders sprite objects to window.
        :param window_data: Dict of general window data.
        :param sprite_data: Dict of general sprite data.
        :param roomba: Roomba/vacuum entity.
        """
        # Save class variables.
        self.sprite_renderer = data_manager.sprite_renderer
        self.window_data = data_manager.window_data
        self.sprite_data = data_manager.sprite_data
        self.tile_set = []
        self.roomba = roomba

        # Initialize all tiles.
        for row_index in range(self.sprite_data['sprite_h_count']):

            # Initialize row of tiles.
            curr_row = []
            y_coord = (row_index * 50) + self.sprite_data['max_pixel_top']

            # Initialize each tile in row.
            for col_index in range(self.sprite_data['sprite_w_count']):
                x_coord = (col_index * 50) + self.sprite_data['max_pixel_left']
                curr_row.append(
                    Tile(
                        data_manager,
                        x_coord,
                        y_coord,
                        row_index,
                        col_index,
                        self.roomba,
                    )
                )

            # Set full row to tile set.
            self.tile_set.append(curr_row)


class Tile:
    """
    A single tile, representing a single location in the environment.
    """
    def __init__(self, data_manager, window_x_coord, window_y_coord, row_index, col_index, roomba):
        """
        :param data_manager:
        :param window_x_coord:
        :param window_y_coord:
        :param row_index:
        :param col_index:
        :param roomba: Roomba/vacuum entity.
        """
        self.sprite_factory = data_manager.sprite_factory
        self.sprite_renderer = data_manager.sprite_renderer
        self.window_data = data_manager.window_data
        self.sprite_data = data_manager.sprite_data
        self.row_index = row_index
        self.col_index = col_index
        self.x = window_x_coord
        self.y = window_y_coord
        self.roomba = roomba

        # Initialize internal tile data.
        self.has_roomba = False
        self.has_walls = False
        self.has_wall_north = False
        self.has_wall_east = False
        self.has_wall_south = False
        self.has_wall_west = False

        print('x: {0}    y: {1}'.format(self.col_index, self.row_index))

        # Render base tile background.
        sprite_background = self.sprite_factory.from_image(RESOURCES.get_path('background.png'))
        sprite_background.x = self.x
        sprite_background.y = self.y
        sprite_background.depth = 0
        # sprite_renderer.render(sprite_background)

        # Handle for edge tile walls.
        if self.row_index == 0:
            self.display_north_wall()
        elif self.row_index == (self.sprite_data['sprite_h_count'] - 1):
            self.display_south_wall()
        if self.col_index == 0:
            self.display_west_wall()
        elif self.col_index == (self.sprite_data['sprite_w_count'] - 1):
            self.display_east_wall()

        # Handle for roomba starting on tile.
        w_count_center = int(self.sprite_data['sprite_w_count'] / 2)
        h_count_center = int(self.sprite_data['sprite_h_count'] / 2)
        if self.col_index == w_count_center and self.row_index == h_count_center:
            # self.display_roomba()
            self.roomba.set_position(self.col_index, self.row_index)

    def display_roomba(self):
        """
        Sets internal tile data to handle for roomba existing on tile.
        """
        print('    displaying roomba')

        # Render roomba sprite.
        roomba_sprite = self.sprite_factory.from_image(RESOURCES.get_path('roomba.png'))
        roomba_sprite.x = self.x
        roomba_sprite.y = self.y
        self.sprite_renderer.render(roomba_sprite)

        # Set internal wall data.
        self.has_roomba = True

    def display_north_wall(self):
        """
        Sets internal tile data to handle for north (top) wall on tile.
        """
        print('    displaying north/top wall')

        # Render wall sprite.
        wall_background = self.sprite_factory.from_image(RESOURCES.get_path('wall_north.png'))
        wall_background.x = self.x
        wall_background.y = self.y
        self.sprite_renderer.render(wall_background)

        # Set internal wall data.
        self.has_walls = True
        self.has_wall_north = True

    def display_east_wall(self):
        """
        Sets internal tile data to handle for east (right) wall on tile.
        """
        print('    displaying east/right wall')

        # Render wall sprite.
        wall_background = self.sprite_factory.from_image(RESOURCES.get_path('wall_east.png'))
        wall_background.x = self.x
        wall_background.y = self.y
        self.sprite_renderer.render(wall_background)

        # Set internal wall data.
        self.has_walls = True
        self.has_wall_east = True

    def display_south_wall(self):
        """
        Sets internal tile data to handle for south (bottom) wall on tile.
        """
        print('    displaying south/bottom wall')

        # Render wall sprite.
        wall_background = self.sprite_factory.from_image(RESOURCES.get_path('wall_south.png'))
        wall_background.x = self.x
        wall_background.y = self.y
        self.sprite_renderer.render(wall_background)

        # Set internal wall data.
        self.has_walls = True
        self.has_wall_south = True

    def display_west_wall(self):
        """
        Sets internal tile data to handle for west (left) wall on tile.
        """
        print('    displaying west/left wall')

        # Render wall sprite.
        wall_background = self.sprite_factory.from_image(RESOURCES.get_path('wall_west.png'))
        wall_background.x = self.x
        wall_background.y = self.y
        self.sprite_renderer.render(wall_background)

        # Set internal wall data.
        self.has_walls = True
        self.has_wall_west = True
