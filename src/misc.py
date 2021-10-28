"""
Misc helper functions and classes.

Sprite Depth Values (0 is lowest. Higher values will display ontop of lower ones):
 * Roomba: 5
 * TrashBall: 4
 * Active Wall: 3
 * Debug Floor tile: 2
 * Floor Tile: 1
 * Hidden/Unused Sprites: 0
"""

# System Imports.
import sdl2.ext
import networkx

# User Imports.
from src.logging import init_logging


# Initialize logger.
logger = init_logging(__name__)


# Module Variables.
# Here, we point to our image files to render to user.
RESOURCES = sdl2.ext.Resources(__file__, './images/')


# region Data Structures

class DataManager:
    """
    Stores and manages general data, to minimize values needing to be passed back and forth between classes.
    """
    def __init__(self, world, window, sprite_factory, sprite_renderer, window_data, gui_data, tile_data):
        self.world = world
        self.window = window
        self.sprite_factory = sprite_factory
        self.sprite_renderer = sprite_renderer
        self.window_data = window_data
        self.gui_data = gui_data
        self.tile_data = tile_data
        self.gui = None
        self.tile_set = None
        self.roomba = None
        self.graph = networkx.Graph()
        self.graph.data = {
            'trash_tiles': []
        }
        self.sprite_depth = {
            'roomba': 5,
            'trash': 4,
            'wall': 3,
            'debug_floor_tile': 2,
            'floor_tile': 1,
            'inactive': 0,
        }


# endregion Data Structures


# region GUI Logic Functions

def handle_key_press(data_manager, event):
    """
    Handles key press event when running program.
    :param data_manager: Data manager data structure. Consolidates useful program data to one location.
    :param event: Event instance to handle. Only confirmed "key press" events should be passed here.
    """
    roomba = data_manager.roomba

    # Handle if arrow direction was pressed.
    if event.key.keysym.sym in [sdl2.SDLK_UP, sdl2.SDLK_w]:
        roomba.movement.north = True

    elif event.key.keysym.sym in [sdl2.SDLK_RIGHT, sdl2.SDLK_d]:
        roomba.movement.east = True

    elif event.key.keysym.sym in [sdl2.SDLK_DOWN, sdl2.SDLK_s]:
        roomba.movement.south = True

    elif event.key.keysym.sym in [sdl2.SDLK_LEFT, sdl2.SDLK_a]:
        roomba.movement.west = True


def handle_mouse_click(data_manager, button_state, pos_x, pos_y):
    """
    Handles mouse click event when running program.
    :param data_manager: Data manager data structure. Consolidates useful program data to one location.
    :param button_state: State of button on event. 1 = LeftClick, 2 = MiddleClick, 4 = RightClick.
    :param pos_x: Mouse click x coordinate.
    :param pos_y: Mouse click y coordinate.
    """
    logger.info('pos_x.value: {0}    pos_y.value: {1}'.format(pos_x, pos_y))
    logger.info('buttonstate: {0}'.format(button_state))

    # First, verify that click location is within some valid grid bounds. If not, we ignore click.
    gui_data = data_manager.gui_data
    tile_data = data_manager.tile_data
    if (
        (pos_x > gui_data['gui_w_start'] and pos_x < gui_data['gui_w_end']) and
        (pos_y > gui_data['gui_h_start'] and pos_y < gui_data['gui_h_end'])
    ):
        # Click was within gui bounds. Check if any gui elements were clicked.
        logger.info('    Is within GUI element bounds.')

        for element in data_manager.gui.elements:
            if (
                (pos_x > element.bounds['max_pixel_west'] and pos_x < element.bounds['max_pixel_east']) and
                (pos_y > element.bounds['max_pixel_north'] and pos_y < element.bounds['max_pixel_south'])
            ):
                element.on_click()

    elif (
        (pos_x > tile_data['max_pixel_west'] and pos_x < tile_data['max_pixel_east']) and
        (pos_y > tile_data['max_pixel_north'] and pos_y < tile_data['max_pixel_south'])
    ):
        # Click was within tile bounds. Calculate clicked tile.
        logger.info('    Is within Tile border bounds.')
        tile_x = int((pos_x - tile_data['max_pixel_west']) / 50)
        tile_y = int((pos_y - tile_data['max_pixel_north']) / 50)
        logger.info('    Found tile is    x: {0}    y: {1}'.format(tile_x, tile_y))

        # Get clicked tile object.
        tile = data_manager.tile_set.tiles[tile_y][tile_x]

        # Check what click type occurred.
        if button_state == 1:
            # Left click.
            logger.info('    Incrementing tile walls.')
            tile.walls.increment_wall_state()

        elif button_state == 2:
            # Middle click.

            # If tile is empty and no trash, generate some.
            if not tile.walls.has_walls and not tile.trashpile.exists:
                tile.trashpile.place()

            # Else if tile is empty and has trash, remove.
            elif tile.trashpile.exists:
                tile.trashpile.clean()

            # Otherwise reset wall state.
            else:
                # Attempt to reset tile to empty.
                # If state is invalid, increment until "original tile starting state" is found.
                logger.info('    Resetting tile wall state.')
                wall_state = 0
                while not tile.walls.validate_wall_state(wall_state):
                    wall_state += 1

                # Found valid state. Assign to tile.
                tile.walls.wall_state = wall_state

        elif button_state == 4:
            # Right click.
            logger.info('    Decrementing tile walls.')
            tile.walls.decrement_wall_state()

    # print('trash_tiles: {0}'.format(data_manager.graph.data['trash_tiles']))
    calc_trash_distances(data_manager)

