import time
import argparse

from model import Maze, Player
from algo import Generator, Pathfinder


class MazeGame:
    def __init__(self):
        self.maze, self.generator, self.mazeSpanningTree, self.player, self.pathfinder, self.solutionSize, \
            self.canPlay = None, None, None, None, None, None, None
        self.mazeDurTime, self.buildMazeCellsDurTime, self.solutionDurTime, self.printDurTime, self.markDurTime \
            = None, None, None, None, None

    def run(self, x=-1, y=-1, argsMsg=""):
        isRunning = True
        if x!=-1 and y!=-1:
            if x < 10 or y < 10:
                print(ERROR_MAZE_SIZE)
                x, y = self.getMazeSize(x, y)
            else:
                print(argsMsg)
            self.generateAndPrintMaze(x, y)
        while isRunning:
            try:
                match input(MENU):
                    case '0':
                        x, y = self.getMazeSize(0,0)
                        self.generateAndPrintMaze(x,y)
                    case '1':
                        if self.canPlay:
                            self.printMaze(True)
                            self.play()
                        else:
                            print(ERROR_CANT_PLAY)
                    case '2':
                        startTime = time.time_ns()
                        self.markSolutionPath(True)
                        self.markDurTime = time.time_ns() - startTime
                        print(" The solution-path is {} cells long:".format(self.solutionSize))
                        self.printMaze(True)
                        self.printSolutionDurationStats()
                        self.markSolutionPath(False)
                    case '3':
                        print(" Each Node represented by 1 column spanning over 2 rows (vertically). Each Node stores "
                              "just 2 walls - the horizontal north-top wall and the vertical west-left-wall:")
                        self.printMaze(False)
                    case '4':
                        self.setPlayerStart()
                        self.printMazeSetPathfinder()
                    case '5':
                        self.setPlayerTarget()
                        self.printMazeSetPathfinder()
                    case '6':
                        self.setPlayer()
                        self.printMazeSetPathfinder()
                    case '7':
                        print(INFO)
                    case '9' | 'q':
                        isRunning = False
                        print(" Exiting Maze-Game")
                    case _:
                        print(" Error: Wrong input!")

            except Exception as error:
                print(f" Error: {error}")

    def getMazeSize(self, x, y):
        while x < 10 or y < 10:
            try:
                x = int(input("X-axis cell count: "))
                y = int(input("Y-axis cell count: "))
                if x < 10 or y < 10:
                    print(ERROR_MAZE_SIZE)
            except ValueError:
                print("Invalid input!")
        return x, y

    def generateAndPrintMaze(self, x, y):
        self.setMaze(x, y)
        if self.player is not None:
            self.player = None
        self.setPlayer()
        self.printMazeSetPathfinder()
        self.printMazeDurationStats()

    def getMaze(self):
        return self.maze

    def setMaze(self, x, y):
        startTime = time.time_ns()
        self.maze = Maze(x, y)
        self.generator = Generator(self.maze)
        self.mazeDurTime = time.time_ns() - startTime

        self.mazeSpanningTree = self.generator.getSpanning3()

        startTime = time.time_ns()
        self.maze.setCells()                 # generates the maze-output for the console, which is stored in a 2D-array
        self.buildMazeCellsDurTime = time.time_ns() - startTime

    def getPlayer(self):
        return self.player

    def setPlayer(self):
        if self.player is not None:
            self.maze.setMarker(self.player.getPosX(), self.player.getPosY(), "   ")
            self.maze.setMarker(self.player.getTargetX(), self.player.getTargetY(), "   ")
            self.player.setPosTarget(self.maze.sizeX-1, self.maze.sizeY-1)
        else:
            self.player = Player(self.maze.sizeX-1, self.maze.sizeY-1)

        self.maze.setMarker(self.player.getPosX(), self.player.getPosY(), "PLY")
        self.maze.setMarker(self.player.getTargetX(), self.player.getTargetY(), "END")

    def setPlayerStart(self):
        self.maze.setMarker(self.player.getPosX(), self.player.getPosY(), "   ")
        self.player.setPos()
        self.maze.setMarker(self.player.getPosX(), self.player.getPosY(), "PLY")

    def setPlayerTarget(self):
        self.maze.setMarker(self.player.getTargetX(), self.player.getTargetY(), "   ")
        self.player.setTarget()
        self.maze.setMarker(self.player.getTargetX(), self.player.getTargetY(), "END")

    def getPathfinder(self):
        return self.pathfinder

    def setPathfinder(self):
        startTime = time.time_ns()
        self.pathfinder = Pathfinder(self.generator.getSpanning3(),
                                     self.maze.getNode(self.player.getPosX(), self.player.getPosY()),
                                     self.maze.getNode(self.player.getTargetX(), self.player.getTargetY()))
        self.solutionDurTime = time.time_ns() - startTime

    def markSolutionPath(self, isMarked):
        marker = " ■ " if isMarked else "   "
        for node in self.pathfinder.getSolutionPath():
            self.maze.setMarker(node.getX(), node.getY(), marker)

    def printMaze(self, isPrintMaze):
        startTime = time.time_ns()
        print(self.maze if isPrintMaze else self.maze.printOutAsArray())
        self.printDurTime = time.time_ns() - startTime

    def printMazeSetPathfinder(self):
        print("\nPlayer start-coordinate at x={},y={} and end-coordinate at x={},y={}:"
              .format(self.player.getPosX()+1, self.player.getPosY()+1, self.player.getTargetX()+1,
                      self.player.getTargetY()+1))
        self.printMaze(True)
        self.setPathfinder()
        # solutionSize as comparison for player's game performance, canPlay: player allowed to play the maze-game
        self.solutionSize, self.canPlay = len(self.pathfinder.getSolutionPath()) + 1, True
        
    def printMazeDurationStats(self):
        print(" It took {} to generate this maze,\n\t\t{} to build the Maze-Output-Array\n\t and {} to print it out.\n"
              .format(getDurTimeUnit(self.mazeDurTime), getDurTimeUnit(self.buildMazeCellsDurTime),
                      getDurTimeUnit(self.printDurTime)))

    def printSolutionDurationStats(self):
        print(" It took {} to find the only Path connecting PLY-Cell at x={}, y={} to END-Cell at x={}, y={} \n" \
              "     and {} to mark the Solution-Path in the maze to see it in the maze's printout\n" \
              "   after {}.\n".format(getDurTimeUnit(self.solutionDurTime), self.player.getPosX() + 1,
                                      self.player.getPosY() + 1, self.player.getTargetX() + 1,
                                      self.player.getTargetY()+1, getDurTimeUnit(self.markDurTime),
                                      getDurTimeUnit(self.printDurTime)))

    def play(self):
        isPlaying, isShowSolution, plyCounter, direction, marker, msg = True, False, 0, 0, "", ""
        columnModifier =  (0, 0, -1, 0, 1)
        rowModifier    =  (0, -1, 0, 1, 0)
        currentCell = self.maze.getNode(self.player.getPosX(), self.player.getPosY())
        while isPlaying:
            match(input(GAME_INPUT_MSG)):
                case '8' | 'w':
                    direction = 1
                    marker = " ↑ "
                case '4' | 'a':
                    direction = 2
                    marker = " ← "
                case '5' | 's':
                    direction = 3
                    marker = " ↓ "
                case '6' | 'd':
                    direction = 4
                    marker = " → "
                case '2':
                    isShowSolution = True
                    direction = 0
                case '9':
                    isPlaying = False
                case _:
                    direction = 0
            if isPlaying:
                if not isShowSolution:
                    plyCounter += 1
                destinationColumn = self.player.getPosX() + columnModifier[direction] # x
                destinationRow    = self.player.getPosY() + rowModifier[direction]    # y
                if self.player.isPositionWithinMazeBoundary(destinationColumn, destinationRow):
                    destinationCell = self.maze.getNode(destinationColumn, destinationRow)
                    # ↓ checks if the list-value of currentCell-key in the dictionary mazeSpanningTree contains the
                    # ↓ destinationCell, meaning if there is path which connects currentCell to destinationCell. There's
                    # ↓ no need to check if there is a wall inbetween as the mazeSpanningTree stores only valid paths.
                    if destinationCell in self.mazeSpanningTree[currentCell] and not isShowSolution:
                        self.player.setPos(destinationColumn, destinationRow)
                        self.maze.setMarker(currentCell.getX(), currentCell.getY(), marker)
                        self.maze.setMarker(destinationColumn, destinationRow, "PLY")
                        currentCell = destinationCell
                        msg = ""
                        if self.player.isPosTargetEqual():
                            self.canPlay, isPlaying, difference = False, False, plyCounter - self.solutionSize
                            msg = CONGRATS_MSG.format(plyCounter, ("longer than" if difference >= 1
                                                                    else "the same amount as"),
                                                      (f"of {self.solutionSize} cells!" if difference >= 1  else ""))
                    elif isShowSolution:
                        self.setPathfinder()         # recalculates the solution path from player's current position.
                        self.markSolutionPath(True)  # might overwrite player's arrow-direction-markers.
                    elif currentCell == destinationCell:
                        msg = "\n\tError: Invalid key pressed!\n"
                    else:
                        msg = "\n\tError: Invalid direction → wall\n"
                else:
                    msg = "\n\tError: Invalid direction → out of maze boundary\n"

                self.printMaze(True)
                print(msg)

                if isShowSolution:
                    self.markSolutionPath(False) # solution-pathway-marker erased
                    isShowSolution = False
            else:
                print("\nPlayer ended game!\nTo continue the previous game, choose option [1] below.\n")


