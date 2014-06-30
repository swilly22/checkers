import config
import point
import board
from abc import ABCMeta, abstractmethod

class Checker(object):
    __metaclass__ = ABCMeta
    def __init__(self, _color, location, _game_board):
        self.color = _color
        self.position = location
        self.game_board = _game_board
        self.advanceDirection = 1 if (_color == config.WHITE) else -1

    @property
    def Position(self):
        return point.Point(self.position.x, self.position.y)

    @property
    def Color(self):
        return self.color

    @property
    def AdvanceDirection(self):
        return self.advanceDirection

    def Move(self, location):
        #if (location.x == 3 and location.y == 3 and self.color == config.WHITE):
            #print ("1 moving from %d,%d to %d,%d") % (self.Position.x, self.Position.y, location.x, location.y)

        #if(self.Position.x == 3 and  self.Position.y == 3):
            #print ("2 moving from %d,%d to %d,%d") % (self.Position.x, self.Position.y, location.x, location.y)

        self.position = point.Point(location.x, location.y)

    def CanEat(self, eat_mode=False):
        for move in self.PossibleMoves(eat_mode):
            if (move[0]['eat'] == 1):
                return True

        return False

    def PossibleMoves(self, eat_mode=False):

        moves = []

        for YDirection in [-1, 1]:
            if (board.Board.WithinBounds(self.position.x + self.advanceDirection, self.position.y + YDirection)):
                # Position empty
                if (self.game_board[self.position.x + self.advanceDirection][self.position.y + YDirection] == None):
                    moves.append([{'from': self.Position,
                                    'to': point.Point(self.position.x + self.advanceDirection, self.position.y + YDirection),
                                    'eat': False}])

                # Enemy ahead
                elif (self.game_board[self.position.x + self.advanceDirection][self.position.y + YDirection].Color != self.Color):
                    # Is it possible to EAT ?
                    if ((board.Board.WithinBounds(self.position.x + (self.advanceDirection * 2), self.position.y + (2 * YDirection))) and
                        (self.game_board[self.position.x + (self.advanceDirection * 2)][self.position.y + (2 * YDirection)] == None)):
                        moves.append([{'from': self.Position,
                                        'to': point.Point(self.position.x + (self.advanceDirection * 2), self.position.y + (2 * YDirection)),
                                        'eat': True}])

        # In eat mode consider reverse direction eats.
        if (eat_mode):
            for YDirection in [-1, 1]:
                if (board.Board.WithinBounds(self.position.x - (self.advanceDirection * 2), self.position.y + (2 * YDirection))):
                    # Position not empty
                    if (self.game_board[self.position.x - self.advanceDirection][self.position.y + YDirection] != None):
                        # Enemy behind us
                        if (self.game_board[self.position.x - self.advanceDirection][self.position.y + YDirection].Color != self.Color):
                            # Is it possible to EAT ?
                            if ((self.game_board[self.position.x - (self.advanceDirection * 2)][self.position.y + (2 * YDirection)] == None)):
                                moves.append([{'from': self.Position,
                                                'to': point.Point(self.position.x - (self.advanceDirection * 2), self.position.y + (2 * YDirection)),
                                                'eat': True}])


        bEnforeMustEatRule = eat_mode
        # Should we enforce "must eat" rule?
        if(bEnforeMustEatRule == False):
            for move in moves:
                if (move[0]['eat'] == True):
                    bEnforeMustEatRule = True
                    break

        if (bEnforeMustEatRule == True):
            # Remove all NOT eat moves.
            eat_moves = [eat_move for eat_move in moves if eat_move[0]['eat'] == True]

            # See if we can eat more than one checker
            tmp = []  # tmp is here because we cannot modify iterated list.
            for eat_move in eat_moves:
                previous_position = self.Position
                self.game_board.Move(self.Position, eat_move[0]['to'], False) # Note if this is the first eat move, then direction must be enforced, currently it ain't.
                additionalMoves = self.PossibleMoves(True)
                if (len(additionalMoves) > 0):
                    for addition in additionalMoves:
                        tmp.append(eat_move + addition)  # Concat arrays.
                else:
                    tmp.append(eat_move)

                self.game_board.UndoMove(previous_position, eat_move[0]['to'])

            eat_moves = tmp
            return eat_moves

        else:
            return moves

