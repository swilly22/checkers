from abc import ABCMeta, abstractmethod

class Player(object):
    __metaclass__ = ABCMeta
    #def __init__(self, _color, _checkers, _game_board, game):
    def __init__(self, _color, game):
        self.color = _color
        self.game = game
        self.game_board = game.board
        self.checkers = game.board.checkers[_color]
        self.subscribers = [] # Used for Event mechanism.
        self.opponent = None

    @property
    def CheckersCount(self):
        return len(self.checkers)

    def CanEat(self):
        for piece in self.checkers:
            if (piece.CanEat() == True):
                return True
        return False

    # Greedy tries to find the move which will result with most "eats"
    @abstractmethod
    def Play(self):
        pass

    @abstractmethod
    def Wait(self):
        pass

    @abstractmethod
    def JoinedGame(self):
        pass

    def OpponentMove(self, move):
        pass

    def OpponentQueen(self, position):
        pass

    def OpponentLeft(self):
        pass

    def Queened(self, position):
        pass

    def AllMoves(self):
        eatersList = []  # List of 'eat' moves
        noneEatersList = []  # List of none 'eat' moves

        # foreach checker see if it can 'eat'
        for c in self.checkers:
            if (c.CanEat() == True):
                eatersList = eatersList + c.PossibleMoves()
            else:
                noneEatersList = noneEatersList + c.PossibleMoves()

        # Determin which list to use.
        if (len(eatersList) > 0):
            return eatersList
        else:
            return noneEatersList

    def RegisterOnMove(self,subscriber):
        self.subscribers.append(subscriber)

    def UnRegisterOnMove(self, subscriber):
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)

    def FireMove(self, move):
        for subscriber in self.subscribers:
            subscriber(move)