# endregion GUI Logic Functions


# region General Logic Functions

def get_tile_coord_from_id(tile_id):
    """
    Parses tile id into respective integer coordinates.
    :param tile_id: Identifier for tile.
    :return: Tuple of (x_coord, y_coord) for tile.
    """
    tile_x = int(tile_id[0])
    tile_y = int(tile_id[3])

    return tile_x, tile_y


def get_tile_from_id(data_manager, tile_id):
    """
    Gets corresponding tile entity, from provided id.
    :param data_manager: Data manager data structure. Consolidates useful program data to one location.
    :param tile_id: Id of tile to get entity for.
    :return: Corresponding tile entity.
    """
    tile_x, tile_y = get_tile_coord_from_id(tile_id)
    return data_manager.tile_set.tiles[tile_y][tile_x]


def get_id_from_coord(tile_x, tile_y):
    """
    Get corresponding tile id, from tile coordinates.
    :param tile_x: Tile x coordinate.
    :param tile_y: Tile y coordinate.
    :return: Corresponding tile id.
    """
    return '{0}, {1}'.format(tile_x, tile_y)


def get_id_from_tile(tile_entity):
    """
    Gets corresponding tile id, from provided tile entity.
    :param tile_entity: Tile entity to generate id for.
    :return: Corresponding tile id.
    """
    tile_x, tile_y = tile_entity.sprite.tile
    return get_id_from_coord(tile_x, tile_y)


def calc_distance_cost(start_tile_x, start_tile_y, end_tile_x, end_tile_y):
    """
    Determines the minimum distance between two tiles, assuming no walls or barriers exist between them.
    :param start_tile_x: The x coordinate of the tile to start from.
    :param start_tile_y: The y coordinate of the tile to start from.
    :param end_tile_x: The x coordinate of the tile to end at.
    :param end_tile_y: The y coordinate of the tile to end at.
    :return: Calculated distance between tiles.
    """
    distance = abs(start_tile_x - end_tile_x) + abs(start_tile_y - end_tile_y)
    logger.info('    tile_cost for ({0}, {1}) to ({2}, {3}): {4}'.format(
        start_tile_x, start_tile_y, end_tile_x, end_tile_y, distance,
    ))
    return distance


