"""
System entities that hold general system/world data in some manner.
"""

# System Imports.
import random
import sdl2.ext

# User Imports.
from src.logging import init_logging


# Initialize logger.
logger = init_logging(__name__)


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
        self._disallowed_states = []
        self._has_wall_north = False
        self._has_wall_east = False
        self._has_wall_south = False
        self._has_wall_west = False

        if tile_y == 0:
            # Set north (upper) wall to active.
            self.wall_state = 1

            # Update tile disallowed states.
            self._disallowed_states += [0, 2, 3, 4, 8, 9, 10, 11]

        if tile_x == (data_manager.sprite_data['sprite_w_count'] - 1):
            # Set east (right) wall to active.
            if self.wall_state == 0:
                self.wall_state = 2
            else:
                self.wall_state = 5

            # Update tile disallowed states.
            self._disallowed_states += [0, 1, 3, 4, 6, 7, 10, 12]

        if tile_y == (data_manager.sprite_data['sprite_h_count'] - 1):
            # Set south (lower) wall to active.
            if self.wall_state == 0:
                self.wall_state = 3
            else:
                self.wall_state = 8

            # Update tile disallowed states.
            self._disallowed_states += [0, 1, 2, 4, 5, 7, 9, 13]

        if tile_x == 0:
            # Set west (left) wall to active.
            if self.wall_state == 0:
                self.wall_state = 4
            elif self.wall_state == 1:
                self.wall_state = 7
            else:
                self.wall_state = 10

            # Update tile disallowed states.
            self._disallowed_states += [0, 1, 2, 3, 5, 6, 8, 14]

    def increment_wall_state(self):
        """
        Increases wall state counter.
        Ensures walls update in predictable order.
        """
        wall_state = self.wall_state + 1

        # Verify state is still valid value.
        if wall_state > self._wall_state_max:
            wall_state = 0

        # Skip certain state values for outer tiles.
        # Handle for north (upper) edge tiles.
        if self.tile_y == 0:

            # Loop until valid state is found.
            valid_state = False
            while not valid_state:
                valid_state = True

                # Skip invalid states for this tile location.
                if wall_state in self._disallowed_states:
                    wall_state += 1
                    valid_state = False

                # Verify state is still valid value.
                if wall_state > self._wall_state_max:
                    wall_state = 0
                    valid_state = False

        # Handle for east (left) edge tiles.
        if self.tile_x == (self.data_manager.sprite_data['sprite_w_count'] - 1):

            # Loop until valid state is found.
            valid_state = False
            while not valid_state:
                valid_state = True

                # Skip invalid states for this tile location.
                if wall_state in self._disallowed_states:
                    wall_state += 1
                    valid_state = False

                # Verify state is still valid value.
                if wall_state > self._wall_state_max:
                    wall_state = 0
                    valid_state = False

        # Handle for south (lower) edge tiles.
        if self.tile_y == (self.data_manager.sprite_data['sprite_h_count'] - 1):

            # Loop until valid state is found.
            valid_state = False
            while not valid_state:
                valid_state = True

                # Skip invalid states for this tile location.
                if wall_state in self._disallowed_states:
                    wall_state += 1
                    valid_state = False

                # Verify state is still valid value.
                if wall_state > self._wall_state_max:
                    wall_state = 0
                    valid_state = False

        # Handle for west (right) edge tiles.
        if self.tile_x == 0:

            # Loop until valid state is found.
            valid_state = False
            while not valid_state:
                valid_state = True

                # Skip invalid states for this tile location.
                if wall_state in self._disallowed_states:
                    wall_state += 1
                    valid_state = False

                # Verify state is still valid value.
                if wall_state > self._wall_state_max:
                    wall_state = 0
                    valid_state = False

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

        # Skip certain state values for outer tiles.
        # Handle for north (upper) edge tiles.
        if self.tile_y == 0:

            # Loop until valid state is found.
            valid_state = False
            while not valid_state:
                valid_state = True

                # Skip invalid states for this tile location.
                if wall_state in self._disallowed_states:
                    wall_state -= 1
                    valid_state = False

                # Verify state is still valid value.
                if wall_state < 0:
                    wall_state = self._wall_state_max
                    valid_state = False

        # Handle for east (left) edge tiles.
        if self.tile_x == (self.data_manager.sprite_data['sprite_w_count'] - 1):

            # Loop until valid state is found.
            valid_state = False
            while not valid_state:
                valid_state = True

                # Skip invalid states for this tile location.
                if wall_state in self._disallowed_states:
                    wall_state -= 1
                    valid_state = False

                # Verify state is still valid value.
                if wall_state < 0:
                    wall_state = self._wall_state_max
                    valid_state = False

        # Handle for south (lower) edge tiles.
        if self.tile_y == (self.data_manager.sprite_data['sprite_h_count'] - 1):

            # Loop until valid state is found.
            valid_state = False
            while not valid_state:
                valid_state = True

                # Skip invalid states for this tile location.
                if wall_state in self._disallowed_states:
                    wall_state -= 1
                    valid_state = False

                # Verify state is still valid value.
                if wall_state < 0:
                    wall_state = self._wall_state_max
                    valid_state = False

        # Handle for west (right) edge tiles.
        if self.tile_x == 0:

            # Loop until valid state is found.
            valid_state = False
            while not valid_state:
                valid_state = True

                # Skip invalid states for this tile location.
                if wall_state in self._disallowed_states:
                    wall_state -= 1
                    valid_state = False

                # Verify state is still valid value.
                if wall_state < 0:
                    wall_state = self._wall_state_max
                    valid_state = False

        # Save value to class.
        self.wall_state = wall_state

    def get_new_state(self):
        """
        Determine new state counter, based on internal wall data.
        :return:
        """
        # All walls inactive.
        if (

            self.has_wall_north is False and
            self.has_wall_east is False and
            self.has_wall_south is False and
            self.has_wall_west is False
        ):
            return 0

        # Only north wall active.
        elif (
            self.has_wall_north is True and
            self.has_wall_east is False and
            self.has_wall_south is False and
            self.has_wall_west is False
        ):
            return 1

        # Only east wall active.
        elif (
            self.has_wall_north is False and
            self.has_wall_east is True and
            self.has_wall_south is False and
            self.has_wall_west is False
        ):
            return 2

        # Only south wall active.
        elif (
            self.has_wall_north is False and
            self.has_wall_east is False and
            self.has_wall_south is True and
            self.has_wall_west is False
        ):
            return 3

        # Only west wall active.
        elif (
            self.has_wall_north is False and
            self.has_wall_east is False and
            self.has_wall_south is False and
            self.has_wall_west is True
        ):
            return 4

        # North and east walls active.
        elif (
            self.has_wall_north is True and
            self.has_wall_east is True and
            self.has_wall_south is False and
            self.has_wall_west is False
        ):
            return 5

        # North and south walls active.
        elif (
            self.has_wall_north is True and
            self.has_wall_east is False and
            self.has_wall_south is True and
            self.has_wall_west is False
        ):
            return 6

        # North and west walls active.
        elif (
            self.has_wall_north is True and
            self.has_wall_east is False and
            self.has_wall_south is False and
            self.has_wall_west is True
        ):
            return 7

        # East and south walls active.
        elif (
            self.has_wall_north is False and
            self.has_wall_east is True and
            self.has_wall_south is True and
            self.has_wall_west is False
        ):
            return 8

        # East and west walls active.
        elif (
            self.has_wall_north is False and
            self.has_wall_east is True and
            self.has_wall_south is False and
            self.has_wall_west is True
        ):
            return 9

        # South and west walls active.
        elif (
            self.has_wall_north is False and
            self.has_wall_east is False and
            self.has_wall_south is True and
            self.has_wall_west is True
        ):
            return 10

        # All except north wall active.
        elif (
            self.has_wall_north is False and
            self.has_wall_east is True and
            self.has_wall_south is True and
            self.has_wall_west is True
        ):
            return 11

        # All except east wall active.
        elif (
            self.has_wall_north is True and
            self.has_wall_east is False and
            self.has_wall_south is True and
            self.has_wall_west is True
        ):
            return 12

        # All except south wall active.
        elif (
            self.has_wall_north is True and
            self.has_wall_east is True and
            self.has_wall_south is False and
            self.has_wall_west is True
        ):
            return 13

        # All except west wall active.
        elif (
            self.has_wall_north is True and
            self.has_wall_east is True and
            self.has_wall_south is True and
            self.has_wall_west is False
        ):
            return 14

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
            self._wall_state = self.get_new_state()

            # Update adjacent tile variables.
            # Note we only handle this if full tileset has been initialized.
            if self.data_manager.tile_set and self.tile_y > 0:
                adj_tile = self.data_manager.tile_set.tiles[self.tile_y - 1][self.tile_x]
                # Prevent infinite loops.
                if not adj_tile.walls.has_wall_south:
                    adj_tile.walls.has_wall_south = True

        else:
            # Setting to False.

            # Update wall displaying/rendering.
            self.walls['north'].sprite.depth = 0

            # Update tile management variables.
            self._has_wall_north = False
            self._wall_state = self.get_new_state()
            if (
                not self.has_wall_north and
                not self.has_wall_east and
                not self.has_wall_south and
                not self.has_wall_west
            ):
                self.has_walls = False

            # Update adjacent tile variables.
            # Note we only handle this if full tileset has been initialized.
            if self.data_manager.tile_set:
                adj_tile = self.data_manager.tile_set.tiles[self.tile_y - 1][self.tile_x]
                # Prevent infinite loops.
                if adj_tile.walls.has_wall_south:
                    adj_tile.walls.has_wall_south = False

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
            self._wall_state = self.get_new_state()

            # Update adjacent tile variables.
            # Note we only handle this if full tileset has been initialized.
            if self.data_manager.tile_set and self.tile_x < (self.data_manager.sprite_data['sprite_w_count'] - 1):
                adj_tile = self.data_manager.tile_set.tiles[self.tile_y][self.tile_x + 1]
                # Prevent infinite loops.
                if not adj_tile.walls.has_wall_west:
                    adj_tile.walls.has_wall_west = True

        else:
            # Setting to False.

            # Update wall displaying/rendering.
            self.walls['east'].sprite.depth = 0

            # Update tile management variables.
            self._has_wall_east = False
            self._wall_state = self.get_new_state()
            if (
                not self.has_wall_north and
                not self.has_wall_east and
                not self.has_wall_south and
                not self.has_wall_west
            ):
                self.has_walls = False

            # Update adjacent tile variables.
            # Note we only handle this if full tileset has been initialized.
            if self.data_manager.tile_set:
                adj_tile = self.data_manager.tile_set.tiles[self.tile_y][self.tile_x + 1]
                # Prevent infinite loops.
                if adj_tile.walls.has_wall_west:
                    adj_tile.walls.has_wall_west = False

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
            self._wall_state = self.get_new_state()

            # Update adjacent tile variables.
            # Note we only handle this if full tileset has been initialized.
            if self.data_manager.tile_set and self.tile_y < (self.data_manager.sprite_data['sprite_h_count'] - 1):
                adj_tile = self.data_manager.tile_set.tiles[self.tile_y + 1][self.tile_x]
                # Prevent infinite loops.
                if not adj_tile.walls.has_wall_north:
                    adj_tile.walls.has_wall_north = True

        else:
            # Setting to False.

            # Update wall displaying/rendering.
            self.walls['south'].sprite.depth = 0

            # Update tile management variables.
            self._has_wall_south = False
            self._wall_state = self.get_new_state()
            if (
                not self.has_wall_north and
                not self.has_wall_east and
                not self.has_wall_south and
                not self.has_wall_west
            ):
                self.has_walls = False

            # Update adjacent tile variables.
            # Note we only handle this if full tileset has been initialized.
            if self.data_manager.tile_set:
                adj_tile = self.data_manager.tile_set.tiles[self.tile_y + 1][self.tile_x]
                # Prevent infinite loops.
                if adj_tile.walls.has_wall_north:
                    adj_tile.walls.has_wall_north = False

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
            self._wall_state = self.get_new_state()

            # Update adjacent tile variables.
            # Note we only handle this if full tileset has been initialized.
            if self.data_manager.tile_set and self.tile_x > 0:
                adj_tile = self.data_manager.tile_set.tiles[self.tile_y][self.tile_x - 1]
                # Prevent infinite loops.
                if not adj_tile.walls.has_wall_east:
                    adj_tile.walls.has_wall_east = True

        else:
            # Setting to False.

            # Update wall displaying/rendering.
            self.walls['west'].sprite.depth = 0

            # Update tile management variables.
            self._has_wall_west = False
            self._wall_state = self.get_new_state()
            if (
                not self.has_wall_north and
                not self.has_wall_east and
                not self.has_wall_south and
                not self.has_wall_west
            ):
                self.has_walls = False

            # Update adjacent tile variables.
            # Note we only handle this if full tileset has been initialized.
            if self.data_manager.tile_set:
                adj_tile = self.data_manager.tile_set.tiles[self.tile_y][self.tile_x - 1]
                # Prevent infinite loops.
                if adj_tile.walls.has_wall_east:
                    adj_tile.walls.has_wall_east = False


