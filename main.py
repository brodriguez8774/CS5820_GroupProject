"""
Virtual roomba/vacuum AI project.
"""

# System Imports.
import sdl2.ext

# User Imports.
from src.entities import Roomba
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

    # Initialize render window.
    window = sdl2.ext.Window('CS 5820 - Virtual Roomba/Vacuum AI Project', size=(WINDOW_WIDTH, WINDOW_HEIGHT))
    window.show()

    # Initialize "world" manager object.
    world = sdl2.ext.World()

    # Initialize subsystems of world manager.
    movement = MovementSystem(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    spriterenderer = SoftwareRendererSystem(window)

    # Add subsystems to world manager.
    world.add_system(movement)
    world.add_system(spriterenderer)

    # Initialize sprites.
    sprite_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    roomba_sprite = sprite_factory.from_image(RESOURCES.get_path('roomba.png'))

    roomba = Roomba(world, roomba_sprite, 125, 125)

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


if __name__ == '__main__':
    print('Starting program.')

    main()

    print('Terminating program.')
