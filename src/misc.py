"""
Misc helper classes.
"""

# System Imports.
import sdl2.ext


# Module Variables.
# Here, we point to our image files to render to user.
RESOURCES = sdl2.ext.Resources(__file__, './images/')


# region Data Structures

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
        self.tile_set = None
        self.roomba = None

# endregion Data Structures


# region Handler Functions

def handle_key_press(data_manager, event):
    """
    Handles key press event when running program.
    :param data_manager: Data manager data structure. Consolidates useful program data to one location.
    :param event: Event instance to handle. Only confirmed "key press" events should be passed here.
    """
    roomba = data_manager.roomba

    # Handle if arrow direction was pressed.
    if event.key.keysym.sym in [sdl2.SDLK_UP, sdl2.SDLK_w]:
        roomba.movement.north = True

    elif event.key.keysym.sym in [sdl2.SDLK_RIGHT, sdl2.SDLK_d]:
        roomba.movement.east = True

    elif event.key.keysym.sym in [sdl2.SDLK_DOWN, sdl2.SDLK_s]:
        roomba.movement.south = True

    elif event.key.keysym.sym in [sdl2.SDLK_LEFT, sdl2.SDLK_a]:
        roomba.movement.west = True


def handle_mouse_click(data_manager, pos_x, pos_y):
    """
    Handles mouse click event when running program.
    :param data_manager: Data manager data structure. Consolidates useful program data to one location.
    :param pos_x: Mouse click x coordinate.
    :param pos_y: Mouse click y coordinate.
    """
    # print('sprite_data[max_pixel_north]: {0}'.format(sprite_data['max_pixel_north']))
    # print('sprite_data[max_pixel_east]: {0}'.format(sprite_data['max_pixel_east']))
    # print('sprite_data[max_pixel_south]: {0}'.format(sprite_data['max_pixel_south']))
    # print('sprite_data[max_pixel_west]: {0}'.format(sprite_data['max_pixel_west']))
    print('pos_x.value: {0}    pos_y.value: {1}'.format(pos_x, pos_y))

    # First, verify that click location is within tile grid bounds. If not, we ignore click.
    sprite_data = data_manager.sprite_data
    if (
        (pos_x > sprite_data['max_pixel_west'] and pos_x < sprite_data['max_pixel_east']) and
        (pos_y > sprite_data['max_pixel_north'] and pos_y < sprite_data['max_pixel_south'])
    ):
        # Click was within tile bounds. Calculate clicked tile.
        print('    is within bounds.')
        tile_x = int((pos_x - sprite_data['max_pixel_west']) / 50)
        tile_y = int((pos_y - sprite_data['max_pixel_north']) / 50)
        print('    found tile is    x: {0}    y: {1}'.format(tile_x, tile_y))

# endregion Handler Functions
