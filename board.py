import checker
import config
import point
import math
import sys

class Board(object):
    def __init__(self):        
        self.board = [[None for x in range(8)] for x in range(8)]
        self.checkers = {config.WHITE: [], config.BLACK: []}
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

    def ClearBoard(self):
        for x in range(config.BOARD_HEIGHT):
            for y in range(config.BOARD_WIDTH):
                piece = self.board[x][y]
                if(piece != None):
                    self.checkers[piece.Color].remove(piece)
                    self.board[x][y] = None

    def UndoMove(self, source, dest, bEat=False):
        # Sanity checks
        if (not self.IsLegalMove(source, dest, bEat)):
            return False

        if (self[source.x][source.y] != None):
            print("UndoMove, Illegal move, UndoMove self[source.x][source.y] != None")
            return False

        piece = self[dest.x][dest.y]
        if (piece == None):
            print("UndoMove, piece missing, UndoMove")
            return False

        XDistance = abs(source.x - dest.x)
        YDistance = abs(source.y - dest.y)

        XDirection = (dest.x - source.x)  / XDistance
        YDirection = (dest.y - source.y)  / YDistance

        # check if we're undoing a queen's move or a simple checker's move.
        if(piece.__class__.__name__ == "Checker"):
            # distance should be either 1 or 2
            if (XDistance > 2 or YDistance > 2):
                print("UndoMove, Impossible move.")
                return False

            # Make sure move direction is correct for selected piece.
            if (not bEat and piece.AdvanceDirection != XDirection):
                print "UndoMove, Your going in the wrong direction"
                return False

            if(bEat and XDistance != 2):
                print "UndoMove, checker eat move should be exactly two steps"
                return False

        if(bEat):

            deadXPos = dest.x - XDirection
            deadYPos = dest.y - YDirection
            dead = self[deadXPos][deadYPos]

            if (dead != None):
                print("UndoMove, Expecting empty spot.")
                return

            color = config.WHITE if (piece.Color == config.BLACK) else config.BLACK

            dead = checker.Checker(color, point.Point(deadXPos, deadYPos), self)

            self.board[deadXPos][deadYPos] = dead
            self.checkers[dead.Color].append(dead)

        piece.Move(source)
        self.board[source.x][source.y] = piece
        self.board[dest.x][dest.y] = None

    def MultipleMove(self, move_list):
        moveCounter = 0
        for move in move_list:
            bCheckDirection = False if (moveCounter > 0 and move['eat']) else True
            if(not self.Move(move['from'], move['to'], bCheckDirection)):
                # TODO revert performed moves.
                return False
            moveCounter += 1

        return True

    def MultipleUndoMove(self, move_list):
        for move in reversed(move_list):
            self.UndoMove(move['from'], move['to'], move['eat'])

    def IsLegalMove(self, source, dest, bEat):
        if (not self.WithinBounds(source.x, source.y)):
            print("Illegal move, WithinBounds")
            return False

        if (not self.WithinBounds(dest.x, dest.y)):
            print("Illegal move, WithinBounds")
            return False

        if ((source.x == dest.x) or (source.y == dest.y)):
            print("Illegal move, you must move in both directions")
            return False

        XDistance = abs(source.x - dest.x)
        YDistance = abs(source.y - dest.y)

        if(XDistance != YDistance):
            print("Illegal move, you must move an equal distance in both directions")
            return False

        if(bEat == True and (XDistance < 2 or YDistance < 2)):
            print("Illegal move, when eating piece must travel at least two steps")
            return False

        return True

    def Move(self, source, dest, bCheckDirection = True, bEat = False):

        # Sanity checks.
        if(not self.IsLegalMove(source, dest, bEat)):
            return False

        if (self[source.x][source.y] == None):
            print("Move, piece missing")
            return False

        if (self[dest.x][dest.y] != None):
            print("Move, Illegal move from %d,%d to %d,%d" % (source.x, source.y, dest.x, dest.y))
            return False

        piece = self[source.x][source.y]
        # Find out move direction: up left, down left, etc.
        # Division is necessary to keep Distance equal to 1 / -1, (think vector normal).
        XDirection = (dest.x - source.x) / (abs(source.x - dest.x))
        YDirection = (dest.y - source.y) / (abs(source.x - dest.x))

        if (piece.__class__.__name__ == "Checker"):
            # Check move direction.
            if(bCheckDirection and piece.AdvanceDirection != XDirection):
                print "Move, Your going in the wrong direction"
                return False

            # Checker can't move more than two steps in a single move
            if ((abs(source.x - dest.x) > 2 or abs(source.y - dest.y) > 2)):
                print "Move, Checker can't move more than two steps in a single move."
                return False

        # Is it an eat move?
        if (abs(source.x - dest.x) > 1):
            eatXPos = dest.x - XDirection
            eatYPos = dest.y - YDirection
            dead = self[eatXPos][eatYPos]

            # Make sure there's a piece at 'skipped' position.
            if (dead != None):
                if (dead.Color == piece.Color):
                    print("Move, Can't eat your own kind.")
                    return False
                # Eat!
                self.RemovePiece(dead.Position)

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