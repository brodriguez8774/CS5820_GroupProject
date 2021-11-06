"""
World system definitions.
These are subsystems added to the "world manager" object, that basically control actions being taken on each event tick.
"""

# System Imports.
import random
import sdl2.ext
from abc import ABC

# User Imports.
from src.entities.system_entities import AI, Movement
from src.logging import init_logging
from src.misc import calc_trash_distances, calc_traveling_salesman, get_tile_coord_from_id


# Initialize logger.
logger = init_logging(__name__)


class SoftwareRendererSystem(sdl2.ext.SoftwareSpriteRenderSystem):
    """
    System that handles displaying sprites to renderer window.
    """
    def __init__(self, window):
        self.data_manager = None
        super(SoftwareRendererSystem, self).__init__(window)

    def render(self, components):
        # Run tick to update general interface.
        sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super(SoftwareRendererSystem, self).render(components)

        # Also update dynamic GUI text elements.
        # Set "optimal calculated solution" text.
        self.data_manager.gui.optimal_counter_text.update(
            'Optimal Solution Cost: {0}'.format(self.data_manager.gui_data['optimal_counter']),
        )
        # Set "total moves taken" counter text.
        self.data_manager.gui.total_move_counter_text.update(
            'Moves: {0}'.format(self.data_manager.gui_data['total_move_counter']),
        )
        # Set "current ai search setting" text.
        ai_setting_text = 'AI Setting: {0}'
        if self.data_manager.roomba_vision == 0:
            ai_setting_text = ai_setting_text.format('Bump Sensor (0 Vision)')
        elif self.data_manager.roomba_vision < 0:
            ai_setting_text = ai_setting_text.format('Full Vision')
        else:
            ai_setting_text = ai_setting_text.format('{0} Tiles of Vision'.format(self.data_manager.roomba_vision))
        self.data_manager.gui.ai_setting_text.update(ai_setting_text)
        # Set "can fail" text.
        self.data_manager.gui.ai_failure_text.update(
            'Failure Chance: {0}'.format('10%' if self.data_manager.ai_can_fail else '0%'),
        )


