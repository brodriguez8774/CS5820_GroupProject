"""
User interface GUI entities that display to the GUI section.

Sprite Depth Values (0 is lowest. Higher values will display ontop of lower ones):
 * Buttons: 3
 * Border: 2
 * Background: 1
 * Hidden/Unused Sprites: 0
"""

# System Imports.
import sdl2.ext


class GuiCore:
    """
    Core GUI class. Holds/controls all other gui entities.
    """
    def __init__(self, data_manager):
        self.data_manager = data_manager

        # Initialize gui background.
        background_color = sdl2.ext.Color(5, 8, 51)     # Hex: #050833
        background_width = data_manager.gui_data['gui_w_end'] - data_manager.gui_data['gui_w_start']
        background_height = data_manager.gui_data['gui_h_end'] - data_manager.gui_data['gui_h_start']
        background_sprite = data_manager.sprite_factory.from_color(
            background_color,
            size=(background_width, background_height),
        )
        self.background = GuiBackground(data_manager.world, background_sprite, data_manager)

        # Initialize gui border.
        border_color = sdl2.ext.Color(15, 18, 61)  # Hex: #0f123d
        border_width = 4
        border_height = data_manager.gui_data['gui_h_end'] - data_manager.gui_data['gui_h_start']
        border_sprite = data_manager.sprite_factory.from_color(
            border_color,
            size=(border_width, border_height),
        )
        GuiBorder(
            data_manager.world,
            border_sprite,
            data_manager,
            data_manager.gui_data['gui_w_start'],
            data_manager.gui_data['gui_w_start'] + 3,
        )
        border_color = sdl2.ext.Color(25, 28, 71)  # Hex: #191c47
        border_width = 2
        border_height = data_manager.gui_data['gui_h_end'] - data_manager.gui_data['gui_h_start']
        border_sprite = data_manager.sprite_factory.from_color(
            border_color,
            size=(border_width, border_height),
        )
        GuiBorder(
            data_manager.world,
            border_sprite,
            data_manager,
            data_manager.gui_data['gui_w_start'],
            data_manager.gui_data['gui_w_start'],
        )


class GuiBackground(sdl2.ext.Entity):
    """
    The general background element for the GUI interface.
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


class GuiBorder(sdl2.ext.Entity):
    """
    Border part of general gui background element.
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
