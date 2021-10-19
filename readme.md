
# Python - Roomba AI Simulator


## Description
A virtual roomba/vacuum AI project.

Simulate a vacuum cleaner AI attempting to clean up a virtual room.


## Installation
First, set up a Python "virtual environment" (see
https://git.brandon-rodriguez.com/python/example_projects/virtual_environments).

Then in a terminal with said environment, change to project root and run:

    pip install -r requirements.txt


## Running the Project
In a terminal with the above virtual environment loaded, change to project root and run:

    python ./main.py


## Using the Project
Currently, there is no AI involved. Project only has a barebones top-down grid-based environment, plus a "roomba"
entity.


Clicking any tile will change the walls of that tile:
* Left click - Walks forward through wall options.
* Middle click - Resets tile to have no walls.
* Right click - Walks backward through wall options.


Roomba can be moved with standard arrow key movement (or asdw).<br>
Roomba cannot move through walls.


Any tiles on the outer edge of the grid MUST have a wall along the outer border.


Lastly, window size can be adjusted via the (WINDOW_WIDTH, WINDOW_HEIGHT) variables at the top of main.py.


## Helper Documentation/Tutorials
* <https://pysdl2.readthedocs.io/en/rel_0_9_7/tutorial/pong.html>
* <http://www.roguebasin.com/index.php/Complete_Roguelike_Tutorial,_using_python3%2Bpysdl2>