class AbstractMovementSystem(ABC):
    """
    Holds general "movement logic".
    """
    def move_north(self, sprite):
        """
        Move entity north (upward).
        :param sprite: Entity sprite data.
        :return: True on movement success | False otherwise.
        """
        orig_location = sprite.y
        orig_x, orig_y = sprite.tile

        # Get corresponding tile wall data.
        tile_walls = self.data_manager.tile_set.tiles[orig_y][orig_x].walls

        # Check if direction is free of obstructions.
        if not tile_walls.has_wall_north:
            # Set new sprite location, for movement attempt.
            sprite.y -= 50

            # Verify that sprite's new location is within north (upper) bounds.
            # We use the more restrictive of either "the provided limit class limit" or "defined window limit".
            north_max = max(self.min_x, self.data_manager.tile_data['max_pixel_north'])
            sprite.y = max(north_max, sprite.y)

        # Check if movement occurred.
        if orig_location != sprite.y:
            # Call general "movement" logic, for entity having moved in any direction at all.
            logger.debug('Moved north.')
            self._handle_move(sprite, orig_x, orig_y)

            # Movement successful.
            return True
        else:
            # Movement failed. Some barrier was in the way.
            return False

    def move_east(self, sprite):
        """
        Move entity east (right).
        :param sprite: Entity sprite data.
        :return: True on movement success | False otherwise.
        """
        orig_location = sprite.x
        orig_x, orig_y = sprite.tile

        # Get corresponding tile wall data.
        tile_walls = self.data_manager.tile_set.tiles[orig_y][orig_x].walls

        # Check if direction is free of obstructions.
        if not tile_walls.has_wall_east:
            # Set new sprite location, for movement attempt.
            sprite.x += 50

            # Get sprite size in pixels.
            sprite_width, sprite_height = sprite.size

            # Verify that sprite's new location is within east (right) bounds.
            # We use the more restrictive of either "the provided limit class limit" or "defined window limit".
            sprite_right = sprite.x + sprite_width
            east_max = min(self.max_x, self.data_manager.tile_data['max_pixel_east'])
            if sprite_right > east_max:
                sprite.x = east_max - sprite_width

        # Check if movement occurred.
        if orig_location != sprite.x:
            # Call general "movement" logic, for entity having moved in any direction at all.
            logger.debug('Moved east.')
            self._handle_move(sprite, orig_x, orig_y)

            # Movement successful.
            return True
        else:
            # Movement failed. Some barrier was in the way.
            return False

    def move_south(self, sprite):
        """
        Move entity south (down).
        :param sprite: Entity sprite data.
        :return: True on movement success | False otherwise.
        """
        orig_location = sprite.y
        orig_x, orig_y = sprite.tile

        # Get corresponding tile wall data.
        tile_walls = self.data_manager.tile_set.tiles[orig_y][orig_x].walls

        # Check if direction is free of obstructions.
        if not tile_walls.has_wall_south:
            # Set new sprite location, for movement attempt.
            sprite.y += 50

            # Get sprite size in pixels.
            sprite_width, sprite_height = sprite.size

            # Verify that sprite's new location is within south (bottom) bounds.
            # We use the more restrictive of either "the provided limit class limit" or "defined window limit".
            sprite_lower = sprite.y + sprite_height
            south_max = min(self.max_y, self.data_manager.tile_data['max_pixel_south'])
            if sprite_lower > south_max:
                sprite.y = south_max - sprite_height

        # Check if movement occurred.
        if orig_location != sprite.y:
            # Call general "movement" logic, for entity having moved in any direction at all.
            logger.debug('Moved south.')
            self._handle_move(sprite, orig_x, orig_y)

            # Movement successful.
            return True
        else:
            # Movement failed. Some barrier was in the way.
            return False

    def move_west(self, sprite):
        """
        Move entity west (left).
        :param sprite: Entity sprite data.
        :return: True on movement success | False otherwise.
        """
        orig_location = sprite.x
        orig_x, orig_y = sprite.tile

        # Get corresponding tile wall data.
        tile_walls = self.data_manager.tile_set.tiles[orig_y][orig_x].walls

        # Check if direction is free of obstructions.
        if not tile_walls.has_wall_west:
            # Set new sprite location, for movement attempt.
            sprite.x -= 50

            # Verify that sprite's new location is within west (left) bounds.
            # We use the more restrictive of either "the provided limit class limit" or "defined window limit".
            west_max = max(self.min_x, self.data_manager.tile_data['max_pixel_west'])
            sprite.x = max(west_max, sprite.x)

        # Check if movement occurred.
        if orig_location != sprite.x:
            # Call general "movement" logic, for entity having moved in any direction at all.
            logger.debug('Moved west.')
            self._handle_move(sprite, orig_x, orig_y)

            # Movement successful.
            return True
        else:
            # Movement failed. Some barrier was in the way.
            return False

    def _handle_move(self, sprite, orig_x, orig_y):
        """
        Generalized logic that applies upon roomba moving in any direction.
        :param sprite: Entity sprite data.
        """
        # Update entity internal tile location.
        tile_x = int((sprite.x - self.data_manager.tile_data['max_pixel_west']) / 50)
        tile_y = int((sprite.y - self.data_manager.tile_data['max_pixel_north']) / 50)
        sprite.tile = tile_x, tile_y

        # Handle if trash exists on tile.
        curr_tile = self.data_manager.tile_set.tiles[tile_y][tile_x]
        roomba_location = self.data_manager.roomba.sprite.tile
        logger.debug('roomba_location: {0}'.format(roomba_location))
        if roomba_location[0] == tile_x and roomba_location[1] == tile_y and curr_tile.trashpile.exists:
            curr_tile.trashpile.clean()

        # Handle if roomba is set to allow "failing".
        # Such an instance causes 10% chance of trash pile appearing in square roomba just left.
        roomba_failed = False
        if self.data_manager.ai_can_fail:
            roomba_failed = self._trigger_failure(orig_x, orig_y)

        # Recalculate path distances for new roomba location.
        calc_trash_distances(self.data_manager, roomba_only=(not roomba_failed))
        calc_traveling_salesman(self.data_manager, calc_new=roomba_failed, total_move_reset=False)

        # Update for a movement.
        self.data_manager.gui_data['total_move_counter'] += 1

    def _trigger_failure(self, tile_x, tile_y):
        """
        If toggled on, roomba has 10% chance of "failing" upon leaving any square.
        Causes roomba to generate a new trash pile in square it was just in.
        :return: True if roomba failure occurred | False otherwise.
        """
        if random.randint(0, 9) < 1:
            # Trigger failure.
            self.data_manager.tile_set.tiles[tile_y][tile_x].trashpile.place()
            return True
        return False


