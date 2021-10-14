"""
Virtual roomba/vacuum AI project.
"""

# System Imports.
import sdl2.ext

# User Imports.
from src.tiles import TileSet


# Module Variables.
# Initialize window width/height.
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480


def main():
    """
    Project start.
    """
    # Initialize sdl2 library.
    sdl2.ext.init()

    # Initialize sprite factory, which is what draws our images (aka "sprites") to window.
    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

    # Initialize window and basic sprites.
    window = initialize_window(factory)

    # Force program to wait, so we actually see output.
    processor = sdl2.ext.TestEventProcessor()
    processor.run(window)

    # Call final library teardown logic.
    sdl2.ext.quit()


def initialize_window(factory):
    """
    Initializes render window for user.
    :param factory: SpriteFactory object which renders sprites to window.
    :return: Initialized window.
    """
    # Initialize render window.
    window = sdl2.ext.Window('CS 5820 - Virtual Roomba/Vacuum AI Project', size=(WINDOW_WIDTH, WINDOW_HEIGHT))
    window.show()

    # Create sprite renderer factory.
    sprite_renderer = factory.create_sprite_render_system(window)

    # Calculate sprite counts to fit into rendered window.
    window_center_w = int(WINDOW_WIDTH / 2)
    window_center_h = int(WINDOW_HEIGHT / 2)
    sprite_w_count = int(WINDOW_WIDTH / 50) - 1
    sprite_h_count = int(WINDOW_HEIGHT / 50) - 1
    sprite_w_start = int(window_center_w - (int(sprite_w_count / 2) * 50))
    sprite_h_start = int(window_center_h - (int(sprite_h_count / 2) * 50))
    sprite_w_end = int(window_center_w + (int(sprite_w_count / 2) * 50))
    sprite_h_end = int(window_center_h + (int(sprite_h_count / 2) * 50))

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
        'max_pixel_top': sprite_h_start,
        'max_pixel_right': sprite_w_end,
        'max_pixel_bottom': sprite_h_end,
        'max_pixel_left': sprite_w_start,
    }
    print('\n\n')
    print('window_data[total_pixel_w]: {0}'.format(window_data['total_pixel_w']))
    print('window_data[total_pixel_h]: {0}'.format(window_data['total_pixel_h']))
    print('window_data[center_pixel_w]: {0}'.format(window_data['center_pixel_w']))
    print('window_data[center_pixel_h]: {0}'.format(window_data['center_pixel_h']))
    print('sprite_data[sprite_w_count]: {0}'.format(sprite_data['sprite_w_count']))
    print('sprite_data[sprite_h_count]: {0}'.format(sprite_data['sprite_h_count']))
    print('sprite_data[max_pixel_top]: {0}'.format(sprite_data['max_pixel_top']))
    print('sprite_data[max_pixel_right]: {0}'.format(sprite_data['max_pixel_right']))
    print('sprite_data[max_pixel_bottom]: {0}'.format(sprite_data['max_pixel_bottom']))
    print('sprite_data[max_pixel_left]: {0}'.format(sprite_data['max_pixel_left']))
    print('\n\n')

    # Generate all sprite tiles.
    TileSet(factory, sprite_renderer, window_data, sprite_data)

    # Return generated window object.
    return window


if __name__ == '__main__':
    print('Starting program.')

    main()

    print('Terminating program.')

