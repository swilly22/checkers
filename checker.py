import config
import point
import board
import play
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

    @property
    def Type(self):
        return config.CHECKER if self.__class__.__name__ == "Checker" else config.QUEEN

    def Move(self, location):
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

    def ShouldTurnIntoQueen(self, xPosition):
        if(self.Type == config.QUEEN):
            return False

        if(self.advanceDirection == 1):
            if(xPosition == config.BOARD_HEIGHT):
                return True

        if(self.advanceDirection == -1):
            if(xPosition == 0):
                return True

        return False

    def PossibleMoves(self, eat_mode=False):

        moves = []

        for YDirection in [-1, 1]:
            if (board.Board.WithinBounds(self.position.x + self.advanceDirection, self.position.y + YDirection)):
                # Position empty
                dest = point.Point(self.position.x + self.advanceDirection, self.position.y + YDirection)
                if (self.game_board[dest.x][dest.y] == None):
                    bQueen = self.ShouldTurnIntoQueen(dest)
                    moves.append(play.Play(self.Position, dest, bQueened=bQueen))

                # Enemy ahead
                elif (self.game_board[dest.x][dest.y].Color != self.Color):
                    # Is it possible to EAT ?
                    if ((board.Board.WithinBounds(self.position.x + (self.advanceDirection * 2), self.position.y + (2 * YDirection))) and
                        (self.game_board[self.position.x + (self.advanceDirection * 2)][self.position.y + (2 * YDirection)] == None)):

                        dest = point.Point(self.position.x + (self.advanceDirection * 2), self.position.y + (2 * YDirection))
                        eatPositoin = point.Point(self.position.x + self.advanceDirection, self.position.y + YDirection)
                        eatColor = self.game_board[eatPositoin.x][eatPositoin.y].Color
                        eatType = self.game_board[eatPositoin.x][eatPositoin.y].Type
                        bQueen = self.ShouldTurnIntoQueen(dest)

                        move = play.Play(self.Position, dest, True, eatPositoin, eatColor, eatType)
                        moves.append([move])

        # In eat mode consider reverse direction eats.
        if (eat_mode):
            for YDirection in [-1, 1]:

                dest = point.Point(self.position.x - (self.advanceDirection * 2), self.position.y + (2 * YDirection))
                eatPosition = point.Point(self.position.x - self.advanceDirection, self.position.y + YDirection)

                if (board.Board.WithinBounds(dest.x, dest.y)):
                    # Position not empty
                    if (self.game_board[eatPosition.x][eatPosition.y] != None):
                        # Enemy behind us
                        if (self.game_board[eatPosition.x][eatPosition.y].Color != self.Color):
                            # Is it possible to EAT ?
                            if ((self.game_board[dest.x][dest.y] == None)):

                                eatColor = self.game_board[eatPosition.x][eatPosition.y].Color
                                eatType = self.game_board[eatPosition.x][eatPosition.y].Type
                                bQueen = self.ShouldTurnIntoQueen(dest)

                                move = play.Play(self.Position, dest, True, eatPosition,eatColor, eatType, bQueen)
                                moves.append([move])


        bEnforeMustEatRule = eat_mode
        # Should we enforce "must eat" rule?
        if(bEnforeMustEatRule == False):
            for move in moves:
                if (move[0].Eat == True):
                    bEnforeMustEatRule = True
                    break

        if (bEnforeMustEatRule == True):
            # Remove all NOT eat moves.
            eat_moves = [eat_move for eat_move in moves if eat_move[0].Eat == True]

            # See if we can eat more than one checker
            tmp = []  # tmp is here because we cannot modify iterated list.
            for eat_move in eat_moves:
                previous_position = self.Position

                checkDirection = False if(eat_mode) else False
                self.game_board.Move(eat_move[0].From, eat_move[0].To, bCheckDirection = checkDirection)
                additionalMoves = self.PossibleMoves(True)
                if (len(additionalMoves) > 0):
                    for addition in additionalMoves:
                        tmp.append(eat_move + addition)  # Concat arrays.
                else:
                    tmp.append(eat_move)

                self.game_board.UndoMove(eat_move)

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