"""
Living entities that have sprites and display to renderer window.

Sprite Depth Values (0 is lowest. Higher values will display ontop of lower ones):
 * Roomba: 4
 * TrashBall: 3
 * Active Wall: 2
 * Floor Tile: 1
 * Hidden/Unused Sprites: 0
"""

# System Imports.
import sdl2.ext

# User Imports.
from .system_entities import AI, Movement, TrashPile, Walls
from src.logging import init_logging


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
        self.sprite.depth = 4


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
        self.sprite.depth = 1

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
        self.sprite.depth = 0


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
                print('\n\n')
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

                print('\n\n')

            # Set full row to tile set.
            self.tiles.append(curr_row)

        print('\n\n\n\n')
        print('graph.number_of_nodes(): {0}\n'.format(data_manager.graph.number_of_nodes()))
        print('graph.number_of_edges(): {0}\n'.format(data_manager.graph.number_of_edges()))
        print('graph.nodes(): {0}\n'.format(data_manager.graph.nodes()))
        print('graph.edges(): {0}\n'.format(data_manager.graph.edges()))
        print('graph.neighbors(1, 1): {0}\n'.format(list(data_manager.graph.neighbors('1, 1'))))

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

        print('tile: {0}, {1}'.format(tile_x, tile_y))

        # Check if we get north neighboring tile id.
        if north_neighbor:
            print('    getting north neighbor')
            if tile_y > 0:
                tile_y = tile_y - 1
            else:
                raise ValueError('Tile "{0}, {1}" does not have northern neighbor!'.format(tile_x, tile_y))

        # Check if we get east neighboring tile id.
        if east_neighbor:
            print('    getting east neighbor')
            if tile_x < self.data_manager.tile_data['tile_w_count'] - 1:
                tile_x = tile_x + 1
            else:
                raise ValueError('Tile "{0}, {1}" does not have eastern neighbor!'.format(tile_x, tile_y))

        # Check if we get south neighboring tile id.
        if south_neighbor:
            print('    getting south neighbor')
            if tile_y < self.data_manager.tile_data['tile_h_count'] - 1:
                tile_y = tile_y + 1
            else:
                raise ValueError('Tile "{0}, {1}" does not have southern neighbor!'.format(tile_x, tile_y))

        # Check if we get west neighboring tile id.
        if west_neighbor:
            print('    getting west neighbor')
            if tile_x > 0:
                tile_x = tile_x - 1
            else:
                raise ValueError('Tile "{0}, {1}" does not have western neighbor!'.format(tile_x, tile_y))

        # Convert into expected format.
        id = '{0}, {1}'.format(tile_x, tile_y)
        print('    found_id: "{0}"'.format(id))
        return id

    def randomize_tile_walls(self):
        """
        Randomizes walls on all tiles, while still abiding by wall validation logic.
        """
        logger.info('Function not implemented yet!')

    def randomize_trash(self):
        """
        Randomizes trash entities on all tiles.
        """
        logger.info('Function not implemented yet!')


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
        self.sprite.depth = 0
