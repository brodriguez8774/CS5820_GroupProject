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
import networkx, random

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
        self.debug_entities = []
        self.gui = None
        self.tile_set = None
        self.roomba = None
        self.ideal_trash_paths = None
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
            if not tile.walls.check_has_extra_walls() and not tile.trashpile.exists:
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

        # Recalculate trash distances for new tile wall setup.
        data_manager.ideal_trash_paths = calc_trash_distances(data_manager)

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
    return distance


def calc_trash_distances(data_manager):
    """
    Calculates the "ideal" distance from every trash pile to every other trash pile.
    Accounts for walls and barriers.

    This function should be called every time any wall or trash entity is added/removed/otherwise changed.
    :param data_manager: Data manager data structure. Consolidates useful program data to one location.
    :return: Set of all calculated "ideal paths" from each trash tile to every other trash tile.
    """
    priority_queue = []
    handled_tiles = {}

    # Clear all debug entities.
    clear_debug_entities(data_manager)

    def _calc_trash_distances(debug=False):
        """
        Start of function logic.
        """
        # Tell function to use variables in larger function scope.
        nonlocal priority_queue
        nonlocal handled_tiles

        calculated_set = {}

        # Get list of all known trash piles.
        trash_tiles = data_manager.graph.data['trash_tiles']
        logger.info('trash_tiles: {0}'.format(trash_tiles))

        # Grab each tile with a trash pile.
        for start_tile_id in trash_tiles:
            # Add tile to final data structure.
            calculated_set[start_tile_id] = {}

            # Parse out coordinates for tile.
            start_tile_x, start_tile_y = get_tile_coord_from_id(start_tile_id)
            start_tile = get_tile_from_id(data_manager, start_tile_id)

            logger.debug('Calculating from tile ({0}, {1}):'.format(start_tile_x, start_tile_y))

            # Find distance from current trash pile to each other trash pile.
            for end_tile_id in trash_tiles:
                # Reset data structures for new tile.
                priority_queue = []
                handled_tiles = {}
                final_path = []

                # Ensure tiles are different.
                if start_tile_id != end_tile_id:
                    # Check if reverse path was already calculated.
                    try:
                        logger.debug('Attempting to get path ({0}) -> ({1})'.format(start_tile_id, end_tile_id))
                        final_path = calculated_set[end_tile_id][start_tile_id]

                        # If we got this far, then reverse path (end_tile -> start_tile) was already found.
                        # Invert and use that instead of re-calculating.
                        final_path = list(reversed(final_path))
                        logger.debug('    Path found: {0}'.format(final_path))

                        # Save path for future reference.
                        calculated_set[start_tile_id][end_tile_id] = final_path

                        # Skip to start of loop for next path calculation.
                        continue
                    except KeyError:
                        # Reverse path was not yet calculated.
                        # Calculate path to tiles from scratch.
                        logger.debug('    Path not found. Calculating from scratch.')

                    # Parse out coordinates for tile.
                    end_tile_x, end_tile_y = get_tile_coord_from_id(end_tile_id)

                    # Initialize queue by calculating first tile distance and setting as first element.
                    curr_id = get_id_from_tile(start_tile)
                    curr_path = [curr_id]
                    _calc_neighbor_costs(start_tile, end_tile_x, end_tile_y, 1, curr_path)
                    logger.debug('    to ({0}, {1}): {2}'.format(end_tile_x, end_tile_y, priority_queue))

                    # Iterate until we make it to our desired ending tile.
                    # Always use priority queue to check the shortest-distance tile.
                    iterate = True
                    while iterate:
                        # Parse out data for next tile.
                        curr_tile_data = priority_queue.pop(0)
                        curr_tile_id = curr_tile_data['id']
                        logger.debug('Handling {0}: {1}'.format(curr_tile_id, curr_tile_data))
                        curr_tile_backward_cost = curr_tile_data['backward_cost']
                        curr_tile_path = curr_tile_data['path']
                        curr_tile = get_tile_from_id(data_manager, curr_tile_id)

                        # Check if tile is at desired end position.
                        curr_tile_x, curr_tile_y = curr_tile.sprite.tile
                        if curr_tile_x == end_tile_x and curr_tile_y == end_tile_y:
                            # Found path. Stop checking further tiles.
                            final_path = curr_tile_path
                            iterate = False

                            # Save found path for future reference.
                            calculated_set[start_tile_id][end_tile_id] = final_path
                        else:
                            # Not yet at final tile.
                            # Calculate distance costs of fellow neighbor tiles.
                            _calc_neighbor_costs(
                                curr_tile,
                                end_tile_x,
                                end_tile_y,
                                curr_tile_backward_cost,
                                curr_tile_path,
                            )
                            logger.debug('    to ({0}, {1}): {2}'.format(end_tile_x, end_tile_y, priority_queue))

                    # Optionally display debug tile sprites.
                    if debug:
                        from src.entities.object_entities import DebugTile

                        # Loop through all found tiles in final path. Display debug sprites for each.
                        for tile_id in final_path:
                            tile_x, tile_y = get_tile_coord_from_id(tile_id)
                            debug_tile_sprite = data_manager.sprite_factory.from_image(
                                RESOURCES.get_path('search_overlay.png')
                            )
                            debug_entity = DebugTile(
                                data_manager.world,
                                debug_tile_sprite,
                                data_manager,
                                tile_x,
                                tile_y,
                            )
                            data_manager.debug_entities.append(debug_entity)

        calculated_set = _calc_roomba_distance(calculated_set, debug=debug)

        # Optionally print out calculated path set to console.
        if debug:
            logger.info('calculated_paths:')
            for start_tile_id, start_set in calculated_set.items():
                logger.info('({0})'.format(start_tile_id))
                for end_tile_id, calculated_path in start_set.items():
                    logger.info('    to ({0}):   {1}'.format(end_tile_id, calculated_path))
        else:
            # Print calculated path set to log files only.
            logger.debug('calculated_paths:')
            for start_tile_id, start_set in calculated_set.items():
                logger.debug('({0})'.format(start_tile_id))
                for end_tile_id, calculated_path in start_set.items():
                    logger.debug('    to ({0}):   {1}'.format(end_tile_id, calculated_path))

        return calculated_set

    def _calc_roomba_distance(calculated_set, debug=False):
        """"""
        # Tell function to use variables in larger function scope.
        nonlocal priority_queue
        nonlocal handled_tiles

        trash_tiles = data_manager.graph.data['trash_tiles']
        roomba_x, roomba_y = data_manager.roomba.sprite.tile
        roomba_tile_id = get_id_from_coord(roomba_x, roomba_y)
        roomba_tile = get_tile_from_id(data_manager, roomba_tile_id)

        calculated_set['roomba'] = {}

        # Find distance from current trash pile to each other trash pile.
        for end_tile_id in trash_tiles:
            # Reset data structures for new tile.
            priority_queue = []
            handled_tiles = {}
            final_path = []

            # Ensure tiles are different.
            if roomba_tile_id != end_tile_id:

                # Parse out coordinates for tile.
                end_tile_x, end_tile_y = get_tile_coord_from_id(end_tile_id)

                # Initialize queue by calculating first tile distance and setting as first element.
                curr_id = get_id_from_tile(roomba_tile)
                curr_path = [curr_id]
                _calc_neighbor_costs(roomba_tile, end_tile_x, end_tile_y, 1, curr_path)
                logger.debug('    to ({0}, {1}): {2}'.format(end_tile_x, end_tile_y, priority_queue))

                # Iterate until we make it to our desired ending tile.
                # Always use priority queue to check the shortest-distance tile.
                iterate = True
                while iterate:
                    # Parse out data for next tile.
                    curr_tile_data = priority_queue.pop(0)
                    curr_tile_id = curr_tile_data['id']
                    logger.debug('Handling {0}: {1}'.format(curr_tile_id, curr_tile_data))
                    curr_tile_backward_cost = curr_tile_data['backward_cost']
                    curr_tile_path = curr_tile_data['path']
                    curr_tile = get_tile_from_id(data_manager, curr_tile_id)

                    # Check if tile is at desired end position.
                    curr_tile_x, curr_tile_y = curr_tile.sprite.tile
                    if curr_tile_x == end_tile_x and curr_tile_y == end_tile_y:
                        # Found path. Stop checking further tiles.
                        final_path = curr_tile_path
                        iterate = False

                        # Save found path for future reference.
                        calculated_set['roomba'][end_tile_id] = final_path
                    else:
                        # Not yet at final tile.
                        # Calculate distance costs of fellow neighbor tiles.
                        _calc_neighbor_costs(
                            curr_tile,
                            end_tile_x,
                            end_tile_y,
                            curr_tile_backward_cost,
                            curr_tile_path,
                        )
                        logger.debug('    to ({0}, {1}): {2}'.format(end_tile_x, end_tile_y, priority_queue))

                # Optionally display debug tile sprites.
                if debug:
                    from src.entities.object_entities import DebugTile

                    # Loop through all found tiles in final path. Display debug sprites for each.
                    for tile_id in final_path:
                        tile_x, tile_y = get_tile_coord_from_id(tile_id)
                        debug_tile_sprite = data_manager.sprite_factory.from_image(
                            RESOURCES.get_path('search_overlay.png')
                        )
                        debug_entity = DebugTile(
                            data_manager.world,
                            debug_tile_sprite,
                            data_manager,
                            tile_x,
                            tile_y,
                        )
                        data_manager.debug_entities.append(debug_entity)

        return calculated_set

    def _calc_neighbor_costs(curr_tile, end_tile_x, end_tile_y, curr_backward_cost, curr_path, debug=False):
        """
        Calculate costs from neighbors of current tile, to desired ending tile coordinates.
        Skips any neighboring tiles that are blocked, such as by a wall.
        :param curr_tile: Tile entity to calculate from.
        :param end_tile_x: Desired ending x coordinates.
        :param end_tile_y: Desired ending y  coordinates.
        :param curr_backward_cost: Cost incurred so far to reach current tile.
        :param curr_path: Path taken to reach current tile.
        :param debug: Bool indicating if debug sprites should display.
        """
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
                forward_cost = calc_distance_cost(neig_tile_x, neig_tile_y, end_tile_x, end_tile_y)
                tile_id = '{0}, {1}'.format(neig_tile_x, neig_tile_y)

                # Add to priority queue.
                _add_to_priority_queue(tile_id, forward_cost, curr_backward_cost, curr_path)

                # Update our handled_tiles dict to include this tile.
                handled_tiles[neig_id] = True

                # Optionally display debug tile sprites.
                if debug:
                    debug_tile_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('search_overlay.png'))
                    debug_entity = DebugTile(
                        data_manager.world,
                        debug_tile_sprite,
                        data_manager,
                        neig_tile_x,
                        neig_tile_y,
                    )
                    data_manager.debug_entities.append(debug_entity)

        if not curr_tile.walls.has_wall_east:
            # Verify we haven't already checked this tile in a previous loop.
            neig_tile_x = start_tile_x + 1
            neig_tile_y = start_tile_y
            neig_id = get_id_from_coord(neig_tile_x, neig_tile_y)
            try:
                handled_tiles[neig_id]
            except KeyError:
                # East tile is accessible and not yet handled. Check distance.
                forward_cost = calc_distance_cost(neig_tile_x, neig_tile_y, end_tile_x, end_tile_y)
                tile_id = '{0}, {1}'.format(neig_tile_x, neig_tile_y)

                # Add to priority queue.
                _add_to_priority_queue(tile_id, forward_cost, curr_backward_cost, curr_path)

                # Update our handled_tiles dict to include this tile.
                handled_tiles[neig_id] = True

                # Optionally display debug tile sprites.
                if debug:
                    debug_tile_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('search_overlay.png'))
                    debug_entity = DebugTile(
                        data_manager.world,
                        debug_tile_sprite,
                        data_manager,
                        neig_tile_x,
                        neig_tile_y,
                    )
                    data_manager.debug_entities.append(debug_entity)

        if not curr_tile.walls.has_wall_south:
            # Verify we haven't already checked this tile in a previous loop.
            neig_tile_x = start_tile_x
            neig_tile_y = start_tile_y + 1
            neig_id = get_id_from_coord(neig_tile_x, neig_tile_y)
            try:
                handled_tiles[neig_id]
            except KeyError:
                # South tile is accessible and not yet handled. Check distance.
                forward_cost = calc_distance_cost(neig_tile_x, neig_tile_y, end_tile_x, end_tile_y)
                tile_id = '{0}, {1}'.format(neig_tile_x, neig_tile_y)

                # Add to priority queue.
                _add_to_priority_queue(tile_id, forward_cost, curr_backward_cost, curr_path)

                # Update our handled_tiles dict to include this tile.
                handled_tiles[neig_id] = True

                # Optionally display debug tile sprites.
                if debug:
                    debug_tile_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('search_overlay.png'))
                    debug_entity = DebugTile(
                        data_manager.world,
                        debug_tile_sprite,
                        data_manager,
                        neig_tile_x,
                        neig_tile_y,
                    )
                    data_manager.debug_entities.append(debug_entity)

        if not curr_tile.walls.has_wall_west:
            # Verify we haven't already checked this tile in a previous loop.
            neig_tile_x = start_tile_x - 1
            neig_tile_y = start_tile_y
            neig_id = get_id_from_coord(neig_tile_x, neig_tile_y)
            try:
                handled_tiles[neig_id]
            except KeyError:
                # West tile is accessible and not yet handled. Check distance.
                forward_cost = calc_distance_cost(neig_tile_x, neig_tile_y, end_tile_x, end_tile_y)
                tile_id = '{0}, {1}'.format(neig_tile_x, neig_tile_y)

                # Add to priority queue.
                _add_to_priority_queue(tile_id, forward_cost, curr_backward_cost, curr_path)

                # Update our handled_tiles dict to include this tile.
                handled_tiles[neig_id] = True

                # Optionally display debug tile sprites.
                if debug:
                    debug_tile_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('search_overlay.png'))
                    debug_entity = DebugTile(
                        data_manager.world,
                        debug_tile_sprite,
                        data_manager,
                        neig_tile_x,
                        neig_tile_y,
                    )
                    data_manager.debug_entities.append(debug_entity)

    def _add_to_priority_queue(tile_id, forward_cost, backward_cost, path):
        """
        Creates new entry in priority queue data structure.
        Data is entered in ascending distance order, so smaller distances will show first.

        Distance should be a combination of "tiles travelled so far" plus "distance left to reach tile, assuming no
        barriers exist between current tile and ending locations.
        :param tile_id: Id of tile to enter into queue.
        :param forward_cost: Distance of tile to end-goal.
        :param backward_cost: Distance travelled so far, to reach current tile.
        :param path: List of all tiles in current path to reach current location.
        """
        # Tell function to use variables in larger function scope.
        nonlocal priority_queue
        nonlocal handled_tiles
        # self.pending_list.append({'tile': start_tile, 'cost': start_cost})

        # Update current path set for new location.
        path = list(path)
        path.append(tile_id)

        # Calcualte distance values.
        curr_tile_distance = forward_cost + backward_cost
        backward_cost += 1

        # Iterate through priority queue until we find proper location.
        added = False
        for index in range(len(priority_queue)):

            # Check if value is equal or lesser distance.
            index_cost = priority_queue[index]['forward_cost'] + priority_queue[index]['backward_cost']
            if index_cost >= curr_tile_distance:
                priority_queue.insert(
                    index,
                    {'id': tile_id, 'forward_cost': forward_cost, 'backward_cost': backward_cost, 'path': path},
                )
                added = True
                break

        # Check if went through entire queue and failed to add. Means it's greater than all other values in queue.
        if not added:
            priority_queue.append(
                {'id': tile_id, 'forward_cost': forward_cost, 'backward_cost': backward_cost, 'path': path},
            )

    # Call actual function logic, now that inner functions are defined.
    return _calc_trash_distances()


