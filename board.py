import checker
import config
import point
import math
import sys

class Board(object):
    def __init__(self):
        self.blank_board = [[0 for x in range(10)] for x in range(10)]
        self.board = [[None for x in range(10)] for x in range(10)]
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
                    piece = checker.Checker(config.WHITE, point.Point(x, y), self)

                    self.checkers[config.WHITE].append(piece)
                    self.board[x][y] = piece

        # Place whites.
        for x in range(5, 8):
            for y in range(config.BOARD_HEIGHT):
                if ((x + y) % 2 == 0):
                    piece = checker.Checker(config.BLACK, point.Point(x, y), self)
                    self.checkers[config.BLACK].append(piece)
                    self.board[x][y] = piece

    def UndoMove(self, source, dest):
        if ((source.x == dest.x) and (source.y == dest.y)):
            print("Illegal move, you're not going anywhere!")
            return

        if (not self.WithinBounds(source.x, source.y)):
            print("Illegal move, UndoMove WithinBounds")
            return

        if (not self.WithinBounds(dest.x, dest.y)):
            print("Illegal move, UndoMove WithinBounds")
            return

        if (self[dest.x][dest.y] == None):
            print("pice missing, UndoMove")
            return

        if (self[source.x][source.y] != None):
            print("Illegal move, UndoMove self[source.x][source.y] != None")
            return

        if (source.x == dest.x) or (source.y == dest.y):
            print("Illegal move, UndoMove source.x == dest.x) or (source.y == dest.y")
            return

        # distnce should be either 1 or 2, for the time being.
        if (abs(source.x - dest.x) > 2) or (abs(source.y - dest.y) > 2):
            print("Impossible move at the moment.")
            return

        piece = self[dest.x][dest.y]

        # Is it a double step?
        if (abs(source.x - dest.x) == 2):
            # Make sure move is legal.
            midX = int(math.ceil((source.x + dest.x) / 2))
            midY = int(math.ceil((source.y + dest.y) / 2))
            dead = self[midX][midY]

            if (dead != None):
                print("Expecting empty spot.")
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
                print "Your going in the wrong direction"
                return
        
        piece.Move(source)
        self.board[source.x][source.y] = piece
        self.board[dest.x][dest.y] = None

    def MultipleMove(self, move_list):
        for move in move_list:
            self.Move(move['from'], move['to'])

    def MultipleUndoMove(self, move_list):
        for move in reversed(move_list):
            self.UndoMove(move['from'], move['to'])

    def Move(self, source, dest):
        if (not self.WithinBounds(source.x, source.y)):
            print("WithinBounds - Illegal move")
            return False

        if (not self.WithinBounds(dest.x, dest.y)):
            print("WithinBounds - Illegal move")
            return False

        if (self[source.x][source.y] == None):
            print("piece missing")
            return False

        if (self[dest.x][dest.y] != None):
            print("AAA Illegal move from %d,%d to %d,%d" % (source.x, source.y, dest.x, dest.y))
            return False

        if (source.x == dest.x) or (source.y == dest.y):
            print("BBB Illegal move")
            return False

        # distance should be either 1 or 2, for the time being.
        if (abs(source.x - dest.x) > 2 or abs(source.y - dest.y) > 2):
            print("Impossible move at the moment.")
            return False

        piece = self[source.x][source.y]

        # Is it a double step?
        if (abs(source.x - dest.x) == 2):
            # Make sure move is legal.
            midX = int(math.ceil((source.x + dest.x) / 2))
            midY = int(math.ceil((source.y + dest.y) / 2))
            dead = self[midX][midY]

            if (dead == None):
                print("Illegal move, dead == None")
                return False

            if (dead.Color == piece.Color):
                print("Can't eat your own kind.")
                return False

            # Eat!
            # NOTE there's no check for move direction here!, check is made in the checker class.
            self.RemovePiece(dead.Position)
        else:  # This is a single step make sure move direction is correct for selected piece.
            if piece.AdvanceDirection != (dest.x - source.x):
                print "Your going in the wrong direction"
                return False

        piece.Move(dest)
        self.board[dest.x][dest.y] = piece
        self.board[source.x][source.y] = None
        return True

    def RemovePiece(self, location):
        # Sanity checks.
        if (not self.WithinBounds(location.x, location.y)):
            print("Illegal move, RemovePiece")
            return

        piece = self.board[location.x][location.y]
        if (piece == None):
            print("No piece in given location.")
            return

        self.checkers[piece.Color].remove(piece)

        # Remove checker from board.
        self.board[location.x][location.y] = None


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