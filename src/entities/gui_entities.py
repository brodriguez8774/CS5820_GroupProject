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
from fclist import fcmatch

# User Imports.
from src.logging import init_logging
from src.misc import (
    set_roomba_vision_range_0,
    set_roomba_vision_range_1,
    set_roomba_vision_range_2,
    set_roomba_vision_range_full,
    toggle_roomba_ai,
    toggle_roomba_failure,
)


# Initialize logger.
logger = init_logging(__name__)


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

        # Initialize GUI text.
        self.optimal_counter_text = GuiText(
            data_manager,
            'Optimal Solution Cost:',
            5,
            data_manager.gui_data['gui_h_start'] + 5,
        )
        self.total_move_counter_text = GuiText(
            data_manager,
            'Moves:',
            data_manager.gui_data['gui_w_start'] - 80,
            data_manager.gui_data['gui_h_start'] + 5,
        )
        self.ai_setting_text = GuiText(
            data_manager,
            'AI Setting:',
            5,
            data_manager.gui_data['gui_h_end'] - 25,
        )
        self.ai_failure_text = GuiText(
            data_manager,
            'Failure Chance: 0%',
            data_manager.gui_data['gui_w_start'] - 150,
            data_manager.gui_data['gui_h_end'] - 25,
        )
        self.settings_header_text = GuiText(
            data_manager,
            'Settings:',
            data_manager.gui_data['gui_w_start'] + 10,
            data_manager.gui_data['gui_h_start'] + 5,
        )
        self.randomizer_header_text = GuiText(
            data_manager,
            'Randomizers:',
            data_manager.gui_data['gui_w_start'] + 10,
            data_manager.gui_data['gui_h_start'] + 115,
        )
        self.roomba_header_text = GuiText(
            data_manager,
            'Roomba Settings:',
            data_manager.gui_data['gui_w_start'] + 10,
            data_manager.gui_data['gui_h_start'] + 280,
        )

        # Initialize "toggle ai" button.
        self.toggle_ai = GuiButton(
            data_manager,
            'Toggle AI',
            30,
            name='Toggle AI',
            function_call=toggle_roomba_ai,
            function_args=data_manager,
        )
        self.elements.append(self.toggle_ai)

        # Initialize "toggle failure" button.
        self.toggle_failure_button = GuiButton(
            data_manager,
            'Toggle Failure',
            70,
            name='Toggle Failure',
            function_call=toggle_roomba_failure,
            function_args=data_manager,
        )
        self.elements.append(self.toggle_failure_button)

        # Initialize "randomize tile walls" buttons.
        self.rand_walls = GuiButton(
            data_manager,
            'Randomize Walls (E)',
            140,
            name='RandWalls Button (Equal Randomization)',
            function_call=data_manager.tile_set.randomize_tile_walls_equal,
        )
        self.elements.append(self.rand_walls)
        self.rand_walls = GuiButton(
            data_manager,
            'Randomize Walls (W)',
            180,
            name='RandWalls Button (Weighted Randomization)',
            function_call=data_manager.tile_set.randomize_tile_walls_weighted,
        )
        self.elements.append(self.rand_walls)

        # Initialize "randomize trash piles" button.
        self.rand_trash = GuiButton(
            data_manager,
            'Randomize Trash',
            220,
            name='RandTrash Button',
            function_call=data_manager.tile_set.randomize_trash,
        )
        self.elements.append(self.rand_trash)

        # Initialize "roomba vision distance of 0" (aka "bump sensor") button.
        self.vision_0 = GuiButton(
            data_manager,
            'Bump Sensor',
            300,
            name='Distance of 0 (Bump Sensor)',
            function_call=set_roomba_vision_range_0,
            function_args=data_manager,
        )
        self.elements.append(self.vision_0)

        # Initialize "roomba vision distance of 1" button.
        self.vision_1 = GuiButton(
            data_manager,
            'Distance of 1',
            340,
            name='Distance of 1',
            function_call=set_roomba_vision_range_1,
            function_args=data_manager,
        )
        self.elements.append(self.vision_1)

        # Initialize "roomba vision distance of 2" button.
        self.vision_2 = GuiButton(
            data_manager,
            'Distance of 2',
            380,
            name='Distance of 2',
            function_call=set_roomba_vision_range_2,
            function_args=data_manager,
        )
        self.elements.append(self.vision_2)

        # Initialize "roomba vision distance of 'all seeing'" button.
        self.vision_full = GuiButton(
            data_manager,
            'Full Sight',
            420,
            name='Full Sight',
            function_call=set_roomba_vision_range_full,
            function_args=data_manager,
        )
        self.elements.append(self.vision_full)


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


class GuiText:
    """
    Text for the GUI interface.
    """
    def __init__(self, data_manager, text, pos_x, pos_y):
        self.data_manager = data_manager
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.text_entity = None

        # Set font to system's default monospace font.
        self.font = fcmatch('monospace').file

        # Initialize text sprite.
        self.update(text)

    def update(self, text):
        """
        Update's text entity to display new text value.
        :param text: Text string to display.
        """
        # Remove previous text entity, if there is one.
        if self.text_entity:
            self.text_entity.delete()

        # Initialize button text.
        text_color = sdl2.SDL_Color(250, 250, 250)  # White text.
        font_manager = sdl2.ext.FontManager(self.font, size=12, color=text_color)
        text_sprite = self.data_manager.sprite_factory.from_text(str(text), fontmanager=font_manager)

        # Create sprite entity to display text value.
        self.text_entity = self.Text(self.data_manager.world, text_sprite, self.data_manager, self.pos_x, self.pos_y)

    class Text(sdl2.ext.Entity):
        def __init__(self, world, sprite, data_manager, pos_x, pos_y):
            # Set entity display image.
            self.sprite = sprite

            # Define world systems which affect entity.
            # None so far.

            # Set entity location tracking.
            self.sprite.position = pos_x, pos_y

            # Set entity depth mapping.
            self.sprite.depth = 5


class GuiButton:
    """
    A button for the GUI interface.
    """
    def __init__(self, data_manager, text, pos_y, name='Gui Button', function_call=None, function_args=None):
        self.data_manager = data_manager
        self.name = str(name)
        self.function_call = function_call
        if function_args is None:
            self.function_args = None
        else:
            if isinstance(function_args, list) or isinstance(function_args, tuple):
                self.function_args = function_args
            else:
                self.function_args = [function_args]

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

    def on_click(self):
        """
        Calls associated class function.
        Allows external logic (such as main event loop) to trigger expected button press logic, on click.
        :return: Corresponding return value for bound function call.
        """
        logger.info('    Clicked button "{0}":'.format(self.name))

        if self.function_call is None:
            raise RuntimeError('Button does not have a bound function call!')

        if self.function_args:
            return self.function_call(*self.function_args)
        else:
            return self.function_call()

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