AXIS_HELP_MSG = "Separate the cell-count-values for x- and y-axis by 1 space.\nI.e.: mazegamy.py 10 10"
PARAM_MSG = "\nGenerating a maze of {} cells, with {} cells for the x-axis and {} cells for the y-axis.\n"
ERROR_OVER_2_PARAM = "\nError: Too many arguments!\nExactly 2 integer arguments are allowed.\n"
ERROR_ONLY_1_PARAM = ERROR_OVER_2_PARAM.replace("many","few")
ERROR_MAZE_SIZE = "Error: The values for x and y must be greater than 9!\n"
ERROR_CANT_PLAY = "Error: Please generate either a new maze with option [0]\n\t\t" \
                "or generate a new end position with option [5] or [6].\n"
MENU = """  [0] Generate a random 'perfect' maze.
  [1] Play the Maze-Game (in console).
  [2] Print solution.
  [3] Print the maze as a 2D-Array
  [4] New random Player start position
  [5] New random Player end position
  [6] New random Player start and end position.
  
  [7] About Maze-Game 
  [9] Exit program 
"""
INFO = "\n{0:>39}\n{1:>29}\n{2:>36}\n{3:>58}\n\n{4}\n{5:>93}\n"\
     .format("Author: Mandeep Singh", "Version: 2.0", "Date: 28.07.2023", "GitHub: https://github.com/M4nd33pSingh/Maze_Game",
             "Ported from java version: https://github.com/M4nd33pSingh/Mazegame",
             "Maze-Game version 1: https://github.com/Malkogiannidou/MazeGame_MazeSolver_MazeGenerator")
