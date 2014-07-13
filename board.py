import checker
import config
import point
import math
import sys
import play

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

    def UndoMove(self, move):
        # Sanity checks
        if (not self.IsLegalUndoMove(move)):
            return False

        # Get piece.
        piece = self[move.To.x][move.To.y]

        # Are we undoing an eat move?
        if(move.Eat):
            if(move.EatType == config.CHECKER):
                dead = checker.Checker(move.EatColor, move.EatPosition, self)
            else:
                dead = checker.Queen(move.EatColor, move.EatPosition, self)

            # Add revive piece to board
            self.board[dead.Position.x][dead.Position.y] = dead
            self.checkers[dead.Color].append(dead)

        # Undo move, restore piece to its original position
        piece.Move(move.From)
        self.board[move.From.x][move.From.y] = piece
        self.board[move.To.x][move.To.y] = None

        return True

    def MultipleMove(self, play_list):
        # Sanity check, make sure that if there's more than one move in the list
        # then all moves are eat moves.
        if(len(play_list) > 1):
            for move in play_list:
                if not move['eat']:
                    print("Move must be an wat move.")
                    return False

        moveCounter = 0
        for move in play_list:
            bCheckDirection = False if (moveCounter > 0 and move['eat']) else True
            if(not self.Move(move['from'], move['to'], bCheckDirection)):
                # TODO revert performed moves.
                return False
            moveCounter += 1

        return True

    def MultipleUndoMove(self, move_list):
        for move in reversed(move_list):
            self.UndoMove(move)

    def IsLegalMove(self, move, bCheckDirection = True):

        # Make sure play is within board bonds.
        if (not self.WithinBounds(move.From.x, move.From.y)):
            print("Illegal move, WithinBounds")
            return False

        if (not self.WithinBounds(move.To.x, move.To.y)):
            print("Illegal move, WithinBounds")
            return False

        # Make sure we're not staying put.
        if ((move.From.x == move.To.x) or (move.From.y == move.To.y)):
            print("Illegal move, you must move in both directions")
            return False

        # Make sure destination is not occupied
        if(self[move.To.x][move.To.y] != None):
            print("destination position occupied")
            return False

        # Get move piece.
        piece = self[move.From.x][move.From.y]

        # Make sure piece exists
        if(piece == None):
            print("Missing expected piece")
            return False

        # Determine travel distance
        # Find out move direction: up left, down left, etc.
        # Division is necessary to keep Distance equal to 1 / -1, (think vector normal).
        XDistance = abs(move.From.x - move.To.x)
        YDistance = abs(move.From.y - move.To.y)
        XDirection = (move.To.x - move.From.x) / XDistance
        YDirection = (move.To.y - move.From.y) / YDistance

        # Make sure we're travailing the same distance in both directions
        if(XDistance != YDistance):
            print("Illegal move, you must move an equal distance in both directions")
            return False

        # Incase we're dealing with a checker (not a queen).
        if(piece.Type == config.CHECKER):
            # Make sure travel distance is not bigger then two.
            if(XDistance > 2 or YDistance > 2):
                print("Checker can travel at most two steps.")
                return False

            # Check move direction.
            if(bCheckDirection and piece.AdvanceDirection != XDirection):
                print "Move, Your going in the wrong direction"
                return False

            # Incase of an 'eat' move:
            if(move.Eat == True):
                # Distance should be exactly two.
                if(XDistance != 2 or YDistance != 2):
                    print("Illegal move, when eating piece must travel two steps")
                    return False

            if(XDistance == 2 or YDistance == 2):
                if(not move.Eat):
                    print "Checker can't travel a distance of two without eating."
                    return False


        if(move.Eat == True):
            # Distance should be at least two.
            if(XDistance < 2 or YDistance < 2):
                print("Illegal move, when eating piece must travel at least two steps")
                return False

            # Make sure deadPosition is valid.
            deadPosition = point.Point(move.To.x - XDirection, move.To.y - YDirection)
            if(deadPosition.x != move.EatPosition.x or deadPosition.y != move.EatPosition.y):
                print("Invalid eat position")
                return False

            deadPiece = self[move.EatPosition.x][move.EatPosition.y]
            if(deadPiece == None):
                print("Missing expected piece")
                return False

            # Make sure play data matches board state
            if(deadPiece.Color == piece.Color):
                print("You can't eat your own kind")
                return False

            # Make sure no cannibalism is takes place.
            if(deadPiece.Color != move.EatColor):
                print("Color conflict")
                return False

            # Make sure play data matches board state
            if(deadPiece.Type != move.EatType):
                print("Type conflict")
                return False

        # at last
        return True

    def IsLegalUndoMove(self, move):
        # Make sure play is within board bonds.
        if (not self.WithinBounds(move.From.x, move.From.y)):
            print("Illegal move, WithinBounds")
            return False

        if (not self.WithinBounds(move.To.x, move.To.y)):
            print("Illegal move, WithinBounds")
            return False

        # Make sure we're not staying put.
        if ((move.From.x == move.To.x) or (move.From.y == move.To.y)):
            print("Illegal move, you must move in both directions")
            return False

        # Make sure origin is free
        if(self[move.From.x][move.From.y] != None):
            print("destination position occupied")
            return False

        # Get move piece.
        piece = self[move.To.x][move.To.y]

        # Make sure piece exists
        if(piece == None):
            print("Missing expected piece")
            return False

        # Determine travel distance
        # Find out move direction: up left, down left, etc.
        # Division is necessary to keep Distance equal to 1 / -1, (think vector normal).
        XDistance = abs(move.From.x - move.To.x)
        YDistance = abs(move.From.y - move.To.y)
        XDirection = (move.To.x - move.From.x) / XDistance
        YDirection = (move.To.y - move.From.y) / YDistance

        # Make sure we're travailing the same distance in both directions
        if(XDistance != YDistance):
            print("Illegal move, you must move an equal distance in both directions")
            return False

        # Incase we're dealing with a checker (not a queen).
        if(piece.Type == config.CHECKER):
            # Make sure travel distance is not bigger then two.
            if(XDistance > 2 or YDistance > 2):
                print("Checker can travel at most two steps.")
                return False

            # TODO Check move direction.

        # Incase of an 'eat' move:
        if(move.Eat == True):
            # Distance should be exactly two.
            if(XDistance != 2 or YDistance != 2):
                print("Illegal move, when eating piece must travel two steps")
                return False

            # TODO Make sure deadPosition is valid.

            deadPiece = self[move.EatPosition.x][move.EatPosition.y]
            if(deadPiece != None):
                print("Expected a blank spot.")
                return False

            # Make sure no cannibalism is takes place.
            if(piece.Color == move.EatColor):
                print("Color conflict")
                return False

        # at last
        return True

    def Move(self, src, dest, bCheckDirection = True):

        # Determine travel distance
        # Find out move direction: up left, down left, etc.
        # Division is necessary to keep Distance equal to 1 / -1, (think vector normal).
        piece = self[src.x][src.y]
        if(piece == None):
            return None

        XDistance = abs(src.x - dest.x)
        YDistance = abs(src.y - dest.y)

        # check for division by zero
        if(XDistance == 0 or YDistance == 0):
            return None

        XDirection = (dest.x - src.x) / XDistance
        YDirection = (dest.y - src.y) / YDistance

        bEat = False
        move = play.Play(src, dest, False, None, None, None, piece.ShouldTurnIntoQueen(dest))

        # is this a potential eat move?
        if(XDistance > 1):
            deadPosition = point.Point(dest.x - XDirection, dest.y - YDirection)
            deadPiece = self[deadPosition.x][deadPosition.y]
            if (deadPiece != None):
                bEat = True
                move = play.Play(src, dest, bEat, deadPosition, deadPiece.Color, deadPiece.Type, piece.ShouldTurnIntoQueen(dest))
            else:
                bEat = False

        return self.PlayMove(move, bCheckDirection)

    def PlayMove(self, move, bCheckDirection = True):

        # Sanity checks, enforces game logic / rules.
        if(not self.IsLegalMove(move, bCheckDirection)):
            return None

        # Is it an eat move?
        if (move.Eat):
            self.RemovePiece(move.EatPosition)

        piece = self[move.From.x][move.From.y]
        piece.Move(move.To)
        self.board[move.To.x][move.To.y] = piece
        self.board[move.From.x][move.From.y] = None

        return move

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