def calc_traveling_salesman(data_manager, debug=False):
    """
    Calculates the approximately-ideal overall path to visit all trash tiles.
    :param data_manager:
    :return:
    """
    debug = True

    # Clear all debug entities.
    clear_debug_entities(data_manager)

    roomba_x, roomba_y = data_manager.roomba.sprite.tile
    roomba_tile_id = get_id_from_coord(roomba_x, roomba_y)
    trash_tile_set = data_manager.graph.data['trash_tiles']
    trash_paths = data_manager.ideal_trash_paths

    print('\n\n\n\n')
    print(' ==== TRAVELING SALESMAN ===== ')
    print('\n')
    print('trash_paths: {0}'.format(trash_paths))

    # Initialize path by just going to trash tiles in original ordering.
    curr_total_dist = 999999
    calculated_path = {
        'ordering': [roomba_tile_id],
        'total_cost': curr_total_dist,
    }
    start_tile_id = None
    end_tile_id = None
    for tile_id in trash_tile_set:
        start_tile_id = end_tile_id
        end_tile_id = tile_id

        # Add first trash tile.
        if not start_tile_id:
            calculated_path['ordering'].append(end_tile_id)

        # Add all other trash tiles after first one.
        if start_tile_id and end_tile_id:
            calculated_path['ordering'].append(end_tile_id)

    # Run ( "length of trash tile set" * 10 ) iterations.
    # For each, we randomly grab two sets of connected points, then swap them with each other to see if improvement
    # occurs. If swap leads to overall distance improvement, we save. Otherwise revert and try next iteration.
    for index_counter in range(len(trash_tile_set) * 10):
        # Grab first set of points.
        conn_1_index_0 = random.randint(0, len(calculated_path['ordering']) - 2)
        conn_1_index_1 = conn_1_index_0 + 1

        # Grab second set of points.
        conn_2_index_0 = random.randint(0, len(calculated_path['ordering']) - 2)
        conn_2_index_1 = conn_2_index_0 + 1
        temp_counter = 0
        # Make sure sets of point are actually different.
        while (
            temp_counter < 10 and   # If it fails 10 times, then we probably don't have enough indexes to actually swap.
            (
                conn_2_index_0 in [conn_1_index_0, conn_1_index_1] or
                conn_2_index_1 == [conn_1_index_0, conn_1_index_1]
            )
        ):
            conn_2_index_0 = random.randint(0, len(calculated_path['ordering']) - 2)
            conn_2_index_1 = conn_2_index_0 + 1
            temp_counter += 1

        # Get respective id's for selected indexes.
        conn_1_id_0 = calculated_path['ordering'][conn_1_index_0]
        conn_1_id_1 = calculated_path['ordering'][conn_1_index_1]
        conn_2_id_0 = calculated_path['ordering'][conn_2_index_0]
        conn_2_id_1 = calculated_path['ordering'][conn_2_index_1]

        # Verify swapping won't result in trying to travel from a tile to itself.
        if conn_1_id_0 == conn_2_id_1 or conn_2_id_0 == conn_1_id_1:
            # Would lead to bad path. Skip current iteration.
            continue

        # Calculate distance travelled for current selection.
        start_tile_id = None
        end_tile_id = None
        curr_total_dist = 0
        for index in range(len(calculated_path['ordering'])):
            start_tile_id = end_tile_id
            end_tile_id = calculated_path['ordering'][index]

            # Only proceed if both id's are present (aka, skip first index).
            if start_tile_id and end_tile_id:
                # Both present. Add length of path to overall length calculation.
                if start_tile_id == roomba_tile_id:
                    curr_total_dist += len(trash_paths['roomba'][end_tile_id]) - 1
                else:
                    curr_total_dist += len(trash_paths[start_tile_id][end_tile_id]) - 1

        # Swap and recalculate distance.
        swapped_total_dist = 0
        swapped_path = list(calculated_path['ordering'])
        swapped_path[conn_1_index_1] = conn_2_id_1
        swapped_path[conn_2_index_1] = conn_1_id_1
        start_tile_id = None
        end_tile_id = None
        for index in range(len(swapped_path)):
            start_tile_id = end_tile_id
            end_tile_id = swapped_path[index]

            # Only proceed if both id's are present (aka, skip first index).
            if start_tile_id and end_tile_id:
                # Both present. Add length of path to overall length calculation.
                if start_tile_id == roomba_tile_id:
                    swapped_total_dist += len(trash_paths['roomba'][end_tile_id]) - 1
                else:
                    swapped_total_dist += len(trash_paths[start_tile_id][end_tile_id]) - 1

        # Check if swapping sets will decrease overall distance travelled.
        if swapped_total_dist < curr_total_dist:
            calculated_path['ordering'][conn_1_index_1] = conn_2_id_1
            calculated_path['ordering'][conn_2_index_1] = conn_1_id_1

    # Optionally display debug tile sprites.
    if debug:
        from src.entities.object_entities import DebugTile

        # Loop through all found tiles in final path. Display debug sprites for each.
        start_tile_id = None
        end_tile_id = None
        for index in range(len(calculated_path['ordering'])):
            start_tile_id = end_tile_id
            end_tile_id = calculated_path['ordering'][index]

            # Only proceed if both id's are present (aka, skip first index).
            if start_tile_id and end_tile_id:

                # Loop through all tiles in path connecting the given trash entities.
                if start_tile_id == roomba_tile_id:
                    full_path = trash_paths['roomba'][end_tile_id]
                else:
                    full_path = trash_paths[start_tile_id][end_tile_id]
                for tile_id in full_path:
                    tile_x, tile_y = get_tile_coord_from_id(tile_id)
                    debug_tile_sprite = data_manager.sprite_factory.from_image(
                        RESOURCES.get_path('search_overlay.png')
                    )
                    debug_entity = DebugTile(
                        data_manager.world,
                        debug_tile_sprite,
                        data_manager,
                        tile_x,
                        tile_y,
                    )
                    data_manager.debug_entities.append(debug_entity)


def clear_debug_entities(data_manager):
    """
    Removes all debug entities, so that the screen does not become cluttered with redundant/overlapping debug info.
    :param data_manager: Data manager data structure. Consolidates useful program data to one location.
    """
    # Delete each entity so it no longer displays on render.
    for debug_entity in data_manager.debug_entities:
        debug_entity.delete()

    # Reset debug entity list.
    data_manager.debug_entities = []

# endregion General Logic Functions
