"""
Virtual roomba/vacuum AI project.
"""

# System Imports.
import sys
import sdl2.ext


# Module Variables.
# Here, we point to our image files to render to user.
RESOURCES = sdl2.ext.Resources(__file__, 'src/images/')
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
    window = sdl2.ext.Window("Hello World!", size=(WINDOW_WIDTH, WINDOW_HEIGHT))
    window.show()

    # Initialize sprite factory, which is what draws our images (aka "sprites") to window.
    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

    # Create single "sprite" to display.
    sprite_background = factory.from_image(RESOURCES.get_path('background.png'))

    # Display sprites to window.
    spriterenderer = factory.create_sprite_render_system(window)
    spriterenderer.render(sprite_background)

    # Force program to wait, so we actually see output.
    processor = sdl2.ext.TestEventProcessor()
    processor.run(window)

    # Call final library teardown logic.
    sdl2.ext.quit()


if __name__ == '__main__':
    print('Starting program.')

    main()

    print('Terminating program.')

