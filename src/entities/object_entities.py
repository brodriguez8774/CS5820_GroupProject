"""
Living entities that have sprites and display to renderer window.
"""

# System Imports.
import random

import sdl2.ext

# User Imports.
from .system_entities import AI, Movement, TrashPile, Search, Walls
from src.logging import init_logging
from src.misc import calc_trash_distances, calc_traveling_salesman


# Initialize logger.
logger = init_logging(__name__)


# Module Variables.
# Here, we point to our image files to render to user.
RESOURCES = sdl2.ext.Resources(__file__, '../images/')


class Roomba(sdl2.ext.Entity):
    """
    A roomba/vacuum entity.
    """
    def __init__(self, world, sprite, data_manager, tile_x=0, tile_y=0):
        # Set entity display image.
        self.sprite = sprite

        # Define world systems which affect entity.
        self.movement = Movement(data_manager)
        self.ai = AI(data_manager)

        # Set entity location tracking.
        self.sprite.tile = tile_x, tile_y
        self.sprite.position = self.movement.calculate_pix_from_tile(tile_x, tile_y)

        # Set entity depth mapping.
        self.sprite.depth = data_manager.sprite_depth['roomba']


class Tile(sdl2.ext.Entity):
    """
    A single tile, representing a single location in the environment.
    """
    def __init__(self, world, sprite, data_manager, tile_x=0, tile_y=0):
        # Set entity display image.
        self.sprite = sprite

        # Define world systems which affect entity.
        self.movement = Movement(data_manager)

        # Set entity location tracking.
        self.sprite.tile = tile_x, tile_y
        self.sprite.position = self.movement.calculate_pix_from_tile(tile_x, tile_y)

        # Set entity depth mapping.
        self.sprite.depth = data_manager.sprite_depth['floor_tile']

        # Initialize tile wall data.
        wall_sprite_north = data_manager.sprite_factory.from_image(RESOURCES.get_path('wall_north.png'))
        wall_sprite_east = data_manager.sprite_factory.from_image(RESOURCES.get_path('wall_east.png'))
        wall_sprite_south = data_manager.sprite_factory.from_image(RESOURCES.get_path('wall_south.png'))
        wall_sprite_west = data_manager.sprite_factory.from_image(RESOURCES.get_path('wall_west.png'))
        wall_data = {
            'north': TileWall(world, wall_sprite_north, data_manager, tile_x=tile_x, tile_y=tile_y),
            'east': TileWall(world, wall_sprite_east, data_manager, tile_x=tile_x, tile_y=tile_y),
            'south': TileWall(world, wall_sprite_south, data_manager, tile_x=tile_x, tile_y=tile_y),
            'west': TileWall(world, wall_sprite_west, data_manager, tile_x=tile_x, tile_y=tile_y),
        }
        self.walls = Walls(data_manager, tile_x, tile_y, wall_data)

        # Initialize tile trash data.
        trash_sprite = data_manager.sprite_factory.from_image(RESOURCES.get_path('trash.png'))
        trash_entity = Trash(world, trash_sprite, data_manager, tile_x, tile_y)
        self.trashpile = TrashPile(data_manager, trash_entity, tile_x, tile_y)


class DebugTile(sdl2.ext.Entity):
    """
    Debug rendering for a single tile.
    """
    def __init__(self, world, sprite, data_manager, tile_x=0, tile_y=0):
        # Set entity display image.
        self.sprite = sprite

        # Define world systems which affect entity.
        self.movement = Movement(data_manager)

        # Set entity location tracking.
        self.sprite.tile = tile_x, tile_y
        self.sprite.position = self.movement.calculate_pix_from_tile(tile_x, tile_y)

        # Set entity depth mapping.
        self.sprite.depth = data_manager.sprite_depth['debug_floor_tile']


