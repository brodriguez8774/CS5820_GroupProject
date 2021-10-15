"""

"""

# System Imports.
import sdl2.ext


class SoftwareRenderSystem(sdl2.ext.SoftwareSpriteRenderSystem):
    def __init__(self, window):
        super().__init__(window)

    def render(self, components):
        # sdl2.ext.fill(self.surface, sdl2.ext.Color(0, 0, 0))
        super().render(components)

    def process(self, world, components):
        """

        :param world:
        :param components:
        :return:
        """
        # print('processing things!')
        # for sprite in components:
        #     print('sprite: "{0}"'.format(sprite))
        # import time
        # time.sleep(5)


class EntityMovementSystem(sdl2.ext.Applicator):
    def __init__(self):
        super().__init__()

    def process(self, world, components):
        for sprite in components:
            print('sprite: "{0}"'.format(sprite))