class MovementSystem(sdl2.ext.Applicator, AbstractMovementSystem):
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
        """
        System handling during a single world processing tick.
        :param world: World instance calling the process tick.
        :param componenttypes: Tuple of relevant tuples for system.
        """
        for movement_tick, sprite in componenttypes:
            # Calculate tile location from pixels.
            pos_x = sprite.x
            pos_y = sprite.y
            tile_x = int((pos_x - self.data_manager.tile_data['max_pixel_west']) / 50)
            tile_y = int((pos_y - self.data_manager.tile_data['max_pixel_north']) / 50)
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


class AISystem(sdl2.ext.Applicator, AbstractMovementSystem):
    """
    System that handles roomba AI.
    """
    def __init__(self, data_manager, min_x, min_y, max_x, max_y):
        # Call parent logic.
        super().__init__()

        # Save component types values. Necessary for SDL2 system handling.
        self.componenttypes = AI, sdl2.ext.Sprite

        # Save class variables.
        self.data_manager = data_manager
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.prev_direction = 'north'

    def process(self, world, componenttypes):
        """
        System handling during a single world processing tick.
        :param world: World instance calling the process tick.
        :param componenttypes: Tuple of relevant tuples for system.
        """
        for ai_tick, sprite in componenttypes:

            # Proceed if tick rate is met and ai is set to be active..
            if ai_tick.active and ai_tick.check_counter() and self.data_manager.ai_active:
                # AI is active and tick event is occurring. Move roomba, based on current setting.

                # Check vision range.
                if self.data_manager.roomba_vision == 0:
                    # Roomba has no vision range. Acting as bump sensor.
                    logger.info('Moving with "bump sensor".')
                    self.move_bump_sensor(sprite)

                elif self.data_manager.roomba_vision == -1:
                    # Roomba has full tile sight.
                    logger.info('Moving with "full tile sight".')
                    self.move_full_sight(sprite)

                else:
                    # Roomba has limited tile range.
                    logger.info('Moving with "limited tile range".')
                    self.move_limited_vision(sprite)

    def move_bump_sensor(self, sprite):
        """
        Move roomba with "bump sensor" setting.

        Roomba will attempt to "continue in the same direction" until it hits a wall.
        At such a point, it will choose a random non-backtracking direction and attempt that.
        Only backtracks when no other valid options exist.
        :param sprite: Roomba sprite entity.
        """
        orig_x, orig_y = sprite.tile
        logger.debug('current_location: ({0}, {1})'.format(orig_x, orig_y))

        # First check previous direction. Attempt to continue going that way, if possible.
        has_moved = False
        if self.prev_direction == 'north':
            # Attempt to move roomba.
            logger.debug('Attempting to continue north.')
            has_moved = self.move_north(sprite)
        elif self.prev_direction == 'east':
            # Attempt to move roomba.
            logger.debug('Attempting to continue east.')
            has_moved = self.move_east(sprite)
        elif self.prev_direction == 'south':
            # Attempt to move roomba.
            logger.debug('Attempting to continue south.')
            has_moved = self.move_south(sprite)
        elif self.prev_direction == 'west':
            # Attempt to move roomba.
            logger.debug('Attempting to continue west.')
            has_moved = self.move_west(sprite)

        # Check if roomba has moved. If not, a barrier was in the way. Choose a random direction.
        if not has_moved:
            # Failed to move. Get new direction.
            prev_direction = self.prev_direction
            viable_directions = ['north', 'east', 'south', 'west']
            logger.debug('prev_direction: {0}'.format(prev_direction))
            logger.debug('viable_directions: {0}'.format(viable_directions))
            if self.prev_direction in ['north', 'south']:
                viable_directions.remove('north')
                viable_directions.remove('south')
            elif self.prev_direction in ['east', 'west']:
                viable_directions.remove('east')
                viable_directions.remove('west')

            # Attempt one of the other directions.
            while not has_moved and len(viable_directions) > 0:
                logger.debug('viable_directions: {0}'.format(viable_directions))
                new_dir_index = random.randint(0, len(viable_directions) - 1)
                new_dir = viable_directions.pop(new_dir_index)
                logger.debug('new_dir: {0}'.format(new_dir))

                if new_dir == 'north':
                    # Attempt to move roomba.
                    has_moved = self.move_north(sprite)
                    prev_direction = 'north'
                elif new_dir == 'east':
                    # Attempt to move roomba.
                    has_moved = self.move_east(sprite)
                    prev_direction = 'east'
                elif new_dir == 'south':
                    # Attempt to move roomba.
                    has_moved = self.move_south(sprite)
                    prev_direction = 'south'
                elif new_dir == 'west':
                    # Attempt to move roomba.
                    has_moved = self.move_west(sprite)
                    prev_direction = 'west'

            # Check one last time if roomba has moved.
            if not has_moved:
                logger.debug('Still has not moved, backtracking.')
                # Roomba still has not moved. That means three walls are blocked off on tile, and the only way
                # to move is by backtracking.
                if self.prev_direction == 'north':
                    # Attempt to move roomba.
                    has_moved = self.move_south(sprite)
                    prev_direction = 'south'
                elif self.prev_direction == 'east':
                    # Attempt to move roomba.
                    has_moved = self.move_west(sprite)
                    prev_direction = 'west'
                elif self.prev_direction == 'south':
                    # Attempt to move roomba.
                    has_moved = self.move_north(sprite)
                    prev_direction = 'north'
                elif self.prev_direction == 'west':
                    # Attempt to move roomba.
                    has_moved = self.move_east(sprite)
                    prev_direction = 'east'

            # Final validation that roomba has moved. If not, then logic error occurred.
            if not has_moved:
                raise RuntimeError('Roomba failed to move. Logic error occurred.')

            # Update for new movement direction.
            logger.debug('Setting "prev_direction" to {0}'.format(prev_direction))
            self.prev_direction = prev_direction

    def move_full_sight(self, sprite):
        """
        Move roomba with "full sight" setting.

        Assumes some "outside entity" knows what the full environment setup is, and is feeding the roomba this
        information. Roomba intelligently attempts to take the "most efficient path" to get to all trash piles.
        :param sprite: Roomba sprite entity.
        """
        # Get first set in "calculated ideal path".
        end_tile_group_id = self.data_manager.ideal_overall_path['ordering'][1]
        path_set = self.data_manager.ideal_trash_paths['roomba'][end_tile_group_id]

        # Get first tile in path set.
        curr_tile_id = path_set[0]
        desired_next_tile_id = path_set[1]
        curr_tile_x, curr_tile_y = get_tile_coord_from_id(curr_tile_id)
        desired_tile_x, desired_tile_y = get_tile_coord_from_id(desired_next_tile_id)

        # Determine which direction we move, in order to reach desired tile.
        if curr_tile_x != desired_tile_x:
            # Moving east/west.
            if curr_tile_x < desired_tile_x:
                # Move east.
                self.move_east(sprite)
                self.prev_direction = 'east'
            else:
                # Move west.
                self.move_west(sprite)
                self.prev_direction = 'west'
        elif curr_tile_y != desired_tile_y:
            # Moving north/south.
            if curr_tile_y < desired_tile_y:
                # Move south.
                self.move_south(sprite)
                self.prev_direction = 'south'
            else:
                # Move north.
                self.move_north(sprite)
                self.prev_direction = 'north'
        else:
            raise RuntimeError('Unable to determine where to move.')

    def move_limited_vision(self, sprite):
        """"""
        # Move roomba.
        self.move_east(sprite)
