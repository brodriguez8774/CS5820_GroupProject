"""
System entities that hold general system/world data in some manner.
"""

# System Imports.
import sdl2.ext
import random

# User Imports.
from src.logging import init_logging


# Initialize logger.
logger = init_logging(__name__)


# Module Variables.
# Here, we point to our image files to render to user.
RESOURCES = sdl2.ext.Resources(__file__, '../images/')


# region Active Systems

class Movement:
    """
    Holds movement tick data for an entity.
    """
    def __init__(self, data_manager):
        # Call parent logic.
        super().__init__()

        # Set class variables.
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
        pos_x = (tile_x * 50) + self.data_manager.tile_data['max_pixel_west']
        pos_y = (tile_y * 50) + self.data_manager.tile_data['max_pixel_north']

        # Return calculated pixel coordinates.
        return pos_x, pos_y


class AI:
    """
    Holds AI data for roomba entity.
    """
    def __init__(self, data_manager):
        # Call parent logic.
        super().__init__()

        # Set class variables.
        self.data_manager = data_manager
        self.active = True
        self._timer_counter = 0
        self._ai_tick_rate = 20
        self.debug_set = []
        self.pending_list = []

    def check_counter(self):
        """
        Checks internal AI counter, so that entities delay actions enough that
        humans can actually see what the AI is doing.

        We do this internally, instead of using sdl2.SDL_Delay(), so that the game-world is still
        responsive even when the AI is waiting to trigger.

        This is based on the "_ai_tick_rate" value. Smaller values means it triggers faster.
        :return: True if AI has met tick rate and should trigger | False otherwise.
        """
        # Increment counter.
        self._timer_counter += 1

        # Check if counter has hit value to run AI trigger.
        if self._timer_counter == self._ai_tick_rate:
            # Reset counter for next AI trigger.
            self._timer_counter = 0

            return True
        else:
            # AI is still ticking to next trigger.
            return False

    def _calc_distance_cost(self, curr_tile_x, curr_tile_y, end_tile_x, end_tile_y):
        """"""
        distance = abs(curr_tile_x - end_tile_x) + abs(curr_tile_y - end_tile_y)
        print('tile_cost for ({0}, {1}) to ({2}, {3}): {4}'.format(curr_tile_x, curr_tile_y, end_tile_x, end_tile_y, distance))
        return distance

    def _calc_forward_cost(self, curr_tile, end_tile):
        """"""

# endregion Active Systems


