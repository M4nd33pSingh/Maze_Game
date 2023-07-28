import random
import copy
from model import Maze, Node, Stack

class Generator:
    def __init__(self, maze:Maze):
        self.maze = maze
        self.startX, self.startY = random.randint(0,self.maze.sizeX), random.randint(0,self.maze.sizeY)
        self._spanning3:dict = {}
        self._generateMaze()

    def getSpanning3(self) -> dict:
        """ Returns a newly created copy of the spanning3 and not just a reference (shallow/deep copy) to the _spanning3.

        Creates a new dictionary-object copyOfSpanning3 and copies every object in the spanning3, which allocates more
        memory. Does not reference to the original spanning3, no shallow or deep copy (deep didn't work as intented).

        :return: A newly created copy of the spanning3 as a new dictionary-object, which does not reference to the
         original spanning-tree.
        """
        copyOfSpanning3 = {}
        for key in self._spanning3.keys():
            copyOfSpanning3[key] = []
            for item in self._spanning3[key]:
                copyOfSpanning3[key].append(item)
        return copyOfSpanning3
        # return copy.deepcopy(self._spanning3)  # ← ← ← deepcopy didn't work!

    def _generateMaze(self):
        """ Generates maze with the iterative algorithm of randomized depth-first search with backtracking (uses stack).

        While generating the maze the spanning-tree (_spanning3) of the maze is also built. The _spanning3 is a
        dictionary, which stores a node as the key and a list as the value of the key in which only valid path-Nodes are
        stored.
                                                                         \n
        The _spanning3 is needed for finding the solution-path of the maze and for the maze-game, where it's used to
        validate the intended player movement direction by checking, if destination-node exists in the key-node
        value-list.
                                                                    \n
                                                                                        \n
        1  Choose the initial cell*, mark it as visited and push it to the stack        \n
        2  While the stack is not empty										            \n
        2.1  Pop a cell from the stack and make it a current cell*			            \n
        2.2  If the current cell* has any neighbors which have not been visited         \n
        2.2.1  Push the current cell* to the stack 			  			                \n
        2.2.2  Choose one of the unvisited neighbors			  			            \n
        2.2.3  Remove the wall between the current cell* and the chosen cell**          \n
        2.2.4  Mark the chosen cell** as visited and push it to the stack          	    \n
        (* currentNode, ** nextNode)                                                    \n

        Iterative-implementation-pseudo-code-source_                                                             \n
        .. _Iterative-implementation-pseudo-code-source: https://en.wikipedia.org/wiki/Maze_generation_algorithm#:~:text=in%20the%20area.-,Iterative%20implementation,-%5Bedit%5D
        """
        stack = Stack()
        currentNode: Node = self.maze.getNode(self.startX, self.startY)     # 1
        currentNode.setVisited(True)                         # 1
        stack.push(currentNode)                              # 1
        self._spanning3[currentNode]:list[Node] = []

        while stack.isNotEmpty():                            # 2
            currentNode = stack.pop()                        # 2.1
            if currentNode.hasNeighbors():                   # 2.2
                stack.push(currentNode)                      # 2.2.1

                x, y, direction = random.choice(currentNode.getNeighbors()) # 2.2.2
                currentNode.getNeighbors().remove((x, y, direction))        # 2.2.2
                nextNode: Node = self.maze.getNode(x, y)                    # 2.2.2

                if not nextNode.isVisited():                 # 2.2
                    match direction:                         # 2.2.3
                        case 0: # right
                            nextNode.setWest(False)
                        case 1: # down
                            nextNode.setNorth(False)
                        case 2: # left
                            currentNode.setWest(False)
                        case 3: # up
                            currentNode.setNorth(False)

                    self._spanning3[currentNode].append(nextNode)
                    if nextNode in self._spanning3:
                        self._spanning3[nextNode].append(currentNode)
                    else:
                        self._spanning3[nextNode] = [currentNode]

                    nextNode.setVisited(True)                # 2.2.4
                    stack.push(nextNode)                     # 2.2.4


class Pathfinder:
    def __init__(self, spanning3:dict, start:Node, target:Node):
        """ Finds the solution-path of the maze.

        :param spanning3: the spanning-tree of the maze to find a solution path from start-node to target-node as a dictionary
        :param start: the current Node position in the maze of the player
        :param target: the target Node in the maze
        """
        self.solutionPathStack = Stack()
        self._setSolutionPath(spanning3, start, target)

    def getSolutionPath(self):
        return self.solutionPathStack.getItems()

    def _setSolutionPath(self, spanning3:dict, startNode:Node, targetNode:Node):
        """ Finds the Solution-Path from Players current position (currentNode) to the target position (targetNode) by using only the spanning-tree (spanning3) of the maze.

     |  The spanning3-dictionary stores a node as the key and a list as the value of the key-node in which only valid
     |  path-Nodes are stored. While searching for the solution, this copy of the spanning3 gets destroyed.
     |
     |  A stack is used to store the Nodes of the solution-path.
     |
     |  1  PUSH the currentNode to the solutionPath (stack)
     |  2  WHILE the nextNode is not equal to the targetNode
     |  2.1  POP a Node from the stack and make it a current Node
     |  2.2  IF the current Node has any connection to other Nodes
     |  2.2.1  PUSH the currentNode to the stack
     |  2.2.2  CHOOSE a random path from currentNode as nextNode
     |  2.2.3  PUSH the nextNode to the stack
     |  2.2.4  REMOVE the path from currentNode to nextNode
     |  2.2.5  REMOVE the path from nextNode to currentNode
     |  3  REMOVE the first Node from the stack
     |  4  REMOVE the last Node from the stack

        :param spanning3: the spanning-tree of the maze to find a solution path from currentNode to targetNode as a dictionary
        :param startNode: the current Node position in the maze of the player
        :param targetNode: the target Node in the maze
        """
        nextNode:Node = startNode
        self.solutionPathStack.push(startNode)             # 1

        while nextNode != targetNode:                      # 2
            currentNode = self.solutionPathStack.pop()       # 2.1

            if len(spanning3[currentNode]) != 0:             # 2.2
                self.solutionPathStack.push(currentNode)         # 2.2.1
                nextNode = random.choice(spanning3[currentNode]) # 2.2.2
                self.solutionPathStack.push(nextNode)            # 2.2.3

                spanning3[currentNode].remove(nextNode)          # 2.2.4
                spanning3[nextNode].remove(currentNode)          # 2.2.5

        self.solutionPathStack.pop(0)                      # 3 ~ is where PLY is marked in the maze
        self.solutionPathStack.pop()                       # 4 ~ is where END is marked in the maze