class Queen(Checker):
    def __init__(self, _color, location, _game_board):
        # Call parent constructor.
        Checker.__init__(self, _color, location, _game_board)

    def CanEat(self):
        # Can we eat?
        for XDirection in [-1,1]:
            for YDirection in [-1,1]:
                currentPosition = point.Point(self.position.x, self.position.y)

                while(self.game_board.WithinBounds(currentPosition.x + XDirection, currentPosition.y + YDirection)):
                    piece = self.game_board[currentPosition.x + XDirection][currentPosition.y + YDirection]
                    if(piece != None and
                       piece.Color != self.Color and
                       self.game_board.WithinBounds(currentPosition.x + 2 * XDirection, currentPosition.y + 2 * YDirection) and
                       self.game_board[currentPosition.x + 2 * XDirection][currentPosition.y + 2 * YDirection] == None):
                            return True

                    # Move
                    currentPosition = point.Point(currentPosition.x + XDirection,
                                                  currentPosition.y + YDirection)

        return False

    def PossibleMoves(self, eat_mode=False):

        moves = []
        bMustEat = eat_mode

        for XDirection in [-1,1]:
            for YDirection in [-1,1]:
                currentPosition = point.Point(self.position.x, self.position.y)
                while(board.Board.WithinBounds(currentPosition.x, currentPosition.y)):
                    #print(board.Board.WithinBounds(currentPosition.x, currentPosition.y))
                    # Position empty
                    if (board.Board.WithinBounds(currentPosition.x + XDirection,
                                                 currentPosition.y + YDirection)):
                        piece = self.game_board[currentPosition.x + XDirection][currentPosition.y + YDirection]
                        if(piece == None):
                            moves.append([{'from': self.Position, # Original position
                                           'to': point.Point(currentPosition.x + XDirection, currentPosition.y + YDirection),
                                           'eat': False}])
                        # Enemy ahead
                        elif (piece.Color != self.Color):
                            # Is it possible to EAT ?
                            if ((board.Board.WithinBounds(currentPosition.x + 2 * XDirection, currentPosition.y + 2 * YDirection)) and
                                    (self.game_board[currentPosition.x + 2 * XDirection][currentPosition.y + 2 * YDirection] == None)):
                                bMustEat = True
                                moves.append([{'from': self.Position, # Original position
                                               'to': point.Point(currentPosition.x + 2 * XDirection,
                                                                 currentPosition.y + 2 * YDirection),
                                               'eat': True}])
                                # Break out of while loop as queen can't keep
                                # movein after this eat unless it continues on eating
                                # which will be reviled in recursive calls below.
                                break
                    # Advance.
                    currentPosition = point.Point(currentPosition.x + XDirection, currentPosition.y + YDirection)

        if (bMustEat == True):
            # Remove all NOT eat moves.
            eat_moves = [eat_move for eat_move in moves if eat_move[0]['eat'] == True]

            # See if we can eat more than one checker.
            tmp = []  # tmp is here because we cannot modify iterated list.
            for eat_move in eat_moves:
                previous_position = self.Position
                self.game_board.Move(self.Position, eat_move[0]['to'])
                additionalMoves = self.PossibleMoves(True)
                if (len(additionalMoves) > 0):
                    for addition in additionalMoves:
                        tmp.append(eat_move + addition)  # Concat arrays.
                else:
                    tmp.append(eat_move)

                self.game_board.UndoMove(previous_position, eat_move[0]['to'])

            eat_moves = tmp
            return eat_moves

        else:
            return moves