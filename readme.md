
# Python - Roomba AI Simulator


## Description
A virtual roomba/vacuum AI project.

Simulates a vacuum cleaner AI attempting to clean up a virtual room.


## Installation
First, set up a Python "virtual environment" (see
https://git.brandon-rodriguez.com/python/example_projects/virtual_environments).

Then in a terminal with said environment, change to project root and run:

    pip install -r requirements.txt


## Running the Project
In a terminal with the above virtual environment loaded, change to project root and run:

    python ./main.py


## Using the Project
Currently, there is no AI involved. Project only has a barebones top-down grid-based environment, trash pile entities,
plus a "roomba" entity.


Clicking any tile will change the walls of that tile:
* Left click - Walks forward through wall options.
* Middle click - Adds trash if no walls on tile. Removes trash if present on tile. Otherwise, resets tile to have no
walls.
* Right click - Walks backward through wall options.


Roomba can be moved with standard arrow key movement (or asdw).<br>
Roomba cannot move through walls.<br>
Upon occupying the same tile as a trash pile, the roomba will remove the trash.


Any tiles on the outer edge of the grid MUST have a wall along the outer border.


Lastly, window size can be adjusted via the (WINDOW_WIDTH, WINDOW_HEIGHT) variables at the top of main.py.


## Helper Documentation/Tutorials

### SDL2 Library
* Official SDL2 Library Docs - <https://pysdl2.readthedocs.io/en/rel_0_9_7/tutorial/pong.html>
* Official SDL2 Library Examples - <https://github.com/marcusva/py-sdl2/tree/master/examples>
* Additional Repo of Various Examples - <https://github.com/caerus706/Python3-pySDL2-examples>
* Unfinished Random Tutorial, found via google searches -
<http://www.roguebasin.com/index.php/Complete_Roguelike_Tutorial,_using_python3%2Bpysdl2>
** Mostly used as reference in getting initial program logic setup. Cross-referencing examples can be helpful.
* Rendering Text, because there seem to be minimal good sources on it -
* <https://stackoverflow.com/questions/24709312/pysdl2-renderer-or-window-surface-for-handling-colors-and-text>

### Networkx Library
* Official Networkx Library Docs - <https://networkx.org/documentation/stable/reference/index.html>
