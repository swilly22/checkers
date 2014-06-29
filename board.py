import checker
import config
import point
import math
import sys

class Board(object):
    def __init__(self):
        self.blank_board = [[0 for x in range(8)] for x in range(8)]
        self.board = [[None for x in range(8)] for x in range(8)]
        self.checkers = {config.WHITE: [], config.BLACK: []}

        for x in range(config.BOARD_WIDTH):
            for y in range(config.BOARD_HEIGHT):
                if ((x + y) % 2 == 0):
                    self.blank_board[x][y] = 'B'
                else:
                    self.blank_board[x][y] = 'W'

        self.SetNormalBoard()

    @staticmethod
    def WithinBounds(x, y):
        return True if (x >= 0 and x < config.BOARD_WIDTH and y >= 0 and y < config.BOARD_HEIGHT) else False

    def SetNormalBoard(self):
        # Place blacks.
        for x in range(3):
            for y in range(config.BOARD_WIDTH):
                if ((x + y) % 2 == 0):
                    location = point.Point(x, y)
                    piece = checker.Checker(config.WHITE, location, self)
                    self.AddPiece(piece, location)

        # Place whites.
        for x in range(5, 8):
            for y in range(config.BOARD_HEIGHT):
                if ((x + y) % 2 == 0):
                    location = point.Point(x, y)
                    piece = checker.Checker(config.BLACK, location, self)
                    self.AddPiece(piece, location)
                    #self.checkers[config.BLACK].append(piece)
                    #self.board[x][y] = piece

    def UndoMove(self, source, dest, eat=False):
        if ((source.x == dest.x) or (source.y == dest.y)):
            print("UndoMove, Illegal move, you're not going anywhere!")
            return

        if (not self.WithinBounds(source.x, source.y)):
            print("UndoMove, Illegal move, UndoMove WithinBounds")
            return

        if (not self.WithinBounds(dest.x, dest.y)):
            print("UndoMove, Illegal move, UndoMove WithinBounds")
            return

        if (self[dest.x][dest.y] == None):
            print("UndoMove, piece missing, UndoMove")
            return

        if (self[source.x][source.y] != None):
            print("UndoMove, Illegal move, UndoMove self[source.x][source.y] != None")
            return

        if (source.x == dest.x) or (source.y == dest.y):
            print("UndoMove, Illegal move, UndoMove source.x == dest.x) or (source.y == dest.y")
            return

        piece = self[dest.x][dest.y]

        # check if we're undoing a queen's move or a simple checker's move.
        if(piece.__class__.__name__ == "Checker"):
            # distance should be either 1 or 2
            if (abs(source.x - dest.x) > 2) or (abs(source.y - dest.y) > 2):
                print("UndoMove, Impossible move at the moment.")
                return

            # Is it a double step?
            if (abs(source.x - dest.x) == 2):
                # Make sure move is legal.
                midX = int(math.ceil((source.x + dest.x) / 2))
                midY = int(math.ceil((source.y + dest.y) / 2))
                dead = self[midX][midY]

                if (dead != None):
                    print("UndoMove, Expecting empty spot.")
                    return

                if (piece.Color == config.WHITE):
                    dead = checker.Checker(config.BLACK, point.Point(midX, midY), self)
                else:
                    dead = checker.Checker(config.WHITE, point.Point(midX, midY), self)

                # NOTE there's no check for move direction here!, check is made in the checker class.
                self.board[midX][midY] = dead
                self.checkers[dead.Color].append(dead)

            else:  # This is a single step make sure move direction is correct for selected piece.
                if piece.AdvanceDirection != (dest.x - source.x):
                    print "UndoMove, Your going in the wrong direction"
                    return
        # Queen.
        else:
            if(eat):
                #Determine move direction.
                YDirection = 0
                XDirection = 0
                if(source.y > dest.y):
                    YDirection = +1
                else:
                    YDirection = 1

                if source.x > dest.x:
                    XDirection = +1
                else:
                    XDirection = 1

                deadXPos = dest.x + XDirection
                deadYPos = dest.y + YDirection
                dead = self[deadXPos][deadYPos]

                if (dead != None):
                    print("UndoMove, Expecting empty spot.")
                    return

                color = config.WHITE
                if (piece.Color == config.WHITE):
                    color = config.BLACK

                dead = checker.Checker(color, point.Point(deadXPos, deadYPos), self)

                # NOTE there's no check for move direction here!, check is made in the checker class.
                self.board[deadXPos][deadYPos] = dead
                self.checkers[dead.Color].append(dead)

        piece.Move(source)
        self.board[source.x][source.y] = piece
        self.board[dest.x][dest.y] = None

    def MultipleMove(self, move_list):
        moveCounter = 0
        for move in move_list:
            bCheckDirection = False if (moveCounter > 0 and move['eat']) else True
            self.Move(move['from'], move['to'], bCheckDirection)
            moveCounter += 1

    def MultipleUndoMove(self, move_list):
        for move in reversed(move_list):
            self.UndoMove(move['from'], move['to'])

    def Move(self, source, dest, bCheckDirection = True):
        if (not self.WithinBounds(source.x, source.y)):
            print("Move, WithinBounds - Illegal move")
            return False

        if (not self.WithinBounds(dest.x, dest.y)):
            print("Move, WithinBounds - Illegal move")
            return False

        if (self[source.x][source.y] == None):
            print("Move, piece missing")
            return False

        if (self[dest.x][dest.y] != None):
            print("Move, Illegal move from %d,%d to %d,%d" % (source.x, source.y, dest.x, dest.y))
            return False

        if (source.x == dest.x) or (source.y == dest.y):
            print("Move, Illegal move")
            return False

        piece = self[source.x][source.y]

        # Checker can't move more than two steps in a single move
        if (piece.__class__.__name__ == "Checker" and (abs(source.x - dest.x) > 2 or abs(source.y - dest.y) > 2)):
            print "Move, Checker can't move more than two steps in a single move."
            return False

        if (piece.__class__.__name__ == "Checker"):
            # Is it an eat move?
            if (abs(source.x - dest.x) > 1):
                # Find out move direction: up left, down left, etc.
                # Division is necessary to keep Distance equal to 1 / -1, (think vector normal).
                XDirection = (dest.x - source.x) / (abs(source.x - dest.x))
                YDirection = (dest.y - source.y) / (abs(source.x - dest.x))
                eatXPos = dest.x - XDirection
                eatYPos = dest.y - YDirection
                dead = self[eatXPos][eatYPos]

                # Make sure move is legal.
                if (dead == None):
                    print("Move, Illegal move, dead == None")
                    return False

                if (dead.Color == piece.Color):
                    print("Move, Can't eat your own kind.")
                    return False
                # Eat!
                self.RemovePiece(dead.Position)
        # Queen.
        else:
            # Is it a potential eat move?
            if (abs(source.x - dest.x) > 1):
                # Find out move direction: up left, down left, etc.
                # Division is necessary to keep Distance equal to 1 / -1, (think vector normal).
                XDirection = (dest.x - source.x) / (abs(source.x - dest.x))
                YDirection = (dest.y - source.y) / (abs(source.x - dest.x))
                eatXPos = dest.x - XDirection
                eatYPos = dest.y - YDirection
                dead = self[eatXPos][eatYPos]

                # Make sure move is legal.
                if (dead != None):
                    if (dead.Color == piece.Color):
                        print("Move, Can't eat your own kind.")
                        return False
                    # Eat!
                    self.RemovePiece(dead.Position)

        # Make sure move move direction is correct
        if piece.__class__.__name__ == "Checker" and \
                        bCheckDirection and \
                        piece.AdvanceDirection != (dest.x - source.x) / abs((dest.x - source.x)):
            print "Move, Your going in the wrong direction"
            return False

        # Legal move.
        piece.Move(dest)
        self.board[dest.x][dest.y] = piece
        self.board[source.x][source.y] = None
        return True

    def RemovePiece(self, location):
        # Sanity checks.
        if (not self.WithinBounds(location.x, location.y)):
            print("Illegal location, RemovePiece")
            return

        piece = self.board[location.x][location.y]
        if (piece == None):
            print("No piece in given location.")
            return

        self.checkers[piece.Color].remove(piece)

        # Remove checker from board.
        self.board[location.x][location.y] = None

    def AddPiece(self, piece, location):
        # Sanity checks.
        if(piece == None or location == None):
            print("Null argument")
            return False

        if(piece.Position.x != location.x or piece.Position.y != location.y):
            print("Inconsistency, piece isn't at decleared position.")
            return False

        if(not self.WithinBounds(location.x, location.y)):
            print("Can't place piece at given location")
            return False

        temp = self.board[location.x][location.y]
        if (temp != None):
            print("there's already a piece at given location.")
            return False

        self.checkers[piece.Color].append(piece)
        self.board[location.x][location.y] = piece
        return True

    def __getitem__(self, index):
        return self.board[index]

    def CopyBlankBoard(self):
        return list(self.blank_board)

    def Print(self):
        board = self.CopyBlankBoard()

        for white in self.checkers[config.WHITE]:
            board[white.Position.x][white.Position.y] = white.Color

        for black in self.checkers[config.BLACK]:
            board[black.Position.x][black.Position.y] = black.Color

        for x in reversed(range(config.BOARD_HEIGHT)):
            for y in range(config.BOARD_WIDTH):
                sys.stdout.write(str(board[x][y]) + " ")
            print("")