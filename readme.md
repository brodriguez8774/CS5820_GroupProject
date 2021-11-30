
# Python - Roomba AI Simulator


## Description
A virtual roomba/vacuum AI project.

Simulates a vacuum cleaner AI attempting to clean up a virtual room.


## Languages
Written using Python3.9. Tested in Ubuntu20.


## Installation
First, set up a Python "virtual environment" (see
https://git.brandon-rodriguez.com/python/example_projects/virtual_environments).

Then in a terminal with said environment, change to project root and run:

    pip install -r requirements.txt


### Known installation issue on Ubuntu20 VirtualBox VMs

You may run into an error when trying to install the `fclist` package, even when using Python3.9. In such a case, open
up the requirements.txt file and comment the `fclist` line out. Then uncomment the `fclist-cffi` line.

These packages appear to be interchangable, and doing this seems to allow package installation. The `fclist` package is
still set as the default, if only because we've tested project runtime much more thoroughly with this package.


## Running the Project
In a terminal with the above virtual environment loaded, change to project root and run:

    python ./main.py


## Using the Project

### Project Options
On launching program, the right-hand side has multiple settings buttons. The are as follows:
* Toggle AI - Turns AI on/off. Defaults to off.
* Toggle Failure - Turns "roomba failure mode" on/off. Defaults to off. The "failure mode" means a 10% chance of
creating a trash pile, upon leaving any given tile.
* Randomize Walls (E) - Places randomized walls on tiles. Every possible wall configuration has equal chance.
* Randomize Walls (W) - Places randomized walls on tiles. Tiles are slightly weighted to prefer certain wall
configurations.
* Randomize Trash - Places trash randomly on tiles. Tends towards a roughly 10% chance of placing trash on any given
tile.
* Bump Sensor - Gives AI the "bump sensor" movement configuration.
* Distance of 2 - Gives AI the "partial vision (range of 2)" movement configuration.
* Distance of 4 - Gives AI the "partial vision (range of 4)" movement configuration.
* Full Vision - Gives AI the "full vision" movement configuration.

### Tile Interactions
Clicking any tile will change the walls of that tile:
* Left click - Walks forward through wall options.
* Middle click - Adds trash if no walls on tile. Removes trash if present on tile. Otherwise, resets tile to have no
walls.
* Right click - Walks backward through wall options.
* Arrow Keys/ASDW Keys - Move roomba manually.

### Other
While not accessible through the GUI on project launch, the program window size can be adjusted via the
(WINDOW_WIDTH, WINDOW_HEIGHT) variables at the top of main.py.

Larger window sizes will automatically scale the program to generate a larger tileset.

WARNING: Program in current state is not efficient with many tiles. Increasing from default may potentially cause
lag/slow program execution.


## Project Logic

### Base Logic
Roomba cannot move through walls.<br>
Upon occupying the same tile as a trash pile, the roomba will remove the trash.<br>
Any tiles on the outer edge of the grid MUST have a wall along the outer border.

### Algorithms
For sake of the program AI being able to navigate, it needs to determine pathing between tiles.<br>
Upon placing/changing/removing any wall or trash entities, the program will recalculate pathing.<br>

Pathing is calculated in two parts:
* First, program uses A* algorithm to calculate the "optimal path" between every trash tile to every other trash tile.
Unfortunately, with many trash tiles present, this can be expensive.
  * Could theoretically be optimized via something like multithreading.
  * Implementation itself also likely could be optimized in places.
* Once the A* logic is complete, program then uses a semi-naive "TravelingSalesman" algorithm to determine the best path
that visits all trash tiles at least once, starting from the current roomba location.
  * This algorithm was more complicated than expected, and no actual outside references were used to figure it out.
  * Implementation can definitely be improved in some aspects, but at least it seems to give an acceptable solution
  a majority of the time.

On roomba movement event, only the TravelingSalesman algorithm is recalculated, in hopes of finding a better path than
the previously found solution. If no better solution is found, then previous solution is kept.

### AI Modes
As mentioned above in "project options", the AI has four possible movement modes.<br>
For all below modes, "performance" is described as "the final roomba movement count to gather all trash tiles, compared
to the hypothetical expected count as determined by TravelingSalesman."


Descriptions are as follows:
* Bump Sensor Movement - A very naive movement system. Roomba cannot see any tiles other than the one it's directly on.
It attempts to continue in a single direction until it hits a wall. Then it chooses a random alternate direction.
  * Roomba will only backtrack if walls surround all three other directions.
  * Very poor performance. AI is not smart at all, and can easily "get stuck". For most configurations, AI is never able
  to grab all trash tiles.
* Full Vision - Roomba is able to "see" the full set of tiles, such as if being fed information about the environment
from an outside source. Roomba will directly follow the "optimal path" as determined by the TravelingSalesman algorithm.
  * In most cases, performance is very good. Is also always able to reach every trash tile, with enough movements.
* Partial Vision Movement - A middle ground between "bump sensor" and "full vision".
  * Can have a vision range of either 2 or 4 tiles.
  * If a trash tile is within vision range, then temporarily uses the TravelingSalesman pathing until either the trash
  tile is picked up, or the trash tile is out of vision range again.
  * If no trash tiles are in range, then reverts back to "bump sensor" movement as a default, at least until a trash
  tile ends up in range once more.
  * For easier implementation, roomba "has x-ray vision" in this mode, and vision goes through walls.
  * Performance and ability to "grab all trash tiles" varies greatly, depending on vision range and environment
  layout. Seems to generally be able to grab all trash tiles (and obviously does better with larger vision), but will
  get stuck sometimes.


None of the above AI movement modes track "tiles visited" in any manner. The "less intelligent" the movement is, the
less it tracks "desired future movement" as well.

Some AI modes, particularly the "less intelligent" ones could probably be greatly improved by implementing some kind of
"track tiles visited" logic. It would likely help significantly with the roomba "getting stuck" or otherwise "being
unable to visit all trash tiles".


## Other Notes
Early on, I expected to need a literal graph data structure. However, the original structure of data ended up being
sufficient for the needs of this program. The graph data structure is being created, but only minimally referenced.

Ideally, one of two things should happen:
* The graph data structure and all references to it should be taken out. This would likely be easiest.
* Entire program data should be reworked to almost exclusively use the graph data structure, instead of current custom
class structure. This might be a lot of work, for minimal to no benefit (at least none visible at the current time).


## References
See `documents/references.md`.
