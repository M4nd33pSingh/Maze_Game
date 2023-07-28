class Node:
    def __init__(self, x, y, maxX, maxY):
        self.x, self.y = x, y
        self.north, self.west, self.visited = True, True, False
        self.neighbors = []
        self._setNeighbors(maxX - 1, maxY - 1)

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def hasNorth(self):
        return self.north

    def hasWest(self):
        return self.west

    def setNorth(self, state):
        self.north = state

    def setWest(self, state):
        self.west = state

    def isVisited(self):
        return self.visited

    def setVisited(self, state):
        self.visited = state

    def hasNeighbors(self):
        return len(self.neighbors) > 0

    def getNeighbors(self):
        return self.neighbors

    def _setNeighbors(self, sizeX, sizeY):
        modX = (1,0,-1,0)
        modY = (0,1,0,-1)
        for directionIndex in range(4):
            x = self.x + modX[directionIndex]
            y = self.y + modY[directionIndex]
            if 0 <= x < sizeX and 0 <= y < sizeY:
                self.neighbors.append((x, y, directionIndex))

    def __repr__(self):
        return "|x={}, y={}| ".format(self.x, self.y)


class Maze: # Todo: Why +1, if the extra is subtracted anyway?
    def __init__(self, sizeX, sizeY):
        self.sizeX, self.sizeY = sizeX+1, sizeY+1
        self.nodes = [[Node(x, y, sizeX+1, sizeY+1) for x in range(sizeX+1)] for y in range(sizeY+1)]
        self.cells = [["" for x in range(sizeX+1)] for y in range(2 * (sizeY+1))]
        self.wallConnection = (" ", "╹", "╸", "┛", "╻", "┃", "┓", "┫", "╺", "┗", "━", "┻", "┏", "┣", "┳", "╋")
        self._set_South_East_MazeBoundaries()

    def _set_South_East_MazeBoundaries(self):
        # sets south (bottom) maze boundary by deleting every vertical west-wall (left cell-wall) of the last row
        for x in range(self.sizeX):
            self.nodes[self.sizeY-1][x].setWest(False)
            self.nodes[self.sizeY-1][x].setVisited(True)

        # sets east (right) maze boundary by deleting every horizontal north-wall (top cell-wall) of the last column
        for y in range(self.sizeY):
            self.nodes[y][self.sizeX-1].setNorth(False)
            self.nodes[y][self.sizeX-1].setVisited(True)

    def getNodes(self):
        return self.nodes

    def getNode(self, x, y):
        return self.nodes[y][x]

    def _getIndex(self, x, y):
        binaryCode = "{}{}{}{}".format(
            1 if self.nodes[y][x].hasNorth() else 0,
            1 if self.nodes[y][x].hasWest() else 0,
            1 if x-1 >= 0 and self.nodes[y][x-1].hasNorth() else 0,
            1 if y-1 >= 0 and self.nodes[y-1][x].hasWest() else 0
        )
        return int(binaryCode, 2)

    def setCells(self):
        for y in range(self.sizeY):
            for x in range(self.sizeX):
                self.cells[2 * y][x] = "{}{}".format(self.wallConnection[self._getIndex(x, y)],
                                                     "━━━" if self.nodes[y][x].hasNorth() else "   ")
                self.cells[2 * y + 1][x] = "{}   ".format("┃" if self.nodes[y][x].hasWest() else " ")

    def setMarker(self, x, y, marker):
        self.cells[2 * y + 1][x] = self.cells[2 * y + 1][x][:1] + marker

    def __repr__(self):
        mazeOutputString = ""
        for y in range( len(self.cells) ):
            for x in range( len(self.cells[0]) ):
                mazeOutputString += self.cells[y][x]
            mazeOutputString += "\n"
        return mazeOutputString[:-4 * len(self.cells[0]) - 2]

    def printOutAsArray(self):
        arrayString = ""
        for index, row in enumerate(self.cells):
            arrayString += str(row) + (",\n\n" if index % 2 != 0 else ",\n")
        return arrayString


import random

class Player:
    def __init__(self, sizeX, sizeY):
        self.pos, self.target = [0,0], [0,0]
        self.sizeX, self.sizeY = sizeX-1, sizeY-1
        self.setPosTarget()

    def getPos(self):
        return self.pos

    def getPosX(self):
        return self.pos[0]

    def getPosY(self):
        return self.pos[1]

    def setPos(self, x=-1, y=-1):
        if x == -1 or y == -1:
            self.pos = [random.randint(0, self.sizeX), random.randint(0, self.sizeY)]
            if self.isPosTargetEqual() or not self.isPositionWithinMazeBoundary(self.getPosX(), self.getPosY()):
                self.setPos()
        else:
            self.pos = [x,y]

    def getTarget(self):
        return self.target

    def getTargetX(self):
        return self.target[0]

    def getTargetY(self):
        return self.target[1]

    def setTarget(self):
        self.target = [random.randint(0, self.sizeX), random.randint(0, self.sizeY)]
        if self.isPosTargetEqual() or not self.isPositionWithinMazeBoundary(self.getTargetX(), self.getTargetY()):
            self.setTarget()

    def setPosTarget(self, sizeX=-1, sizeY=-1):
        if sizeX > -1 or sizeY > -1:
            self.sizeX, self.sizeY = sizeX, sizeY
        self.pos = [random.randint(0, self.sizeX), random.randint(0, self.sizeY)]
        self.target = [random.randint(0, self.sizeX), random.randint(0, self.sizeY)]
        if self.isPosTargetEqual() \
                or not self.isPositionWithinMazeBoundary(self.getPosX(), self.getPosY()) \
                or not self.isPositionWithinMazeBoundary(self.getTargetX(), self.getTargetY()):
            self.setPosTarget()

    def isPositionWithinMazeBoundary(self, x, y):
        return 0 <= x <= self.sizeX and 0 <= y <= self.sizeY

    def isPosTargetEqual(self):
        return self.pos == self.target


class Stack:
    def __init__(self):
        self.items = []

    def getItems(self):
        return self.items

    def push(self, item):
        self.items.append(item)

    def pop(self, index = -1):
        return self.items.pop(index)

    @property
    def size(self):
        return len(self.items)

    def isNotEmpty(self):
        return self.size != 0

    def __repr__(self):
        return str(self.items)