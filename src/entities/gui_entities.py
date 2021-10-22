"""
User interface GUI entities that display to the GUI section.

Sprite Depth Values (0 is lowest. Higher values will display ontop of lower ones):
 * Text: 5
 * Button FlatColor: 4
 * Button Border: 3
 * Background Border: 2
 * Background FlatColor: 1
 * Hidden/Unused Sprites: 0
"""

# System Imports.
import sdl2.ext
from sdl2 import SDL_CreateTextureFromSurface, SDL_CreateRenderer, SDL_RENDERER_ACCELERATED
from fclist import fclist, fcmatch
from sdl2.sdlttf import TTF_Init, TTF_OpenFont, TTF_RenderText_Solid

# User Imports.
from src.logging import init_logging


# Initialize logger.
logger = init_logging(__name__)


# # Initialize SDL2_ttf.
# TTF_Init()



class GuiCore:
    """
    Core GUI class. Holds/controls all other gui entities.
    """
    def __init__(self, data_manager):
        self.data_manager = data_manager

        # Initialize object to hold pixel locations of GUI elements.
        self.elements = []

        # Initialize general gui background.
        self.background = GuiBackground(data_manager)

        # Initialize "randomize tile walls" button.
        self.rand_walls = GuiButton(data_manager, 'Randomize Walls', 50, name='RandWalls Button')
        self.elements.append(self.rand_walls)

        # # Initialize "randomize trash piles" button.
        self.rand_trash = GuiButton(data_manager, 'Randomize Trash', 90, name='RandTrash Button')
        self.elements.append(self.rand_trash)


class GuiBackground:
    """
    The general background element for the GUI interface.
    """
    def __init__(self, data_manager):
        self.data_manager = data_manager

        # Initialize background flat color.
        background_color = sdl2.ext.Color(5, 8, 51)  # Hex: #050833
        background_width = data_manager.gui_data['gui_w_end'] - data_manager.gui_data['gui_w_start']
        background_height = data_manager.gui_data['gui_h_end'] - data_manager.gui_data['gui_h_start']
        background_sprite = data_manager.sprite_factory.from_color(
            background_color,
            size=(background_width, background_height),
        )
        self.main = self.GuiBackgroundSprite(data_manager.world, background_sprite, data_manager)

        # Initialize main gui border.
        border_color = sdl2.ext.Color(15, 18, 61)  # Hex: #0f123d
        border_width = 4
        border_height = data_manager.gui_data['gui_h_end'] - data_manager.gui_data['gui_h_start']
        border_sprite = data_manager.sprite_factory.from_color(
            border_color,
            size=(border_width, border_height),
        )
        self.border = self.GuiBorderSprite(
            data_manager.world,
            border_sprite,
            data_manager,
            data_manager.gui_data['gui_w_start'],
            data_manager.gui_data['gui_w_start'] + 3,
        )

        # Initialize gui border highlight.
        border_color = sdl2.ext.Color(25, 28, 71)  # Hex: #191c47
        border_width = 2
        border_height = data_manager.gui_data['gui_h_end'] - data_manager.gui_data['gui_h_start']
        border_sprite = data_manager.sprite_factory.from_color(
            border_color,
            size=(border_width, border_height),
        )
        self.border_highlight = self.GuiBorderSprite(
            data_manager.world,
            border_sprite,
            data_manager,
            data_manager.gui_data['gui_w_start'],
            data_manager.gui_data['gui_w_start'],
        )

    class GuiBackgroundSprite(sdl2.ext.Entity):
        """
        Sprite data for "flat color" gui background element.
        """
        def __init__(self, world, sprite, data_manager):
            # Set entity display image.
            self.sprite = sprite

            # Define world systems which affect entity.
            # None so far.

            # Set entity location tracking.
            self.sprite.position = data_manager.gui_data['gui_w_start'], data_manager.gui_data['gui_h_start']

            # Set entity depth mapping.
            self.sprite.depth = 1

    class GuiBorderSprite(sdl2.ext.Entity):
        """
        Border sprite data for gui background element.
        """
        def __init__(self, world, sprite, data_manager, start_w, end_w):
            # Set entity display image.
            self.sprite = sprite

            # Define world systems which affect entity.
            # None so far.

            # Set entity location tracking.
            if end_w - start_w < 5:
                self.sprite.position = start_w + 1, data_manager.gui_data['gui_h_start']
            else:
                self.sprite.position = start_w, data_manager.gui_data['gui_h_start']

            # Set entity depth mapping.
            self.sprite.depth = 2


