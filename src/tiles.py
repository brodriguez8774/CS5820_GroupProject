"""
Tiles classes to store tile object data.
Used to manage state and handle displaying data to user.
"""

# System Imports.
import sdl2.ext


# Module Variables.
# Here, we point to our image files to render to user.
RESOURCES = sdl2.ext.Resources(__file__, './images/')


class TileSet:
    """
    Holds set of all sprite tiles.
    """
    def __init__(self, sprite_factory, sprite_renderer, window_data, sprite_data):
        # Save class variables.
        self.sprite_renderer = sprite_renderer
        self.window_data = window_data
        self.sprite_data = sprite_data
        self.tile_set = []

        # Initialize all tiles.
        for row_index in range(sprite_data['sprite_h_count']):

            # Initialize row of tiles.
            curr_row = []
            y_coord = (row_index * 50) + sprite_data['max_pixel_top']

            # Initialize each tile in row.
            for col_index in range(sprite_data['sprite_w_count']):
                x_coord = (col_index * 50) + sprite_data['max_pixel_left']
                curr_row.append(
                    Tile(
                        sprite_factory,
                        sprite_renderer,
                        window_data,
                        sprite_data,
                        x_coord,
                        y_coord,
                        row_index,
                        col_index,
                    )
                )

            # Set full row to tile set.
            self.tile_set.append(curr_row)


class Tile:
    """
    A single tile, representing a single location in the environment.
    """
    def __init__(
        self,
        sprite_factory, sprite_renderer, window_data, sprite_data, window_x_coord, window_y_coord, row_index, col_index,
    ):
        self.sprite_factory = sprite_factory
        self.sprite_renderer = sprite_renderer
        self.window_data = window_data
        self.sprite_data = sprite_data
        self.row_index = row_index
        self.col_index = col_index
        self.x = window_x_coord
        self.y = window_y_coord

        # Render base tile background.
        sprite_background = sprite_factory.from_image(RESOURCES.get_path('background.png'))
        sprite_background.x = self.x
        sprite_background.y = self.y
        sprite_renderer.render(sprite_background)

        print('x: {0}    y: {1}'.format(self.col_index, self.row_index))

        # Handle for edge tile walls.
        if self.row_index == 0:
            self.display_north_wall()
        elif self.row_index == (self.sprite_data['sprite_h_count'] - 1):
            self.display_south_wall()
        if self.col_index == 0:
            self.display_west_wall()
        elif self.col_index == (self.sprite_data['sprite_w_count'] - 1):
            self.display_east_wall()

    def display_north_wall(self):
        """

        :return:
        """
        print('    displaying north/top wall'.format(self.col_index, self.row_index))
        wall_background = self.sprite_factory.from_image(RESOURCES.get_path('wall_north.png'))
        wall_background.x = self.x
        wall_background.y = self.y
        self.sprite_renderer.render(wall_background)

    def display_east_wall(self):
        """

        :return:
        """
        print('    displaying east/right wall'.format(self.col_index, self.row_index))
        wall_background = self.sprite_factory.from_image(RESOURCES.get_path('wall_east.png'))
        wall_background.x = self.x
        wall_background.y = self.y
        self.sprite_renderer.render(wall_background)

    def display_south_wall(self):
        """

        :return:
        """
        print('    displaying south/bottom wall'.format(self.col_index, self.row_index))
        wall_background = self.sprite_factory.from_image(RESOURCES.get_path('wall_south.png'))
        wall_background.x = self.x
        wall_background.y = self.y
        self.sprite_renderer.render(wall_background)

    def display_west_wall(self):
        """

        :return:
        """
        print('    displaying west/left wall'.format(self.col_index, self.row_index))
        wall_background = self.sprite_factory.from_image(RESOURCES.get_path('wall_west.png'))
        wall_background.x = self.x
        wall_background.y = self.y
        self.sprite_renderer.render(wall_background)
