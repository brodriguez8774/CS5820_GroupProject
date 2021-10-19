"""
System entities that hold general system/world data in some manner.
"""

# System Imports.
import sdl2.ext

# User Imports.


# Module Variables.
# Here, we point to our image files to render to user.
RESOURCES = sdl2.ext.Resources(__file__, '../images/')


class Movement:
    """
    Holds movement tick data for an entity.
    """
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.north = False
        self.east = False
        self.south = False
        self.west = False

    def calculate_pix_from_tile(self, tile_x, tile_y):
        """
        Computes the corresponding pixel location for the provided tile grid coordinates.
        :param tile_x: Tile column (x-axis) of entity.
        :param tile_y: Tile row (y-axis) of entity.
        :return: Corresponding (x,y) pixel grid coordinates that match tile location.
        """
        pos_x = (tile_x * 50) + self.data_manager.sprite_data['max_pixel_west']
        pos_y = (tile_y * 50) + self.data_manager.sprite_data['max_pixel_north']

        # Return calculated pixel coordinates.
        return pos_x, pos_y


class Walls:
    """
    Holds tile wall data for a "tile" entity.
    """
    def __init__(self, data_manager, tile_x, tile_y, wall_data):
        self.data_manager = data_manager
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.walls = wall_data

        # Handle for edge tile walls. These walls should unconditionally display.
        self.has_walls = False
        self._wall_state = 0
        self._wall_state_max = 14
        self._has_wall_north = False
        self._has_wall_east = False
        self._has_wall_south = False
        self._has_wall_west = False
        if tile_y == 0:
            # Set north (upper) wall to active.
            self.has_wall_north = True

        if tile_x == (data_manager.sprite_data['sprite_w_count'] - 1):
            # Set east (right) wall to active.
            self.has_wall_east = True

        if tile_y == (data_manager.sprite_data['sprite_h_count'] - 1):
            # Set south (lower) wall to active.
            self.has_wall_south = True

        if tile_x == 0:
            # Set west (left) wall to active.
            self.has_wall_west = True

    def increment_wall_state(self):
        """
        Increases wall state counter.
        Ensures walls update in predictable order.
        """
        wall_state = self.wall_state + 1

        # Verify state is still valid value.
        if wall_state > self._wall_state_max:
            wall_state = 0

        # Save value to class.
        self.wall_state = wall_state

    def decriment_wall_state(self):
        """
        Decreases wall state counter.
        Ensures walls update in predictable order.
        """
        wall_state = self.wall_state - 1

        # Verify state is still valid value.
        if wall_state < 0:
            wall_state = self._wall_state_max

        # Save value to class.
        self.wall_state = wall_state

    @property
    def wall_state(self):
        return self._wall_state

    @wall_state.setter
    def wall_state(self, value):
        # Verify is int.
        if not isinstance(value, int):
            raise TypeError('Variable "wall_state" must be an integer.')
        elif value < 0 or value > self._wall_state_max:
            raise ValueError('Variable "wall_state" must be between 0 and {0}. Was {1}.'.format(
                self._wall_state_max,
                value,
            ))

        self._wall_state = value

        # Update internal wall data, based on state.
        if value == 0:
            # Set all walls to inactive.
            self.has_wall_north = False
            self.has_wall_east = False
            self.has_wall_south = False
            self.has_wall_west = False

        elif value == 1:
            # Set only north wall to active.
            self.has_wall_north = True
            self.has_wall_east = False
            self.has_wall_south = False
            self.has_wall_west = False

        elif value == 2:
            # Set only east wall to active.
            self.has_wall_north = False
            self.has_wall_east = True
            self.has_wall_south = False
            self.has_wall_west = False

        elif value == 3:
            # Set only south wall to active.
            self.has_wall_north = False
            self.has_wall_east = False
            self.has_wall_south = True
            self.has_wall_west = False

        elif value == 4:
            # Set only west wall to active.
            self.has_wall_north = False
            self.has_wall_east = False
            self.has_wall_south = False
            self.has_wall_west = True

        elif value == 5:
            # Set north and east walls to active.
            self.has_wall_north = True
            self.has_wall_east = True
            self.has_wall_south = False
            self.has_wall_west = False

        elif value == 6:
            # Set north and south walls to active.
            self.has_wall_north = True
            self.has_wall_east = False
            self.has_wall_south = True
            self.has_wall_west = False

        elif value == 7:
            # Set north and west walls to active.
            self.has_wall_north = True
            self.has_wall_east = False
            self.has_wall_south = False
            self.has_wall_west = True

        elif value == 8:
            # Set east and south walls to active.
            self.has_wall_north = False
            self.has_wall_east = True
            self.has_wall_south = True
            self.has_wall_west = False

        elif value == 9:
            # Set east and west walls to active.
            self.has_wall_north = False
            self.has_wall_east = True
            self.has_wall_south = False
            self.has_wall_west = True

        elif value == 10:
            # Set south and west walls to active.
            self.has_wall_north = False
            self.has_wall_east = False
            self.has_wall_south = True
            self.has_wall_west = True

        elif value == 11:
            # Set all except north to active.
            self.has_wall_north = False
            self.has_wall_east = True
            self.has_wall_south = True
            self.has_wall_west = True

        elif value == 12:
            # Set all except east to active.
            self.has_wall_north = True
            self.has_wall_east = False
            self.has_wall_south = True
            self.has_wall_west = True

        elif value == 13:
            # Set all except south to active.
            self.has_wall_north = True
            self.has_wall_east = True
            self.has_wall_south = False
            self.has_wall_west = True

        elif value == 14:
            # Set all except west to active.
            self.has_wall_north = True
            self.has_wall_east = True
            self.has_wall_south = True
            self.has_wall_west = False

    @property
    def has_wall_north(self):
        return self._has_wall_north

    @has_wall_north.setter
    def has_wall_north(self, value):
        # Validate passed value.
        if not isinstance(value, bool):
            raise TypeError('Must be boolean.')

        # Handle value.
        if value:
            # Setting to True.

            # Update wall displaying/rendering.
            self.walls['north'].sprite.depth = 2

            # Update tile management variables.
            self.has_walls = True
            self._has_wall_north = True

        else:
            # Setting to False.

            # Update wall displaying/rendering.
            self.walls['north'].sprite.depth = 0

            # Update tile management variables.
            self._has_wall_north = False
            if (
                not self.has_wall_north and
                not self.has_wall_east and
                not self.has_wall_south and
                not self.has_wall_west
            ):
                self.has_walls = False

    @property
    def has_wall_east(self):
        return self._has_wall_east

    @has_wall_east.setter
    def has_wall_east(self, value):
        # Validate passed value.
        if not isinstance(value, bool):
            raise TypeError('Must be boolean.')

        # Handle value.
        if value:
            # Setting to True.

            # Update wall displaying/rendering.
            self.walls['east'].sprite.depth = 2

            # Update tile management variables.
            self.has_walls = True
            self._has_wall_east = True

        else:
            # Setting to False.

            # Update wall displaying/rendering.
            self.walls['east'].sprite.depth = 0

            # Update tile management variables.
            self._has_wall_east = False
            if (
                not self.has_wall_north and
                not self.has_wall_east and
                not self.has_wall_south and
                not self.has_wall_west
            ):
                self.has_walls = False

    @property
    def has_wall_south(self):
        return self._has_wall_south

    @has_wall_south.setter
    def has_wall_south(self, value):
        # Validate passed value.
        if not isinstance(value, bool):
            raise TypeError('Must be boolean.')

        # Handle value.
        if value:
            # Setting to True.

            # Update wall displaying/rendering.
            self.walls['south'].sprite.depth = 2

            # Update tile management variables.
            self.has_walls = True
            self._has_wall_south = True

        else:
            # Setting to False.

            # Update wall displaying/rendering.
            self.walls['south'].sprite.depth = 0

            # Update tile management variables.
            self._has_wall_south = False
            if (
                not self.has_wall_north and
                not self.has_wall_east and
                not self.has_wall_south and
                not self.has_wall_west
            ):
                self.has_walls = False

    @property
    def has_wall_west(self):
        return self._has_wall_west

    @has_wall_west.setter
    def has_wall_west(self, value):
        # Validate passed value.
        if not isinstance(value, bool):
            raise TypeError('Must be boolean.')

        # Handle value.
        if value:
            # Setting to True.

            # Update wall displaying/rendering.
            self.walls['west'].sprite.depth = 2

            # Update tile management variables.
            self.has_walls = True
            self._has_wall_west = True

        else:
            # Setting to False.

            # Update wall displaying/rendering.
            self.walls['west'].sprite.depth = 0

            # Update tile management variables.
            self._has_wall_west = False
            if (
                not self.has_wall_north and
                not self.has_wall_east and
                not self.has_wall_south and
                not self.has_wall_west
            ):
                self.has_walls = False
