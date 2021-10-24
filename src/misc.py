"""
Misc helper functions and classes.
"""

# System Imports.
import sdl2.ext
import networkx

# User Imports.
from src.logging import init_logging


# Initialize logger.
logger = init_logging(__name__)


# Module Variables.
# Here, we point to our image files to render to user.
RESOURCES = sdl2.ext.Resources(__file__, './images/')


# region Data Structures

class DataManager:
    """
    Stores and manages general data, to minimize values needing to be passed back and forth between classes.
    """
    def __init__(self, world, window, sprite_factory, sprite_renderer, window_data, gui_data, tile_data):
        self.world = world
        self.window = window
        self.sprite_factory = sprite_factory
        self.sprite_renderer = sprite_renderer
        self.window_data = window_data
        self.gui_data = gui_data
        self.tile_data = tile_data
        self.gui = None
        self.tile_set = None
        self.roomba = None
        self.graph = networkx.Graph()

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


def handle_mouse_click(data_manager, button_state, pos_x, pos_y):
    """
    Handles mouse click event when running program.
    :param data_manager: Data manager data structure. Consolidates useful program data to one location.
    :param button_state: State of button on event. 1 = LeftClick, 2 = MiddleClick, 4 = RightClick.
    :param pos_x: Mouse click x coordinate.
    :param pos_y: Mouse click y coordinate.
    """
    logger.info('pos_x.value: {0}    pos_y.value: {1}'.format(pos_x, pos_y))
    logger.info('buttonstate: {0}'.format(button_state))

    # First, verify that click location is within some valid grid bounds. If not, we ignore click.
    gui_data = data_manager.gui_data
    tile_data = data_manager.tile_data
    if (
        (pos_x > gui_data['gui_w_start'] and pos_x < gui_data['gui_w_end']) and
        (pos_y > gui_data['gui_h_start'] and pos_y < gui_data['gui_h_end'])
    ):
        # Click was within gui bounds. Check if any gui elements were clicked.
        logger.info('    Is within GUI element bounds.')

        for element in data_manager.gui.elements:
            if (
                (pos_x > element.bounds['max_pixel_west'] and pos_x < element.bounds['max_pixel_east']) and
                (pos_y > element.bounds['max_pixel_north'] and pos_y < element.bounds['max_pixel_south'])
            ):
                element.on_click()

    elif (
        (pos_x > tile_data['max_pixel_west'] and pos_x < tile_data['max_pixel_east']) and
        (pos_y > tile_data['max_pixel_north'] and pos_y < tile_data['max_pixel_south'])
    ):
        # Click was within tile bounds. Calculate clicked tile.
        logger.info('    Is within Tile border bounds.')
        tile_x = int((pos_x - tile_data['max_pixel_west']) / 50)
        tile_y = int((pos_y - tile_data['max_pixel_north']) / 50)
        logger.info('    Found tile is    x: {0}    y: {1}'.format(tile_x, tile_y))

        # Get clicked tile object.
        tile = data_manager.tile_set.tiles[tile_y][tile_x]

        # Check what click type occurred.
        if button_state == 1:
            # Left click.
            logger.info('    Incrementing tile walls.')
            tile.walls.increment_wall_state()

        elif button_state == 2:
            # Middle click.

            # If tile is empty and no trash, generate some.
            if not tile.walls.has_walls and not tile.trashpile.exists:
                tile.trashpile.place()

            # Else if tile is empty and has trash, remove.
            elif tile.trashpile.exists:
                tile.trashpile.clean()

            # Otherwise reset wall state.
            else:
                # Attempt to reset tile to empty.
                # If state is invalid, increment until "original tile starting state" is found.
                logger.info('    Resetting tile wall state.')
                wall_state = 0
                while not tile.walls.validate_wall_state(wall_state):
                    wall_state += 1

                # Found valid state. Assign to tile.
                tile.walls.wall_state = wall_state

        elif button_state == 4:
            # Right click.
            logger.info('    Decrementing tile walls.')
            tile.walls.decrement_wall_state()

# endregion Handler Functions