class TrashPile:
    """
    Holds "trashpile" data for a "tile" entity.
    """
    def __init__(self, data_manager, trash_entity, tile_x, tile_y):
        self.data_manager = data_manager
        self.trash = trash_entity
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.exists = False

        # Default with trash on roughly 10% of all tiles.
        total_tiles = data_manager.sprite_data['sprite_w_count'] * data_manager.sprite_data['sprite_h_count']
        if random.randint(0, (total_tiles % 10)) < 1:
            self.place()

    def place(self):
        """
        Attempts to place trash on file.
        :return: Bool indicating if trash was successfully placed.
        """
        if self.exists:
            logger.info('Tile ({0}, {1}) already has trash.'.format(self.tile_x, self.tile_y))
            return False
        else:
            logger.info('Placed trash at tile ({0}, {1}).'.format(self.tile_x, self.tile_y))

            # Update tile data.
            self.trash.sprite.depth = 3

            # Update internal trackers.
            self.exists = True
            return True

    def clean(self):
        """
        Attempts to clean tile of trash, if any is present.
        """
        if self.exists:
            logger.info('Cleaned trash at tile ({0}, {1}).'.format(self.tile_x, self.tile_y))

            # Update tile data.
            self.trash.sprite.depth = 0

            # Update internal trackers.
            self.exists = False
        else:
            logger.info('No trash to clean at tile ({0}, {1}).'.format(self.tile_x, self.tile_y))
