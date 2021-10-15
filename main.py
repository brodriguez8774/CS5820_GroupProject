"""
Virtual roomba/vacuum AI project.
"""

# System Imports.
import sdl2.ext

# User Imports.
from src.entities import Roomba
from src.tiles import TileSet


# Module Variables.
# Initialize window width/height.
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480


class SoftwareRenderSystem(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super().__init__(window)

    def render(self, components):
        # sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super().render(components)

    def process(self, world, components):
        """

        :param world:
        :param components:
        :return:
        """
        # print('processing things!')
        # for sprite in components:
        #     print('sprite: "{0}"'.format(sprite))
        # import time
        # time.sleep(5)



def main():
    """
    Project start.
    """
    # Initialize sdl2 library.
    sdl2.ext.init()

    # Initialize sprite factory, which is what draws our images (aka "sprites") to window.
    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

    # Initialize render window and basic background sprites.
    window, sprite_renderer, roomba = initialize_window(factory)

    # Initialize "world". This appears to be what does most of the work "behind the scenes" for the SDL2 library.
    world = sdl2.ext.World()

    # Initialize "world data tracking" for SDL2 library.
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

            # Handle for key up.
            if event.type == sdl2.SDL_KEYDOWN:

                if event.key.keysym.sym in [sdl2.SDLK_UP, sdl2.SDLK_w]:
                    roomba.move_up()

                elif event.key.keysym.sym in [sdl2.SDLK_RIGHT, sdl2.SDLK_d]:
                    roomba.move_right()

                elif event.key.keysym.sym in [sdl2.SDLK_DOWN, sdl2.SDLK_s]:
                    roomba.move_down()

                elif event.key.keysym.sym in [sdl2.SDLK_LEFT, sdl2.SDLK_a]:
                    roomba.move_left()

        # Update render window.
        world.process()
        # window.refresh()

    # Call final library teardown logic.
    sdl2.ext.quit()


def initialize_window(sprite_factory):
    """
    Initializes render window for user.
    :param sprite_factory: SpriteFactory object which renders sprites to window.
    :return: Initialized window.
    """
    # Initialize render window.
    window = sdl2.ext.Window('CS 5820 - Virtual Roomba/Vacuum AI Project', size=(WINDOW_WIDTH, WINDOW_HEIGHT))
    window.show()

    # Create sprite renderer factory.
    sprite_renderer = SoftwareRenderSystem(window)
    # sprite_renderer = factory.create_sprite_render_system(window)

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

    # Initialize roomba object.
    roomba = Roomba(sprite_factory, sprite_renderer, sprite_data, 0, 0)

    # Generate all sprite tiles.
    TileSet(sprite_factory, sprite_renderer, window_data, sprite_data, roomba)

    # Return generated window object.
    return window, sprite_renderer, roomba


if __name__ == '__main__':
    print('Starting program.')

    main()

    print('Terminating program.')