class TileWall(sdl2.ext.Entity):
    """
    A single wall on a tile.
    Represents a barrier in one of the four directions (north, south, east, west).
    """
    def __init__(self, world, sprite, data_manager, tile_x=0, tile_y=0):
        # Set entity display image.
        self.sprite = sprite

        # Define world systems which affect entity.
        self.movement = Movement(data_manager)

        # Set entity location tracking.
        self.sprite.tile = tile_x, tile_y
        self.sprite.position = self.movement.calculate_pix_from_tile(tile_x, tile_y)

        # Set entity depth mapping. Defaults to 0 so it's hidden from view.
        self.sprite.depth = data_manager.sprite_depth['inactive']


class TileSet:
    """
    Holds/Generates set of all sprite tiles.
    """
    def __init__(self, data_manager):
        """
        :param data_manager: Data manager data structure. Consolidates useful program data to one location.
        """
        # Save class variables.
        self.data_manager = data_manager
        self.sprite_renderer = data_manager.sprite_renderer
        self.window_data = data_manager.window_data
        self.sprite_data = data_manager.tile_data
        self.tiles = []

        # Initialize all tiles.
        for row_index in range(self.sprite_data['tile_h_count']):

            # Initialize row of tiles.
            curr_row = []

            # Initialize each tile in row.
            for col_index in range(self.sprite_data['tile_w_count']):
                # Generate current tile.
                tile = Tile(
                    data_manager.world,
                    data_manager.sprite_factory.from_image(RESOURCES.get_path('background.png')),
                    data_manager,
                    tile_x=col_index,
                    tile_y=row_index,
                )
                # Update graph data structure for tile.
                node_id = self.get_tile_id(tile)
                data_manager.graph.add_node(node_id)
                if col_index > 0:
                    data_manager.graph.add_edge(node_id, self.get_tile_id(tile, west_neighbor=True), open=True)
                if row_index > 0:
                    data_manager.graph.add_edge(node_id, self.get_tile_id(tile, north_neighbor=True), open=True)

                # Add node to current row.
                curr_row.append(tile)

            # Set full row to tile set.
            self.tiles.append(curr_row)

        logger.info('')
        logger.info('graph.number_of_nodes(): {0}'.format(data_manager.graph.number_of_nodes()))
        logger.info('graph.number_of_edges(): {0}'.format(data_manager.graph.number_of_edges()))
        logger.info('graph.nodes(): {0}'.format(data_manager.graph.nodes(data=True)))
        logger.info('graph.edges(): {0}'.format(data_manager.graph.edges(data=True)))
        logger.info('graph.neighbors(1, 1): {0}'.format(list(data_manager.graph.neighbors('1, 1'))))
        logger.info('')

    def get_tile_from_id(self, tile_id):
        """"""
        tile_x = int(tile_id[0])
        tile_y = int(tile_id[3])

        return self.tiles[tile_y][tile_x]

    def get_tile_id(self, tile, north_neighbor=False, east_neighbor=False, south_neighbor=False, west_neighbor=False):
        """
        Returns the "graph node" identifier for corresponding tile.
        :param tile: Current tile to get id of.
        :param north_neighbor: Bool indicating if we instead get id of neighbor to direct north.
        :param east_neighbor: Bool indicating if we instead get id of neighbor to direct east.
        :param south_neighbor: Bool indicating if we instead get id of neighbor to direct south.
        :param west_neighbor: Bool indicating if we instead get id of neighbor to direct west.
        :return: Corresponding identifier for graph data structure.
        """
        # Validate kwargs.
        neighbor_check = 0
        if north_neighbor:
            neighbor_check += 1
        if east_neighbor:
            neighbor_check += 1
        if south_neighbor:
            neighbor_check += 1
        if west_neighbor:
            west_neighbor += 1

        if neighbor_check > 1:
            raise ValueError('Can only get neighbor in one direction, not multiple at once.')

        # Get coordinate values from tile.
        tile_x, tile_y = tile.sprite.tile

        logger.info('tile: {0}, {1}'.format(tile_x, tile_y))

        # Check if we get north neighboring tile id.
        if north_neighbor:
            logger.info('    getting north neighbor')
            if tile_y > 0:
                tile_y = tile_y - 1
            else:
                raise ValueError('Tile "{0}, {1}" does not have northern neighbor!'.format(tile_x, tile_y))

        # Check if we get east neighboring tile id.
        if east_neighbor:
            logger.info('    getting east neighbor')
            if tile_x < self.data_manager.tile_data['tile_w_count'] - 1:
                tile_x = tile_x + 1
            else:
                raise ValueError('Tile "{0}, {1}" does not have eastern neighbor!'.format(tile_x, tile_y))

        # Check if we get south neighboring tile id.
        if south_neighbor:
            logger.info('    getting south neighbor')
            if tile_y < self.data_manager.tile_data['tile_h_count'] - 1:
                tile_y = tile_y + 1
            else:
                raise ValueError('Tile "{0}, {1}" does not have southern neighbor!'.format(tile_x, tile_y))

        # Check if we get west neighboring tile id.
        if west_neighbor:
            logger.info('    getting west neighbor')
            if tile_x > 0:
                tile_x = tile_x - 1
            else:
                raise ValueError('Tile "{0}, {1}" does not have western neighbor!'.format(tile_x, tile_y))

        # Convert into expected format.
        id = '{0}, {1}'.format(tile_x, tile_y)
        logger.info('    found_id: "{0}"'.format(id))
        return id

    def randomize_tile_walls_equal(self):
        """
        Wrapper for wall randomization.
        Calls with all tile configurations having equal weight.
        """
        logger.info('Randomizing tile walls (equal randomization).')
        self._randomize_tile_walls(weighted=False)

    def randomize_tile_walls_weighted(self):
        """
        Wrapper for wall randomization.
        Calls with certain tile configurations having larger weights.
        Generally speaking, tiles walls will be more sparsely populated.
        """
        logger.info('Randomizing tile walls (weighted randomization).')
        self._randomize_tile_walls(weighted=True)

    def _randomize_tile_walls(self, weighted=False):
        """
        Randomizes walls on all tiles, while still abiding by wall validation logic.
        """
        # Get each tile row.
        for row_index in range(self.sprite_data['tile_h_count']):

            # Get each col in each row
            for col_index in range(self.sprite_data['tile_w_count']):

                # Set tile wall to random value.
                self.tiles[row_index][col_index].walls.randomize_walls(weighted=weighted)

        # Ensure all paths are accessible by roomba.
        self.tiles[0][0].walls.bipartite_color_validation()

        # Recalculate trash distances for new wall setup.
        self.data_manager.ideal_trash_paths = calc_trash_distances(self.data_manager)
        calc_traveling_salesman(self.data_manager)

    def randomize_trash(self):
        """
        Randomizes trash entities on all tiles.
        """
        logger.info('Randomizing trash entity placement.')

        # Get each tile row.
        for row_index in range(self.sprite_data['tile_h_count']):

            # Get each col in each row
            for col_index in range(self.sprite_data['tile_w_count']):
                # Modify tile trash existence. Roughly 10% chance of any tile having trash.
                if random.randint(0, 9) < 1:
                    # Place trash if not currently on tile.
                    if not self.tiles[row_index][col_index].trashpile.exists:
                        self.tiles[row_index][col_index].trashpile.place()
                else:
                    # Remove trash if present.
                    if self.tiles[row_index][col_index].trashpile.exists:
                        self.tiles[row_index][col_index].trashpile.clean()

        # Recalculate trash distances for new trash pile setup.
        self.data_manager.ideal_trash_paths = calc_trash_distances(self.data_manager)


class Trash(sdl2.ext.Entity):
    """
    An instance of "trash" occupying a single square.
    """
    def __init__(self, world, sprite, data_manager, tile_x=0, tile_y=0):
        # Set entity display image.
        self.sprite = sprite

        # Define world systems which affect entity.
        self.movement = Movement(data_manager)

        # Set entity location tracking.
        self.sprite.tile = tile_x, tile_y
        self.sprite.position = self.movement.calculate_pix_from_tile(tile_x, tile_y)

        # Set entity depth mapping. Defaults to 0 so it's hidden from view.
        self.sprite.depth = data_manager.sprite_depth['inactive']
