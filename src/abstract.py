"""

"""

# System Imports.
import sdl2.ext
from abc import ABC, abstractmethod


# Module Variables.
# Here, we point to our image files to render to user.
RESOURCES = sdl2.ext.Resources(__file__, './images/')


class DataManager:
    """
    Stores and manages general data, to minimize values needing to be passed back and forth between classes.
    """
    def __init__(self, world, window, sprite_factory, sprite_renderer, window_data, sprite_data):
        self.world = world
        self.window = window
        self.sprite_factory = sprite_factory
        self.sprite_renderer = sprite_renderer
        self.window_data = window_data
        self.sprite_data = sprite_data


class BaseEntity(ABC):
    """
    Base object class for universal handling/managing of tile/object display.
    All entity objects should inherit from this, both static and dynamic.
    """
    @abstractmethod
    def __init__(self, data_manager, tile_x_pos, tile_y_pos, sprite=None):
        print('tile_x_pos: {0}'.format(tile_x_pos))
        print('tile_y_pos: {0}'.format(tile_y_pos))
        print('sprite: "{0}"'.format(sprite))

        if sprite is None:
            raise ValueError('Sprite name must be provided.')

        # Initialize class variables.
        self.sprite_factory = data_manager.sprite_factory
        self.sprite_renderer = data_manager.sprite_renderer
        self.sprite_data = data_manager.sprite_data
        self.sprite = sprite
        self._tile_position = (0, 0)    # Position in regards to tile x/y index. Each tile is 50 px.
        self._pix_position = (0, 0)     # Position in regards to literal pixel location, in window.
        self.position = (0, 0)          # Same as "_pix_position", but renamed for SDL2 library.

        # Get proper sprite object, if not already.
        if not isinstance(sprite, sdl2.ext.Sprite):
            self.sprite = self.sprite_factory.from_image(RESOURCES.get_path(sprite))

        # Set starting position.
        self.set_position(tile_x_pos, tile_y_pos)

        # Display initial sprite position.
        self.render_sprite()

    @property
    def tile_position(self):
        return self.tile_position

    @tile_position.setter
    def tile_position(self, value):
        # Validate provided value.
        print('tile_position value: {0}'.format(value))
        if not isinstance(value, list) and not isinstance(value, tuple):
            raise TypeError('Variable "tile_position" must be an array.')
        if not len(value) == 2:
            raise ValueError('Variable "tile_position" must have an "x value" and "y value".')
        if not isinstance(value[0], int) or not isinstance(value[1], int):
            raise ValueError('Variable "tile_position" must have integers for x and y values.')

        # Save new value.
        self._tile_position = value

        # Calculate new pixel positions, to match updated tile positions.
        # Calculation based on tile position, plus sprite data dict.
        pix_x_pos = (self._tile_position[0] * 50) + self.sprite_data['max_pixel_left']
        pix_y_pos = (self._tile_position[1] * 50) + self.sprite_data['max_pixel_top']
        self._pix_position = pix_x_pos, pix_y_pos

    @property
    def pix_position(self):
        return self._pix_position

    @pix_position.setter
    def pix_position(self, value):
        # Validate provided value.
        print('pix_position value: {0}'.format(value))
        if not isinstance(value, list) and not isinstance(value, tuple):
            raise TypeError('Variable "pix_position" must be an array.')
        if not len(value) == 2:
            raise ValueError('Variable "pix_position" must have an "x value" and "y value".')
        if not isinstance(value[0], int) or not isinstance(value[1], int):
            raise ValueError('Variable "pix_position" must have integers for x and y values.')

        # Save new value.
        self._pix_position = value

        # Also update expected value for SDL2 library.
        self.sprite.position = self._pix_position

    def set_position(self, tile_x_pos, tile_y_pos):
        """
        Sets entity position.
        Should only be used on entity initialization.

        To move an entity after initialization, call the below move functions.
        :param tile_x_pos: Entity "x" dimension tile index.
        :param tile_y_pos: Entity "y" dimension tile index.
        """
        self.tile_position = tile_x_pos, tile_y_pos

    def render_sprite(self):
        """
        Renders sprite to window at indicated pixel position.
        """
        self.sprite.x = self.pix_position[0]
        self.sprite.y = self.pix_position[1]
        self.sprite_renderer.render(self.sprite)

    def move_up(self):
        """
        Moves entity upward one tile.
        """
        # Update tile position.
        old_tile_position = self._tile_position
        self._tile_position = (self._tile_position[0], (self._tile_position[1] + 1))

        # Update pixel position.
        old_pix_position = self._pix_position
        self._pix_position = (self._pix_position[0], (self._pix_position[1] + 50))

        print('Pressed "up"')
        print('    new_tile_pos: {0}    new_pix_pos:  {1}'.format(self._tile_position, self._pix_position))
        # print('    old_tile_pos: {0}    new_tile_pos: {1}'.format(old_tile_position, self._tile_position))
        # print('    old_pix_pos:  {0}    new_pix_pos:  {1}'.format(old_pix_position, self._pix_position))

    def move_right(self):
        """
        Moves entity right one tile.
        """
        # Update tile position.
        old_tile_position = self._tile_position
        self._tile_position = ((self._tile_position[0] + 1), self._tile_position[1])

        # Update pixel position.
        old_pix_position = self._pix_position
        self._pix_position = ((self._pix_position[0] + 50), self._pix_position[1])

        print('Pressed "right"')
        print('    new_tile_pos: {0}    new_pix_pos:  {1}'.format(self._tile_position, self._pix_position))
        # print('    old_tile_pos: {0}    new_tile_pos: {1}'.format(old_tile_position, self._tile_position))
        # print('    old_pix_pos:  {0}    new_pix_pos:  {1}'.format(old_pix_position, self._pix_position))

    def move_down(self):
        """
        Moves entity down one tile.
        """
        # Update tile position.
        old_tile_position = self._tile_position
        self._tile_position = (self._tile_position[0], (self._tile_position[1] - 1))

        # Update pixel position.
        old_pix_position = self._pix_position
        self._pix_position = (self._pix_position[0], (self._pix_position[1] - 50))

        print('Pressed "down"')
        print('    new_tile_pos: {0}    new_pix_pos:  {1}'.format(self._tile_position, self._pix_position))
        # print('    old_tile_pos: {0}    new_tile_pos: {1}'.format(old_tile_position, self._tile_position))
        # print('    old_pix_pos:  {0}    new_pix_pos:  {1}'.format(old_pix_position, self._pix_position))

    def move_left(self):
        """
        Moves entity left one tile.
        """
        # Update tile position.
        old_tile_position = self._tile_position
        self._tile_position = ((self._tile_position[0] - 1), self._tile_position[1])

        # Update pixel position.
        old_pix_position = self._pix_position
        self._pix_position = ((self._pix_position[0] - 50), self._pix_position[1])

        print('Pressed "left"')
        print('    new_tile_pos: {0}    new_pix_pos:  {1}'.format(self._tile_position, self._pix_position))
        # print('    old_tile_pos: {0}    new_tile_pos: {1}'.format(old_tile_position, self._tile_position))
        # print('    old_pix_pos:  {0}    new_pix_pos:  {1}'.format(old_pix_position, self._pix_position))