def calc_trash_distances(data_manager):
    """
    Calculates the "ideal" distance from every trash pile to every other trash pile.
    Accounts for walls and barriers.

    This function should be called every time any wall or trash entity is added/removed/otherwise changed.
    :param data_manager: Data manager data structure. Consolidates useful program data to one location.
    :return:
    """
    priority_queue = []
    handled_tiles = {}

    def _calc_trash_distances():
        """
        Start of function logic.
        """
        # Tell function to use variables in larger function scope.
        nonlocal priority_queue
        nonlocal handled_tiles

        # Get list of all known trash piles.
        trash_tiles = data_manager.graph.data['trash_tiles']
        logger.info('trash_tiles: {0}'.format(trash_tiles))

        # Grab each tile with a trash pile.
        for start_tile_id in trash_tiles:
            # Parse out coordinates for tile.
            start_tile_x, start_tile_y = get_tile_coord_from_id(start_tile_id)
            start_tile = get_tile_from_id(data_manager, start_tile_id)

            logger.info('')
            logger.info('')
            logger.info('Calculating from tile ({0}, {1}):'.format(start_tile_x, start_tile_y))

            # Find distance from current trash pile to each other trash pile.
            for end_tile_id in trash_tiles:
                # Ensure tiles are different.
                if start_tile_id != end_tile_id:
                    # Parse out coordinates for tile.
                    end_tile_x, end_tile_y = get_tile_coord_from_id(end_tile_id)

                    # Initialize queue by calculating first tile distance and setting as first element.
                    _calc_neighbor_costs(start_tile, end_tile_x, end_tile_y)
                    logger.info('    to ({0}, {1}): {2}'.format(end_tile_x, end_tile_y, priority_queue))

                    # Iterate until we make it to our desired ending tile.
                    # Always use priority queue to check the shortest-distance tile.
                    iterate = True
                    while iterate and len(priority_queue) > 0:
                        # Parse out data for next tile.
                        curr_tile_data = priority_queue.pop(0)
                        logger.info('Handling {0}'.format(curr_tile_data))
                        curr_tile_id = curr_tile_data['id']
                        curr_tile = get_tile_from_id(data_manager, curr_tile_id)

                        # Check if tile is at desired end position.
                        curr_tile_x, curr_tile_y = curr_tile.sprite.tile
                        if curr_tile_x == end_tile_x and curr_tile_y == end_tile_y:
                            # Found path. Stop checking further tiles.
                            priority_queue = []
                            iterate = False
                            break

                        # Calculate distance costs of fellow neighbor tiles.
                        _calc_neighbor_costs(curr_tile, end_tile_x, end_tile_y)
                        logger.info('    to ({0}, {1}): {2}'.format(end_tile_x, end_tile_y, priority_queue))

                        if len(priority_queue) <= 0:
                            iterate = False

                # Stop after one trash-pair is fully calculated. For debugging. REMOVE LATER.
                break

            print('\n')

    def _calc_neighbor_costs(curr_tile, end_tile_x, end_tile_y, debug=False):
        """
        Calculate costs from neighbors of current tile, to desired ending tile coordinates.
        Skips any neighboring tiles that are blocked, such as by a wall.
        :param curr_tile: Tile entity to calculate from.
        :param end_tile_x: Desired ending x coordinates.
        :param end_tile_y: Desired ending y  coordinates.
        :param debug: Bool indicating if debug sprites should display.
        """
        debug = True

        from src.entities.object_entities import DebugTile

        # Tell function to use variables in larger function scope.
        nonlocal priority_queue
        nonlocal handled_tiles

        # Add current tile to set of "known handled tiles.
        # Allows us to skip tiles that have already been handled once.
        # We use a dict to make it faster, so we have O(1) check time, instead of potentially large times
        # when we have many tiles to check.
        # We don't actually care about the corresponding value, just the dict key. So we set to an arbitrary "True".
        handled_tiles[get_id_from_tile(curr_tile)] = True

        # Check if adjacent tiles are accessible.
        start_tile_x, start_tile_y = curr_tile.sprite.tile
        if not curr_tile.walls.has_wall_north:
            # Verify we haven't already checked this tile in a previous loop.
            neig_tile_x = start_tile_x
            neig_tile_y = start_tile_y - 1
            neig_id = get_id_from_coord(neig_tile_x, neig_tile_y)
            try:
                handled_tiles[neig_id]
            except KeyError:
                # North tile is accessible and not yet handled. Check distance.
                distance = calc_distance_cost(neig_tile_x, neig_tile_y, end_tile_x, end_tile_y)
                tile_id = '{0}, {1}'.format(neig_tile_x, neig_tile_y)

                # Add to priority queue.
                _add_to_priority_queue(tile_id, distance)

                # Update our handled_tiles dict to include this tile.
                handled_tiles[neig_id] = True

                # Optionally display debug tile sprites.
                if debug:
                    debug_tile_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('search_overlay.png'))
                    DebugTile(data_manager.world, debug_tile_sprite, data_manager, neig_tile_x, neig_tile_y)
                    debug_tile_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('search_overlay.png'))
                    DebugTile(data_manager.world, debug_tile_sprite, data_manager, end_tile_x, end_tile_y)

        if not curr_tile.walls.has_wall_east:
            # Verify we haven't already checked this tile in a previous loop.
            neig_tile_x = start_tile_x + 1
            neig_tile_y = start_tile_y
            neig_id = get_id_from_coord(neig_tile_x, neig_tile_y)
            try:
                handled_tiles[neig_id]
            except KeyError:
                # East tile is accessible and not yet handled. Check distance.
                distance = calc_distance_cost(neig_tile_x, neig_tile_y, end_tile_x, end_tile_y)
                tile_id = '{0}, {1}'.format(neig_tile_x, neig_tile_y)

                # Add to priority queue.
                _add_to_priority_queue(tile_id, distance)

                # Update our handled_tiles dict to include this tile.
                handled_tiles[neig_id] = True

                # Optionally display debug tile sprites.
                if debug:
                    debug_tile_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('search_overlay.png'))
                    DebugTile(data_manager.world, debug_tile_sprite, data_manager, neig_tile_x, neig_tile_y)
                    debug_tile_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('search_overlay.png'))
                    DebugTile(data_manager.world, debug_tile_sprite, data_manager, end_tile_x, end_tile_y)

        if not curr_tile.walls.has_wall_south:
            # Verify we haven't already checked this tile in a previous loop.
            neig_tile_x = start_tile_x
            neig_tile_y = start_tile_y + 1
            neig_id = get_id_from_coord(neig_tile_x, neig_tile_y)
            try:
                handled_tiles[neig_id]
            except KeyError:
                # South tile is accessible and not yet handled. Check distance.
                distance = calc_distance_cost(neig_tile_x, neig_tile_y, end_tile_x, end_tile_y)
                tile_id = '{0}, {1}'.format(neig_tile_x, neig_tile_y)

                # Add to priority queue.
                _add_to_priority_queue(tile_id, distance)

                # Update our handled_tiles dict to include this tile.
                handled_tiles[neig_id] = True

                # Optionally display debug tile sprites.
                if debug:
                    debug_tile_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('search_overlay.png'))
                    DebugTile(data_manager.world, debug_tile_sprite, data_manager, neig_tile_x, neig_tile_y)
                    debug_tile_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('search_overlay.png'))
                    DebugTile(data_manager.world, debug_tile_sprite, data_manager, end_tile_x, end_tile_y)

        if not curr_tile.walls.has_wall_west:
            # Verify we haven't already checked this tile in a previous loop.
            neig_tile_x = start_tile_x - 1
            neig_tile_y = start_tile_y
            neig_id = get_id_from_coord(neig_tile_x, neig_tile_y)
            try:
                handled_tiles[neig_id]
            except KeyError:
                # West tile is accessible and not yet handled. Check distance.
                distance = calc_distance_cost(neig_tile_x, neig_tile_y, end_tile_x, end_tile_y)
                tile_id = '{0}, {1}'.format(neig_tile_x, neig_tile_y)

                # Add to priority queue.
                _add_to_priority_queue(tile_id, distance)

                # Update our handled_tiles dict to include this tile.
                handled_tiles[neig_id] = True

                # Optionally display debug tile sprites.
                if debug:
                    debug_tile_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('search_overlay.png'))
                    DebugTile(data_manager.world, debug_tile_sprite, data_manager, neig_tile_x, neig_tile_y)
                    debug_tile_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('search_overlay.png'))
                    DebugTile(data_manager.world, debug_tile_sprite, data_manager, end_tile_x, end_tile_y)

    def _add_to_priority_queue(tile_id, distance):
        """
        Creates new entry in priority queue datastructure.
        Data is entered in ascending distance order, so smaller distances will show first.

        Distance should be a combination of "tiles travelled so far" plus "distance left to reach tile, assuming no
        barriers exist between current tile and ending locations.
        :param tile_id: Id of tile to enter into queue.
        :param distance: Distance of tile to end-goal.
        """
        # Tell function to use variables in larger function scope.
        nonlocal priority_queue
        nonlocal handled_tiles
        # self.pending_list.append({'tile': start_tile, 'cost': start_cost})

        # Iterate through priority queue until we find proper location.
        added = False
        for index in range(len(priority_queue)):

            # Check if value is equal or lesser distance.
            if priority_queue[index]['cost'] >= distance:
                priority_queue.insert(index, {'id': tile_id, 'cost': distance})
                added = True
                break

        # Check if went through entire queue and failed to add. Means it's greater than all other values in queue.
        if not added:
            priority_queue.append({'id': tile_id, 'cost': distance})

    # Call actual function logic, now that inner functions are defined.
    _calc_trash_distances()

# endregion General Logic Functions
