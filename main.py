"""
Virtual roomba/vacuum AI project.
"""

# System Imports.
import ctypes
import sdl2.ext

# User Imports.
from src.entities import Roomba, TileSet
from src.logging import init_logging
from src.misc import DataManager, handle_key_press, handle_mouse_click
from src.systems import AISystem, MovementSystem, SoftwareRendererSystem


# Initialize logger.
logger = init_logging(__name__)


# Module Variables.
# Here, we point to our image files to render to user.
RESOURCES = sdl2.ext.Resources(__file__, './src/images/')
# Initialize window width/height.
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480


def main():
    """
    Project start.
    """
    # Initialize sdl2 library.
    sdl2.ext.init()

    # Initialize general program data to data manager object.
    data_manager = initialize_data()
    world = data_manager.world
    sprite_renderer = data_manager.sprite_renderer

    # Initialize subsystems of world manager.
    ai = AISystem(data_manager, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    movement = MovementSystem(data_manager, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    # Add subsystems to world manager.
    # world.add_system(ai)
    world.add_system(movement)
    world.add_system(sprite_renderer)

    # Run program loop.
    run_program = True
    while run_program:

        # Special handling for any events.
        events = sdl2.ext.get_events()
        for event in events:

            # Handle for exiting program.
            if event.type == sdl2.SDL_QUIT:
                run_program = False
                break

            # Handle for mouse click.
            if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                logger.debug('Mouse button clicked.')

                # Get mouse click (x, y) coordinate position.
                pos_x, pos_y = ctypes.c_int(0), ctypes.c_int(0)
                button_state = sdl2.mouse.SDL_GetMouseState(ctypes.byref(pos_x), ctypes.byref(pos_y))

                # Handle click for location.
                handle_mouse_click(data_manager, button_state, pos_x.value, pos_y.value)

            # Handle for key press.
            if event.type == sdl2.SDL_KEYDOWN:
                logger.debug('Key button pressed.')
                handle_key_press(data_manager, event)

        # Update render window.
        world.process()

        # Wait slightly until next tick.
        sdl2.SDL_Delay(10)

    # Call final library teardown logic.
    sdl2.ext.quit()


def initialize_data():
    """
    Initializes data for program start.
    :return: "Data Manager" data structure object. Consolidates useful program data to one location.
    """
    # Initialize render window.
    window = sdl2.ext.Window('CS 5820 - Virtual Roomba/Vacuum AI Project', size=(WINDOW_WIDTH, WINDOW_HEIGHT))
    window.show()

    # Initialize "world" manager object.
    # This appears to be what does most of the work "behind the scenes" for the SDL2 library.
    world = sdl2.ext.World()

    # Initialize sprite factory, which is what generates our sprite objects.
    sprite_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

    # Create sprite renderer, which is what draws our images (aka "sprites") to window.
    sprite_renderer = SoftwareRendererSystem(window)

    # Calculate sprite counts to fit into rendered window.
    window_center_w = int(WINDOW_WIDTH / 2)
    window_center_h = int(WINDOW_HEIGHT / 2)
    sprite_w_count = int(WINDOW_WIDTH / 50) - 1
    sprite_h_count = int(WINDOW_HEIGHT / 50) - 1
    sprite_w_start = int(window_center_w - (int(sprite_w_count / 2) * 50))
    sprite_h_start = int(window_center_h - (int(sprite_h_count / 2) * 50))
    sprite_w_end = int(window_center_w + (int(sprite_w_count / 2) * 50))
    sprite_h_end = int(window_center_h + (int(sprite_h_count / 2) * 50))
    # Account for calculations being off for certain resolutions.
    if (WINDOW_WIDTH % 100) < 50:
        sprite_w_end += 50
    if (WINDOW_HEIGHT % 100) < 50:
        sprite_h_end += 50

    # Correct spacing if width sprite count is odd number.
    if (sprite_w_count % 2) == 1:
        sprite_w_start -= 25
        sprite_w_end -= 25

    # Correct spacing if height sprite count is odd number.
    if (sprite_h_count % 2) == 1:
        sprite_h_start -= 25
        sprite_h_end -= 25

    # Generate data structure dictionaries.
    window_data = {
        'total_pixel_w': WINDOW_WIDTH,
        'total_pixel_h': WINDOW_HEIGHT,
        'center_pixel_w': window_center_w,
        'center_pixel_h': window_center_h,
    }
    sprite_data = {
        'sprite_w_count': sprite_w_count,
        'sprite_h_count': sprite_h_count,
        'max_pixel_north': sprite_h_start,
        'max_pixel_east': sprite_w_end,
        'max_pixel_south': sprite_h_end,
        'max_pixel_west': sprite_w_start,
    }
    logger.info('')
    logger.info('')
    logger.info('window_data[total_pixel_w]: {0}'.format(window_data['total_pixel_w']))
    logger.info('window_data[total_pixel_h]: {0}'.format(window_data['total_pixel_h']))
    logger.info('window_data[center_pixel_w]: {0}'.format(window_data['center_pixel_w']))
    logger.info('window_data[center_pixel_h]: {0}'.format(window_data['center_pixel_h']))
    logger.info('sprite_data[sprite_w_count]: {0}'.format(sprite_data['sprite_w_count']))
    logger.info('sprite_data[sprite_h_count]: {0}'.format(sprite_data['sprite_h_count']))
    logger.info('sprite_data[max_pixel_north]: {0}'.format(sprite_data['max_pixel_north']))
    logger.info('sprite_data[max_pixel_east]: {0}'.format(sprite_data['max_pixel_east']))
    logger.info('sprite_data[max_pixel_south]: {0}'.format(sprite_data['max_pixel_south']))
    logger.info('sprite_data[max_pixel_west]: {0}'.format(sprite_data['max_pixel_west']))
    logger.info('')
    logger.info('')

    # Initialize data manager object.
    data_manager = DataManager(world, window, sprite_factory, sprite_renderer, window_data, sprite_data)

    # Initialize roomba object.
    roomba_sprite = sprite_factory.from_image(RESOURCES.get_path('roomba.png'))
    data_manager.roomba = Roomba(world, roomba_sprite, data_manager, 0, 0)

    # Generate all sprite tiles.
    data_manager.tile_set = TileSet(data_manager)

    # Return generated window object.
    return data_manager


if __name__ == '__main__':
    logger.info('Starting program.')

    main()

    logger.info('Terminating program.')