GAME_INPUT_MSG = "Press one key for intended direction and then enter- or return-key: \n" \
                 "up ↑: w / 8 ┃ down ↓: s / 5 ┃ left ←: a / 4 ┃ right →: d / 6  ┃┃ show solution: 2 ┃ end game: 9 ┃┣ "
CONGRATS_MSG = "\tCongratulations! You reached the target-cell after {} steps, which is {} the solution-path-length{}."

def getDurTimeUnit(duration):
    return "{:6.2f} microseconds".format(duration / 1000) if duration/1000 < 1000 \
        else "{:6.2f} milliseconds".format(duration / 1000000) if duration/1000000 < 1000 \
        else "{:6.2f} seconds".format(duration / 1000000000)

def _get_args() -> argparse.Namespace:
    """ Converts argument strings to objects and assign them as attributes of the namespace.

    Source-Code_ Argparse-doc_

    .. _Argparse-doc: https://docs.python.org/3.11/library/argparse.html#argparse.ArgumentParser.parse_args \n
    .. _Source-Code: https://github.com/Malkogiannidou/MazeGame_MazeSolver_MazeGenerator/blob/6ac76bcbf01b19ef6d55b28d8c8612d64b064227/mazespiel.py#L584

    :return: the populated namespace to access the attributes which store the assigned argument as an object.
    """
    parser = argparse.ArgumentParser( description = '\tParameterized maze-game start',
                                      formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(   'axisValues', nargs = '*', type = int, help = AXIS_HELP_MSG)
    parser.add_argument('-x', '--xaxis', nargs = 1,   type = int, help = "cell count value for x-axis")
    parser.add_argument('-y', '--yaxis', nargs = 1,   type = int, help = "cell count value for y-axis")
    return parser.parse_args()

if __name__ == '__main__':
    args = _get_args()                                          # argument parser
    if args.xaxis and args.yaxis:                               # program start: mazegame.py -x 10 -y 11
        MazeGame().run(args.xaxis[0], args.yaxis[0], PARAM_MSG.format(args.xaxis[0] * args.yaxis[0], args.xaxis[0], args.yaxis[0]))
    elif (args.xaxis and not args.yaxis) or (not args.xaxis and args.yaxis):
        print(ERROR_ONLY_1_PARAM)                               # program start: mazegame.py -x 10 OR mazegame.py -y 11
        MazeGame().run()
    elif len(args.axisValues) == 2:                             # program start: mazegame.py 10 11
        MazeGame().run(args.axisValues[0], args.axisValues[1], PARAM_MSG.format(args.axisValues[0] * args.axisValues[1], args.axisValues[0], args.axisValues[1]))
    elif len(args.axisValues) > 2:                              # program start: mazegame.py 10 11 12
        print(ERROR_OVER_2_PARAM)
        MazeGame().run()
    elif len(args.axisValues) == 1:                             # program start: mazegame.py 10
        print(ERROR_ONLY_1_PARAM)
        MazeGame().run()
