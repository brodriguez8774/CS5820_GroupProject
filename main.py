"""
Virtual roomba/vacuum AI project.
"""

# System Imports.
import sdl2.ext

# User Imports.
from src.entities import Roomba, TileSet
from src.misc import DataManager
from src.systems import MovementSystem, SoftwareRendererSystem


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
    data_manager, roomba = initialize_data()
    world = data_manager.world
    sprite_renderer = data_manager.sprite_renderer

    # Initialize subsystems of world manager.
    movement = MovementSystem(data_manager, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    # Add subsystems to world manager.
    world.add_system(movement)
    world.add_system(sprite_renderer)

    # Initialize sprites.
    # sprite_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    # roomba_sprite = sprite_factory.from_image(RESOURCES.get_path('roomba.png'))
    #
    # roomba = Roomba(world, roomba_sprite, 125, 125)

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

            # Handle for key up.
            if event.type == sdl2.SDL_KEYDOWN:

                if event.key.keysym.sym in [sdl2.SDLK_UP, sdl2.SDLK_w]:
                    roomba.movement.north = True

                elif event.key.keysym.sym in [sdl2.SDLK_RIGHT, sdl2.SDLK_d]:
                    roomba.movement.east = True

                elif event.key.keysym.sym in [sdl2.SDLK_DOWN, sdl2.SDLK_s]:
                    roomba.movement.south = True

                elif event.key.keysym.sym in [sdl2.SDLK_LEFT, sdl2.SDLK_a]:
                    roomba.movement.west = True

        # Update render window.
        world.process()

    # Call final library teardown logic.
    sdl2.ext.quit()


def initialize_data():
    """
    Initializes data for program start.
    :return: (DataManager object with all starting data, Roomba/Vacuum object).
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
    print('\n\n')
    print('window_data[total_pixel_w]: {0}'.format(window_data['total_pixel_w']))
    print('window_data[total_pixel_h]: {0}'.format(window_data['total_pixel_h']))
    print('window_data[center_pixel_w]: {0}'.format(window_data['center_pixel_w']))
    print('window_data[center_pixel_h]: {0}'.format(window_data['center_pixel_h']))
    print('sprite_data[sprite_w_count]: {0}'.format(sprite_data['sprite_w_count']))
    print('sprite_data[sprite_h_count]: {0}'.format(sprite_data['sprite_h_count']))
    print('sprite_data[max_pixel_north]: {0}'.format(sprite_data['max_pixel_north']))
    print('sprite_data[max_pixel_east]: {0}'.format(sprite_data['max_pixel_east']))
    print('sprite_data[max_pixel_south]: {0}'.format(sprite_data['max_pixel_south']))
    print('sprite_data[max_pixel_west]: {0}'.format(sprite_data['max_pixel_west']))
    print('\n\n')

    # Initialize data manager object.
    data_manager = DataManager(world, window, sprite_factory, sprite_renderer, window_data, sprite_data)

    # # Initialize roomba object.
    # roomba = Roomba(data_manager.world, data_manager, 0, 0)
    roomba_sprite = sprite_factory.from_image(RESOURCES.get_path('roomba.png'))
    roomba = Roomba(world, roomba_sprite, data_manager, 0, 0)

    # Generate all sprite tiles.
    TileSet(data_manager, roomba)

    # Return generated window object.
    return data_manager, roomba


if __name__ == '__main__':
    print('Starting program.')

    main()

    print('Terminating program.')
