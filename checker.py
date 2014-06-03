import config
import point
import board

class Checker(object):
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

    def CanEat(self):
        for move in self.PossibleMoves():
            if (move[0]['eat'] == 1):
                return True

        return False

    def PossibleMoves(self, eat_mode=False):

        moves = []

        # Step right.
        if (board.Board.WithinBounds(self.position.x + self.advanceDirection, self.position.y + 1)):
            # Position empty
            if (self.game_board[self.position.x + self.advanceDirection][self.position.y + 1] == None):
                moves.append([{'from': self.Position,
                               'to': point.Point(self.position.x + self.advanceDirection, self.position.y + 1),
                               'eat': False}])

            # Enemy ahead
            elif (self.game_board[self.position.x + self.advanceDirection][self.position.y + 1].Color != self.Color):
                # Is it possible to EAT ?
                if ((board.Board.WithinBounds(self.position.x + (self.advanceDirection * 2), self.position.y + 2)) and
                        (self.game_board[self.position.x + (self.advanceDirection * 2)][self.position.y + 2] == None)):
                    moves.append([{'from': self.Position,
                                   'to': point.Point(self.position.x + (self.advanceDirection * 2),
                                                     self.position.y + 2),
                                   'eat': True}])

        # Step left.
        if (board.Board.WithinBounds(self.position.x + self.advanceDirection, self.position.y - 1)):
            # Position empty
            if (self.game_board[self.position.x + self.advanceDirection][self.position.y - 1] == None):
                moves.append([{'from': self.Position,
                               'to': point.Point(self.position.x + self.advanceDirection, self.position.y - 1),
                               'eat': False}])

            # Enemy ahead
            elif (self.game_board[self.position.x + self.advanceDirection][self.position.y - 1].Color != self.Color):
                # Is it possible to EAT ?
                if ((board.Board.WithinBounds(self.position.x + (self.advanceDirection * 2), self.position.y - 2)) and
                        (self.game_board[self.position.x + (self.advanceDirection * 2)][self.position.y - 2] == None)):
                    moves.append([{'from': self.Position,
                                   'to': point.Point(self.position.x + (self.advanceDirection * 2),
                                                     self.position.y - 2),
                                   'eat': True}])

        # In eat mode consider reverse direction eats.
        if (eat_mode):
            # Eat right backwards.
            if (board.Board.WithinBounds(self.position.x - (self.advanceDirection * 2), self.position.y + 2)):
                # Position not empty
                if (self.game_board[self.position.x - self.advanceDirection][self.position.y + 1] != None):
                    # Enemy behind us
                    if (self.game_board[self.position.x - self.advanceDirection][
                                self.position.y + 1].Color != self.Color):
                        # Is it possible to EAT ?
                        if (
                                (self.game_board[self.position.x - (self.advanceDirection * 2)][self.position.y + 2] == None)):
                            moves.append([{'from': self.Position,
                                           'to': point.Point(self.position.x - (self.advanceDirection * 2),
                                                             self.position.y + 2),
                                           'eat': True}])

                        # Eat left backwards.
                if (board.Board.WithinBounds(self.position.x - (self.advanceDirection * 2), self.position.y - 2)):
                    # Position not empty
                    if (self.game_board[self.position.x - self.advanceDirection][self.position.y - 1] != None):
                        # Enemy behind us
                        if (self.game_board[self.position.x - self.advanceDirection][
                                    self.position.y - 1].Color != self.Color):
                            # Is it possible to EAT ?
                            if ((self.game_board[self.position.x - (self.advanceDirection * 2)][
                                         self.position.y - 2] == None)):
                                moves.append([{'from': self.Position,
                                               'to': point.Point(self.position.x - (self.advanceDirection * 2),
                                                                 self.position.y - 2),
                                               'eat': True}])

        bEnforeMustEatRule = False
        # Enforce must eat rule.
        for move in moves:
            if ((move[0]['eat'] == True) or eat_mode == True):
                bEnforeMustEatRule = True
                break

        if (bEnforeMustEatRule == True):
            # Remove all NOT eat moves.
            eat_moves = [eat_move for eat_move in moves if eat_move[0]['eat'] == True]

            # See if we can eat more than one checker in this
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