"""
Makes folder imports handle as if it was one single file.
"""

# Import gui entity data.
from .gui_entities import (
    GuiCore,
)

# Import object entity data.
from .object_entities import (
    Roomba,
    TileSet,
)

# Import system entity data.
from .system_entities import (
    AI,
    Movement,
)
