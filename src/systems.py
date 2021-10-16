"""
World system definitions.
These are subsystems added to the "world manager" object, that basically control actions being taken on each event tick.
"""

# System Imports.
import sdl2.ext

# User Imports.
from src.entities.system_entities import Movement


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
    def __init__(self, min_x, min_y, max_x, max_y):
        super(MovementSystem, self).__init__()
        self.componenttypes = Movement, sdl2.ext.Sprite
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def process(self, world, componenttypes):
        for movement_tick, sprite in componenttypes:
            # Get sprite size in pixels.
            sprite_width, sprite_height = sprite.size

            # Check if any movement directions are active for tick.
            if movement_tick.north:
                # Move north (upward).
                sprite.y -= 50
            elif movement_tick.east:
                # Move east (right).
                sprite.x += 50
            elif movement_tick.south:
                # Move south (down).
                sprite.y += 50
            elif movement_tick.west:
                # Move west (left).
                sprite.x -= 50

            # Reset movement tick values, now that we've handled for them.
            movement_tick.north = False
            movement_tick.east = False
            movement_tick.south = False
            movement_tick.west = False

            # Verify that sprite is still within left/upper screen bounds.
            sprite.x = max(self.min_x, sprite.x)
            sprite.y = max(self.min_y, sprite.y)

            # Verify that sprite is still within right/lower screen bounds.
            pmaxx = sprite.x + sprite_width
            pmaxy = sprite.y + sprite_height
            if pmaxx > self.max_x:
                sprite.x = self.max_x - sprite_width
            if pmaxy > self.max_y:
                sprite.y = self.max_y - sprite_height