# region Entity Systems

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

        if tile_x == (data_manager.tile_data['tile_w_count'] - 1):
            # Set east (right) wall to active.
            if self.wall_state == 0:
                self.wall_state = 2
            else:
                self.wall_state = 5

            # Update tile disallowed states.
            self._disallowed_states += [0, 1, 3, 4, 6, 7, 10, 12]

        if tile_y == (data_manager.tile_data['tile_h_count'] - 1):
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

    # region Class Properties

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
            self.walls['north'].sprite.depth = self.data_manager.sprite_depth['wall']

            # Update tile management variables.
            self.has_walls = True
            self._has_wall_north = True
            self._wall_state = self.get_new_state()

            # Check if full tileset has been initialized. Otherwise skip further logic.
            if self.data_manager.tile_set:

                # Update adjacent tile variables.
                if self.tile_y > 0:
                    adj_tile = self.data_manager.tile_set.tiles[self.tile_y - 1][self.tile_x]
                    # Prevent infinite loops.
                    if not adj_tile.walls.has_wall_south:
                        adj_tile.walls.has_wall_south = True

                # Update graph data structure. This is used for search algorithms.
                if self.tile_y > 0:
                    curr_tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y)
                    neighbor_tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y - 1)
                    self.data_manager.graph[curr_tile_id][neighbor_tile_id]['open'] = False

        else:
            # Setting to False.

            # Update wall displaying/rendering.
            self.walls['north'].sprite.depth = self.data_manager.sprite_depth['inactive']

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

            # Check if full tileset has been initialized. Otherwise skip further logic.
            if self.data_manager.tile_set:

                # Update adjacent tile variables.
                if self.tile_y > 0:
                    adj_tile = self.data_manager.tile_set.tiles[self.tile_y - 1][self.tile_x]
                    # Prevent infinite loops.
                    if adj_tile.walls.has_wall_south:
                        adj_tile.walls.has_wall_south = False

                # Update graph data structure. This is used for search algorithms.
                if self.tile_y > 0:
                    curr_tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y)
                    neighbor_tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y - 1)
                    self.data_manager.graph[curr_tile_id][neighbor_tile_id]['open'] = True

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
            self.walls['east'].sprite.depth = self.data_manager.sprite_depth['wall']

            # Update tile management variables.
            self.has_walls = True
            self._has_wall_east = True
            self._wall_state = self.get_new_state()

            # Check if full tileset has been initialized. Otherwise skip further logic.
            if self.data_manager.tile_set:

                # Update adjacent tile variables.
                if self.tile_x < (self.data_manager.tile_data['tile_w_count'] - 1):
                    adj_tile = self.data_manager.tile_set.tiles[self.tile_y][self.tile_x + 1]
                    # Prevent infinite loops.
                    if not adj_tile.walls.has_wall_west:
                        adj_tile.walls.has_wall_west = True

                # Update graph data structure. This is used for search algorithms.
                if self.tile_x < (self.data_manager.tile_data['tile_w_count'] - 1):
                    curr_tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y)
                    neighbor_tile_id = '{0}, {1}'.format(self.tile_x + 1, self.tile_y)
                    self.data_manager.graph[curr_tile_id][neighbor_tile_id]['open'] = False

        else:
            # Setting to False.

            # Update wall displaying/rendering.
            self.walls['east'].sprite.depth = self.data_manager.sprite_depth['inactive']

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

            # Check if full tileset has been initialized. Otherwise skip further logic.
            if self.data_manager.tile_set:

                # Update adjacent tile variables.
                if self.tile_x < (self.data_manager.tile_data['tile_w_count'] - 1):
                    adj_tile = self.data_manager.tile_set.tiles[self.tile_y][self.tile_x + 1]
                    # Prevent infinite loops.
                    if adj_tile.walls.has_wall_west:
                        adj_tile.walls.has_wall_west = False

                # Update graph data structure. This is used for search algorithms.
                if self.tile_x < (self.data_manager.tile_data['tile_w_count'] - 1):
                    curr_tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y)
                    neighbor_tile_id = '{0}, {1}'.format(self.tile_x + 1, self.tile_y)
                    self.data_manager.graph[curr_tile_id][neighbor_tile_id]['open'] = True

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
            self.walls['south'].sprite.depth = self.data_manager.sprite_depth['wall']

            # Update tile management variables.
            self.has_walls = True
            self._has_wall_south = True
            self._wall_state = self.get_new_state()

            # Check if full tileset has been initialized. Otherwise skip further logic.
            if self.data_manager.tile_set:

                # Update adjacent tile variables.
                if self.tile_y < (self.data_manager.tile_data['tile_h_count'] - 1):
                    adj_tile = self.data_manager.tile_set.tiles[self.tile_y + 1][self.tile_x]
                    # Prevent infinite loops.
                    if not adj_tile.walls.has_wall_north:
                        adj_tile.walls.has_wall_north = True

                # Update graph data structure. This is used for search algorithms.
                if self.tile_y < (self.data_manager.tile_data['tile_h_count'] - 1):
                    curr_tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y)
                    neighbor_tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y + 1)
                    self.data_manager.graph[curr_tile_id][neighbor_tile_id]['open'] = False

        else:
            # Setting to False.

            # Update wall displaying/rendering.
            self.walls['south'].sprite.depth = self.data_manager.sprite_depth['inactive']

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

            # Check if full tileset has been initialized. Otherwise skip further logic.
            if self.data_manager.tile_set:

                # Update adjacent tile variables.
                if self.tile_y < (self.data_manager.tile_data['tile_h_count'] - 1):
                    adj_tile = self.data_manager.tile_set.tiles[self.tile_y + 1][self.tile_x]
                    # Prevent infinite loops.
                    if adj_tile.walls.has_wall_north:
                        adj_tile.walls.has_wall_north = False

                # Update graph data structure. This is used for search algorithms.
                if self.tile_y < (self.data_manager.tile_data['tile_h_count'] - 1):
                    curr_tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y)
                    neighbor_tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y + 1)
                    self.data_manager.graph[curr_tile_id][neighbor_tile_id]['open'] = True

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
            self.walls['west'].sprite.depth = self.data_manager.sprite_depth['wall']

            # Update tile management variables.
            self.has_walls = True
            self._has_wall_west = True
            self._wall_state = self.get_new_state()

            # Check if full tileset has been initialized. Otherwise skip further logic.
            if self.data_manager.tile_set:

                # Update adjacent tile variables.
                if self.tile_x > 0:
                    adj_tile = self.data_manager.tile_set.tiles[self.tile_y][self.tile_x - 1]
                    # Prevent infinite loops.
                    if not adj_tile.walls.has_wall_east:
                        adj_tile.walls.has_wall_east = True

                # Update graph data structure. This is used for search algorithms.
                if self.tile_x > 0:
                    curr_tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y)
                    neighbor_tile_id = '{0}, {1}'.format(self.tile_x - 1, self.tile_y)
                    self.data_manager.graph[curr_tile_id][neighbor_tile_id]['open'] = False

        else:
            # Setting to False.

            # Update wall displaying/rendering.
            self.walls['west'].sprite.depth = self.data_manager.sprite_depth['inactive']

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

            # Check if full tileset has been initialized. Otherwise skip further logic.
            if self.data_manager.tile_set:

                # Update adjacent tile variables.
                if self.tile_x > 0:
                    adj_tile = self.data_manager.tile_set.tiles[self.tile_y][self.tile_x - 1]
                    # Prevent infinite loops.
                    if adj_tile.walls.has_wall_east:
                        adj_tile.walls.has_wall_east = False

                # Update graph data structure. This is used for search algorithms.
                if self.tile_x > 0:
                    curr_tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y)
                    neighbor_tile_id = '{0}, {1}'.format(self.tile_x - 1, self.tile_y)
                    self.data_manager.graph[curr_tile_id][neighbor_tile_id]['open'] = True

    # endregion Class Properties

    # region Class Functions

    def validate_wall_state(self, wall_state):
        """
        Ensures current wall state is valid.
        :param wall_state: Integer value of current potential new wall configuration for tile.
        :return: True if new state is valid for wall | False otherwise.
        """
        # Verify state is within expected bounds.
        if wall_state < 0:
            return False
        elif wall_state > self._wall_state_max:
            return False

        # Skip invalid states for this tile location.
        if wall_state in self._disallowed_states:
            return False

        return True

    def check_has_extra_walls(self):
        """
        Checks if tile entity has "extra walls", outside of minimum the tile is required to have (depending on position).
        :return: True if tile has "extra walls" | False otherwise.
        """
        # Do easy check for any walls.
        if not self.has_walls:
            # No walls at all.
            return False
        else:
            # Tile has some walls. Double check if edge tile or not.
            has_walls = True
            if self.tile_x == 0:
                # Tile is on left edge of grid.

                if self.tile_y == 0:
                    # Tile is on upper left of grid.
                    if self.wall_state == 7:
                        has_walls = False

                elif self.tile_y == self.data_manager.tile_data['tile_h_count'] - 1:
                    # Tile is on bottom left of grid.
                    if self.wall_state == 10:
                        has_walls = False

                else:
                    # Tile is on general left edge, but not corner.
                    if self.wall_state == 4:
                        has_walls = False

            elif self.tile_x == self.data_manager.tile_data['tile_w_count'] - 1:
                # Tile is on right edge of grid.

                if self.tile_y == 0:
                    # Tile is on upper right of grid.
                    if self.wall_state == 5:
                        has_walls = False

                elif self.tile_y == self.data_manager.tile_data['tile_h_count'] - 1:
                    # Tile is on lower right of grid.
                    if self.wall_state == 8:
                        has_walls = False

                else:
                    # Tile is on general right edge, but not corner.
                    if self.wall_state == 2:
                        has_walls = False

            elif self.tile_y == 0:
                # Tile is on general top edge, but not corner.
                if self.wall_state == 1:
                    has_walls = False

            elif self.tile_y == self.data_manager.tile_data['tile_h_count'] - 1:
                # Tile is on general bottom edge, but not corner.
                if self.wall_state == 3:
                    has_walls = False

            # Return final condition.
            return has_walls

    def bipartite_color_validation(self):
        """
        Validates wall placement by using 2-coloring on the tile graph to ensure all nodes are reachable by the roomba.
        """
        # Get initial color state of tiles.
        green_tiles, red_tiles = self.calc_bipartite_color()

        # Get roomba location.
        roomba_x, roomba_y = self.data_manager.roomba.sprite.tile

        # Loop until all tiles are green.
        while len(red_tiles) > 0:

            # Lazily calculate by handling first tile in "red" list.
            curr_problem_child = red_tiles.pop(0)

            # Get actual problem tile.
            pos_x = int(curr_problem_child[0])
            pos_y = int(curr_problem_child[3])
            tile = self.data_manager.tile_set.tiles[pos_y][pos_x]

            # Fetch neighbor tiles.
            # If any neighbor is green, then tear down wall.
            is_red = True
            # Check if north is green.
            if is_red and pos_y > 0:
                north_neighbor = self.data_manager.tile_set.tiles[pos_y - 1][pos_x]
                north_id = '{0}, {1}'.format(north_neighbor.sprite.tile[0], north_neighbor.sprite.tile[1])

                if north_id in green_tiles:
                    # North is green. Break wall and set to green also.
                    tile.walls.has_wall_north = False
                    is_red = False
                    green_tiles.append(curr_problem_child)

            # Check if east is green.
            if is_red and pos_x < (self.data_manager.tile_data['tile_w_count'] - 1):
                east_neighbor = self.data_manager.tile_set.tiles[pos_y][pos_x + 1]
                east_id = '{0}, {1}'.format(east_neighbor.sprite.tile[0], east_neighbor.sprite.tile[1])

                if east_id in green_tiles:
                    # East is green. Break wall and set to green also.
                    tile.walls.has_wall_east = False
                    is_red = False
                    green_tiles.append(curr_problem_child)

            # Check if south is green.
            if is_red and pos_y < (self.data_manager.tile_data['tile_h_count'] - 1):
                south_neighbor = self.data_manager.tile_set.tiles[pos_y + 1][pos_x]
                south_id = '{0}, {1}'.format(south_neighbor.sprite.tile[0], south_neighbor.sprite.tile[1])

                if south_id in green_tiles:
                    # South is green. Break wall and set to green also.
                    tile.walls.has_wall_south = False
                    is_red = False
                    green_tiles.append(curr_problem_child)

            # Check if west is green.
            if is_red and pos_x > 0:
                west_neighbor = self.data_manager.tile_set.tiles[pos_y][pos_x - 1]
                west_id = '{0}, {1}'.format(west_neighbor.sprite.tile[0], west_neighbor.sprite.tile[1])

                if west_id in green_tiles:
                    # West is green. Break wall and set to green also.
                    tile.walls.has_wall_west = False
                    is_red = False
                    green_tiles.append(curr_problem_child)

            # Check if any walls were successfully broken down.
            if not is_red:
                # Wall was broken. Recalculate color state of tiles for next loop.
                green_tiles, red_tiles = self.calc_bipartite_color()
            else:
                # All adjacent tiles are red. Failed to break down any walls.
                # Readd tile to end of "red list" and try again with next tile.
                red_tiles.append(curr_problem_child)

    def calc_bipartite_color(self):
        """
        Calculates all tiles accessible by roomba entity. These are marked as "green", all other tiles are "red".
        :return: (Array of green tiles, array of red tiles).
        """
        # Get roomba location.
        roomba_x, roomba_y = self.data_manager.roomba.sprite.tile

        # Initialize all tiles to "red".
        graph = self.data_manager.graph
        red_tiles = list(graph.nodes())
        green_tiles = []
        pending_tile_list = []

        # Start by setting roomba tile to "green".
        tile_id = '{0}, {1}'.format(roomba_x, roomba_y)
        green_tiles.append(tile_id)
        red_tiles.remove(tile_id)
        pending_tile_list.append(tile_id)

        # Loop through pending list until it's empty.
        # Here, we loop through all "green" tiles, checking for additional connected tiles to set to "green".
        while len(pending_tile_list) > 0:

            # Grab tile at start of list.
            tile_id = pending_tile_list.pop(0)
            pos_x = int(tile_id[0])
            pos_y = int(tile_id[3])

            # Get literal tile entity.
            curr_tile = self.data_manager.tile_set.tiles[pos_y][pos_x]

            # Fetch neighbor tiles.
            if not curr_tile.walls.has_wall_north and pos_y > 0:
                # North tile is connected.
                north_neighbor = self.data_manager.tile_set.tiles[pos_y - 1][pos_x]
                north_id = '{0}, {1}'.format(north_neighbor.sprite.tile[0], north_neighbor.sprite.tile[1])

                # Set tile to "green", if not already.
                if north_id in red_tiles:
                    green_tiles.append(north_id)
                    red_tiles.remove(north_id)
                    pending_tile_list.append(north_id)

            if not curr_tile.walls.has_wall_east and self.tile_y < (self.data_manager.tile_data['tile_w_count'] + 1):
                # East tile is connected.
                east_neighbor = self.data_manager.tile_set.tiles[pos_y][pos_x + 1]
                east_id = '{0}, {1}'.format(east_neighbor.sprite.tile[0], east_neighbor.sprite.tile[1])

                # Set tile to "green", if not already.
                if east_id in red_tiles:
                    green_tiles.append(east_id)
                    red_tiles.remove(east_id)
                    pending_tile_list.append(east_id)

            if not curr_tile.walls.has_wall_south and self.tile_y < (self.data_manager.tile_data['tile_h_count'] - 1):
                # South tile is connected.
                south_neighbor = self.data_manager.tile_set.tiles[pos_y + 1][pos_x]
                south_id = '{0}, {1}'.format(south_neighbor.sprite.tile[0], south_neighbor.sprite.tile[1])

                # Set tile to "green", if not already.
                if south_id in red_tiles:
                    green_tiles.append(south_id)
                    red_tiles.remove(south_id)
                    pending_tile_list.append(south_id)

            if not curr_tile.walls.has_wall_west and pos_x > 0:
                # West tile is connected.
                west_neighbor = self.data_manager.tile_set.tiles[pos_y][pos_x - 1]
                west_id = '{0}, {1}'.format(west_neighbor.sprite.tile[0], west_neighbor.sprite.tile[1])

                # Set tile to "green", if not already.
                if west_id in red_tiles:
                    green_tiles.append(west_id)
                    red_tiles.remove(west_id)
                    pending_tile_list.append(west_id)

        return green_tiles, red_tiles

    def increment_wall_state(self):
        """
        Increases wall state counter.
        Ensures walls update in predictable order.
        """
        wall_state = self.wall_state + 1

        # Loop until valid "next increment" state is found.
        while not self.validate_wall_state(wall_state):
            # State not valid. Check next increment value.
            wall_state += 1

            # Verify state is within expected bounds.
            if wall_state < 0:
                wall_state = self._wall_state_max
            elif wall_state > self._wall_state_max:
                wall_state = 0

        # Valid state found. Save new value to class.
        self.wall_state = wall_state

    def decrement_wall_state(self):
        """
        Decreases wall state counter.
        Ensures walls update in predictable order.
        """
        wall_state = self.wall_state - 1

        # Loop until valid "next decrement" state is found.
        while not self.validate_wall_state(wall_state):
            # State not valid. Check next decrement value.
            wall_state -= 1

            # Verify state is within expected bounds.
            if wall_state < 0:
                wall_state = self._wall_state_max
            elif wall_state > self._wall_state_max:
                wall_state = 0

        # Valid state found. Save new value to class.
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

    # region Random Wall Assignment

    def randomize_walls(self, weighted=True):
        """
        Sets walls to random configuration value.
        :param weighted: Bool indicating if randomization should use weighted generation or not.
        """
        # Handle based on mode.
        if not weighted:
            # Give all states an equal chance.
            # Here, we get a random integer, then simply increment until a valid state is found.
            wall_state = random.randint(0, self._wall_state_max)

            # Loop until valid "next increment" state is found.
            while not self.validate_wall_state(wall_state):
                # State not valid. Check next increment value.
                wall_state += 1

                # Verify state is within expected bounds.
                if wall_state < 0:
                    wall_state = self._wall_state_max
                elif wall_state > self._wall_state_max:
                    wall_state = 0

            # Valid state found. Save new value to class.
            self.wall_state = wall_state

        else:
            # Call weighted randomization logic.
            self._weighted_randomize_walls()

    def _weighted_randomize_walls(self, tried_0=False, tried_1=False, tried_2=False, tried_3=False):
        """
        Assign random value based on weights.

        Weight values are as follows:
            * No walls: 25% chance.
            * 1 Wall: 25% chance.
            * 2 Walls: 25% chance.
            * 3 Walls: 25% chance.

        Note that above weight percentages assume that all wall configurations are valid for tile.
        This is not true for certain edge-case tiles. In such an edge-case, logic is tailored to try to avoid
        the possibility of infinite/long loops, while still being as random as possible.
        """
        # Get random value for tile count. Default 25% chance of each.
        rand_val = random.randint(0, 3)

        if rand_val == 0:
            # Set to no walls.
            self._assign_0_walls(tried_0=tried_0, tried_1=tried_1, tried_2=tried_2, tried_3=tried_3)

        elif rand_val == 1:
            # Set to one wall.
            self._assign_1_wall(tried_0=tried_0, tried_1=tried_1, tried_2=tried_2, tried_3=tried_3)

        elif rand_val == 2:
            # Set to two walls.
            self._assign_2_walls(tried_0=tried_0, tried_1=tried_1, tried_2=tried_2, tried_3=tried_3)

        elif rand_val == 3:
            # Set to three walls.
            self._assign_3_walls(tried_0=tried_0, tried_1=tried_1, tried_2=tried_2, tried_3=tried_3)

    def _assign_0_walls(self, tried_0=False, tried_1=False, tried_2=False, tried_3=False):
        """
        Logic for assigning 3 randomized walls to tile, if possible.
        """
        # Update variables for wall assignment.
        tried_0 = True
        potential_states = [0]

        # Call general assignment logic.
        self._assign_wall(potential_states, tried_0, tried_1, tried_2, tried_3)

    def _assign_1_wall(self, tried_0=False, tried_1=False, tried_2=False, tried_3=False):
        """
        Logic for assigning 3 randomized walls to tile, if possible.
        """
        # Update variables for wall assignment.
        tried_1 = True
        potential_states = [1, 2, 3, 4]

        # Call general assignment logic.
        self._assign_wall(potential_states, tried_0, tried_1, tried_2, tried_3)

    def _assign_2_walls(self, tried_0=False, tried_1=False, tried_2=False, tried_3=False):
        """
        Logic for assigning 3 randomized walls to tile, if possible.
        """
        # Update variables for wall assignment.
        tried_2 = True
        potential_states = [5, 6, 7, 8, 9, 10]

        # Call general assignment logic.
        self._assign_wall(potential_states, tried_0, tried_1, tried_2, tried_3)

    def _assign_3_walls(self, tried_0=False, tried_1=False, tried_2=False, tried_3=False):
        """
        Logic for assigning 3 randomized walls to tile, if possible.
        """
        # Update variables for wall assignment.
        tried_3 = True
        potential_states = [11, 12, 13, 14]

        # Call general assignment logic.
        self._assign_wall(potential_states, tried_0, tried_1, tried_2, tried_3)

    def _assign_wall(self, potential_states, tried_0, tried_1, tried_2, tried_3):
        """
        General logic for assigning randomized wall when using weights.
        """
        valid_state = False
        wall_state = -1

        # Loop until we exhaust all possible states or valid state is found.
        while len(potential_states) > 0 and not valid_state:

            # Get new random value.
            rand_max = len(potential_states) - 1
            potential_state_index = random.randint(0, rand_max)

            # Check if valid.
            if self.validate_wall_state(potential_states[potential_state_index]):
                # Valid state for tile. Exit loop.
                valid_state = True
                wall_state = potential_states[potential_state_index]
            else:
                # Invalid state for tile. Delete candidate from "potentials" set and try again.
                del potential_states[potential_state_index]

        # Check if valid state was found.
        if valid_state:
            # Check that wall state actually updated.
            if wall_state > -1:
                # Valid state found.
                self.wall_state = wall_state
            else:
                raise RuntimeError('Failed to find valid state. Logic error somewhere.')

        else:
            # Valid state not found.
            # That means tile cannot have a valid configuration with this number of walls.

            # Check that at least one wall count is not yet attempted for tile.
            if not (tried_0 and tried_1 and tried_2 and tried_3):
                # One or more wall counts have not yet been attempted.
                # Attempting randomization again, but with a different wall count.
                self._weighted_randomize_walls(tried_0=tried_0, tried_1=tried_1, tried_2=tried_2, tried_3=tried_3)
            else:
                # All wall counts have been attempted? Ohno...
                raise RuntimeError('Failed to find valid state. Logic error somewhere.')

    # endregion Random Wall Assignment

    # endregion Class Functions


