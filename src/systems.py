"""
World system definitions.
These are subsystems added to the "world manager" object, that basically control actions being taken on each event tick.
"""

# System Imports.
import sdl2.ext

# User Imports.
from src.entities.system_entities import Movement
from src.logging import init_logging


# Initialize logger.
logger = init_logging(__name__)


class SoftwareRendererSystem(sdl2.ext.SoftwareSpriteRenderSystem):
    """
    System that handles displaying sprites to renderer window.
    """
    def __init__(self, window):
        super(SoftwareRendererSystem, self).__init__(window)

    def render(self, components):
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRendererSystem, self).render(components)


class MovementSystem(sdl2.ext.Applicator):
    """
    System that handles movement of entities.
    """
    def __init__(self, data_manager, min_x, min_y, max_x, max_y):
        # Call parent logic.
        super().__init__()

        # Save component types values. Necessary for SDL2 system handling.
        self.componenttypes = Movement, sdl2.ext.Sprite

        # Save class variables.
        self.data_manager = data_manager
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def process(self, world, componenttypes):
        for movement_tick, sprite in componenttypes:
            # Calculate tile location from pixels.
            pos_x = sprite.x
            pos_y = sprite.y
            tile_x = int((pos_x - self.data_manager.sprite_data['max_pixel_west']) / 50)
            tile_y = int((pos_y - self.data_manager.sprite_data['max_pixel_north']) / 50)
            curr_tile = self.data_manager.tile_set.tiles[tile_y][tile_x]

            # Check if any movement directions are active for tick.
            if movement_tick.north and not curr_tile.walls.has_wall_north:
                self.move_north(sprite)

            elif movement_tick.east and not curr_tile.walls.has_wall_east:
                self.move_east(sprite)

            elif movement_tick.south and not curr_tile.walls.has_wall_south:
                self.move_south(sprite)

            elif movement_tick.west and not curr_tile.walls.has_wall_west:
                self.move_west(sprite)

            # Reset movement tick values, now that we've handled for them.
            movement_tick.north = False
            movement_tick.east = False
            movement_tick.south = False
            movement_tick.west = False

    def move_north(self, sprite):
        """
        Move entity north (upward).
        """
        sprite.y -= 50

        # Call general "movement" logic, for entity having moved in any direction at all.
        self._handle_move(sprite)

    def move_east(self, sprite):
        """
        Move entity east (right).
        :param sprite: Entity sprite data.
        """
        sprite.x += 50

        # Call general "movement" logic, for entity having moved in any direction at all.
        self._handle_move(sprite)

    def move_south(self, sprite):
        """
        Move entity south (down).
        :param sprite: Entity sprite data.
        """
        sprite.y += 50

        # Call general "movement" logic, for entity having moved in any direction at all.
        self._handle_move(sprite)

    def move_west(self, sprite):
        """
        Move entity west (left).
        :param sprite: Entity sprite data.
        """
        sprite.x -= 50

        # Call general "movement" logic, for entity having moved in any direction at all.
        self._handle_move(sprite)

    def _handle_move(self, sprite):
        """
        Generalized logic that applies upon roomba moving in any direction.
        :param sprite: Entity sprite data.
        """
        # Get sprite size in pixels.
        sprite_width, sprite_height = sprite.size

        # For below, we verify that sprite's new location is within bounds.
        # We use the more restrictive of either "the provided limit class limit" or "defined window limit".

        # Verify that sprite is still within north (upper) screen bounds.
        north_max = max(self.min_x, self.data_manager.sprite_data['max_pixel_north'])
        sprite.y = max(north_max, sprite.y)

        # Verify that sprite is still within east (right) screen bounds.
        sprite_right = sprite.x + sprite_width
        east_max = min(self.max_x, self.data_manager.sprite_data['max_pixel_east'])
        if sprite_right > east_max:
            sprite.x = east_max - sprite_width

        # Verify that sprite is still within south (bottom) screen bounds.
        sprite_lower = sprite.y + sprite_height
        south_max = min(self.max_y, self.data_manager.sprite_data['max_pixel_south'])
        if sprite_lower > south_max:
            sprite.y = south_max - sprite_height

        # Verify that sprite is still within west (left) screen bounds.
        west_max = max(self.min_x, self.data_manager.sprite_data['max_pixel_west'])
        sprite.x = max(west_max, sprite.x)

        # Update entity internal tile location.
        tile_x = int((sprite.x - self.data_manager.sprite_data['max_pixel_west']) / 50)
        tile_y = int((sprite.y - self.data_manager.sprite_data['max_pixel_north']) / 50)
        sprite.tile = tile_x, tile_y

        # Handle if trash exists on tile.
        curr_tile = self.data_manager.tile_set.tiles[tile_y][tile_x]
        roomba_location = self.data_manager.roomba.sprite.tile
        logger.debug('roomba_location: {0}'.format(roomba_location))
        if roomba_location[0] == tile_x and roomba_location[1] == tile_y and curr_tile.trashpile.exists:
            curr_tile.trashpile.clean()