class GuiButton:
    """
    A button for the GUI interface.
    """
    def __init__(self, data_manager, text, pos_y, name='Gui Button'):
        self.data_manager = data_manager
        self.name = str(name)

        # Determine bounds of button we're generating. Allows handling on click events.
        background_width = data_manager.gui_data['gui_w_end'] - data_manager.gui_data['gui_w_start'] - 40
        max_pixel_north = pos_y - 2
        max_pixel_east = data_manager.gui_data['gui_w_start'] + 18 + background_width + 2
        max_pixel_south = pos_y + 22
        max_pixel_west = data_manager.gui_data['gui_w_start'] + 18
        self.bounds = {
            'max_pixel_north': max_pixel_north,
            'max_pixel_east': max_pixel_east,
            'max_pixel_south': max_pixel_south,
            'max_pixel_west': max_pixel_west,
        }

        # Set font to system's default monospace font.
        self.font = fcmatch('monospace').file

        # Initialize button flat color.
        background_color = sdl2.ext.Color(236, 237, 248)  # Hex: #ecedf8
        background_width = background_width
        background_height = 20
        background_sprite = data_manager.sprite_factory.from_color(
            background_color,
            size=(background_width, background_height),
        )
        self.main = self.GuiButtonSprite(data_manager.world, background_sprite, data_manager, pos_y)

        # Initialize button border.
        border_color = sdl2.ext.Color(162, 167, 221)  # Hex: #a2a7dd
        border_width = background_width + 4
        border_height = 24
        border_sprite = data_manager.sprite_factory.from_color(
            border_color,
            size=(border_width, border_height),
        )
        self.border = self.GuiButtonBorderSprite(
            data_manager.world,
            border_sprite,
            data_manager,
            pos_y,
        )

        # Initialize button text.
        text_color = sdl2.SDL_Color(0, 0, 0)    # Black text.
        font_manager = sdl2.ext.FontManager(self.font, size=12, color=text_color)
        text_sprite = data_manager.sprite_factory.from_text(text, fontmanager=font_manager)
        pos_x = data_manager.gui_data['gui_w_start'] + 45
        self.GuiButtonText(data_manager.world, text_sprite, data_manager, pos_x, pos_y + 5)

    class GuiButtonSprite(sdl2.ext.Entity):
        """
        Sprite data for gui button "flat color" element.
        """
        def __init__(self, world, sprite, data_manager, pos_y):
            # Set entity display image.
            self.sprite = sprite

            # Define world systems which affect entity.
            # None so far.

            # Set entity location tracking.
            self.sprite.position = data_manager.gui_data['gui_w_start'] + 20, pos_y

            # Set entity depth mapping.
            self.sprite.depth = 4

    class GuiButtonBorderSprite(sdl2.ext.Entity):
        """
        Sprite data for gui button border.
        """
        def __init__(self, world, sprite, data_manager, pos_y):
            # Set entity display image.
            self.sprite = sprite

            # Define world systems which affect entity.
            # None so far.

            # Set entity location tracking.
            self.sprite.position = data_manager.gui_data['gui_w_start'] + 18, pos_y - 2

            # Set entity depth mapping.
            self.sprite.depth = 3

    class GuiButtonText(sdl2.ext.Entity):
        def __init__(self, world, sprite, data_manager, pos_x, pos_y):
            # Set entity display image.
            self.sprite = sprite

            # Define world systems which affect entity.
            # None so far.

            # Set entity location tracking.
            self.sprite.position = pos_x, pos_y

            # Set entity depth mapping.
            self.sprite.depth = 5