class TrashPile:
    """
    Holds "trash pile" data for a "tile" entity.
    """
    def __init__(self, data_manager, trash_entity, tile_x, tile_y):
        self.data_manager = data_manager
        self.trash = trash_entity
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.exists = False

        # Default with trash on roughly 10% of all tiles.
        total_tiles = data_manager.tile_data['tile_w_count'] * data_manager.tile_data['tile_h_count']
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
            self.trash.sprite.depth = self.data_manager.sprite_depth['trash']

            # Update internal trackers.
            self.exists = True

            # Update graph data.
            tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y)
            if tile_id not in self.data_manager.graph.data['trash_tiles']:
                self.data_manager.graph.data['trash_tiles'].append(tile_id)

            return True

    def clean(self):
        """
        Attempts to clean tile of trash, if any is present.
        """
        if self.exists:
            logger.info('Cleaned trash at tile ({0}, {1}).'.format(self.tile_x, self.tile_y))

            # Update tile data.
            self.trash.sprite.depth = self.data_manager.sprite_depth['inactive']

            # Update internal trackers.
            self.exists = False

            # Update graph data.
            tile_id = '{0}, {1}'.format(self.tile_x, self.tile_y)
            self.data_manager.graph.data['trash_tiles'].remove(tile_id)
        else:
            logger.info('No trash to clean at tile ({0}, {1}).'.format(self.tile_x, self.tile_y))

# endregion Entity Systems
