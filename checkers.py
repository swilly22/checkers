import sys
import math
import board
import checker
import config
import Tree


class Play(object):
    def __init__(self, _from, _to):
        self._from = _from
        self._to = _to

    @property
    def From(self):
        return self._from

    @property
    def To(self):
        return self._to


class Player(object):
    def __init__(self, _color, _checkers, _game_board):
        self.color = _color
        self.checkers = _checkers
        self.game_board = _game_board

    @property
    def CheckersCount(self):
        return len(self.checkers)

    def Ratio(self, root):
        if (root == None):
            return

        for node in root.Nodes:
            self.Ratio(node)
            root.Value[0] = root.Value[0] + node.Value[0]
            root.Value[1] = root.Value[1] + node.Value[1]


    # Greedy tries to find the move wich will result with most "eats"
    def Play(self):
		# Step 1. Incase we've got a piece which is able to 'eat' we must use it.
		# Determin if there's such piece.
		bMustEat = False

		# foreach checker see if it can 'eat'
		for checker in self.checkers:
		    if (checker.CanEat() == True):
		        bMustEat = True
		        break

		# construct a list of checkers to test, each checker will be identified by it's position
		# this is becuase our list might change over time, and we'll might calculate a result
		# for the same piece multipal times, missleading ourselves. 
		checkersPositionsList = []
		for checker in self.checkers:
		    if (len(checker.PossibleMoves()) == 0):  # Piece can't move.
		        continue

			if(checker.CanEat() != bMustEat): # We must 'eat' and this piece can't.
				continue

		    checkersPositionsList.append(checker.Position)

		forest = []
		# freach checker to concider, see what moves can we perform.
		for checkerPos in checkersPositionsList:
		    checker = self.game_board[checkerPos.x][checkerPos.y]

		    # Create Tree root.
		    root = Tree.Tree([0, 0])
		    forest.append((checker.Position, root))

		    for move in checker.PossibleMoves():
		        if (move[0]['eat'] == 1):
		            node = root.AddNode([len(move), 0])
		        else:
		            node = root.AddNode([0, 0])

		        self.game_board.MultipleMove(move)
		        self.LookAHead(node, 4)
		        self.game_board.MultipleUndoMove(move)

		    self.Ratio(root)
		    #print root.Value

		print("Position\twins\tlosses\twin ration\tlose ration")

		for item in forest:
			checkerPosition = item[0]
			tree = item[1]
			checker = self.game_board[checkerPosition.x][checkerPosition.y]
			wins = tree.Value[0]
			losses = tree.Value[1]
			winRatio = float(wins) / (wins + losses)
			loseRatio = 1 - winRatio
			print ("%s\t%d\t%d\t%f\t%f")% (checker.Position, wins, losses, winRatio, loseRatio)

    def AllMoves(self):
        eatersList = []  # List of 'eat' moves
        noneEatersList = []  # List of none 'eat' moves

        # foreach checker see if it can 'eat'
        for checker in self.checkers:
            if (checker.CanEat() == True):
                eatersList = eatersList + checker.PossibleMoves()
            else:
                noneEatersList = noneEatersList + checker.PossibleMoves()

        # Determin which list to use.
        if (len(eatersList) > 0):
            return eatersList
        else:
            return noneEatersList


    def LookAHead(self, root, depth):
        if (depth == 0):
            return

        # Opponent's turn.
        if ((depth % 2) == 0):
            player = self.opponent
            multipler = -1
        else:
            player = self
            multipler = 1

        # Get all possible moves.
        for move in player.AllMoves():

            # Add new node.
            if (move[0]['eat'] == 1):
                if (multipler == 1):
                    node = root.AddNode([len(move), 0])  # points.
                else:
                    node = root.AddNode([0, len(move)])  # points.
            else:
                node = root.AddNode([0, 0])  # neutral.

            # Perform move.
            self.game_board.MultipleMove(move)

            # Call recursive.
            self.LookAHead(node, depth - 1)

            # Restore state.
            self.game_board.MultipleUndoMove(move)


class Game(object):
    def __init__(self):
        self.board = board.Board()
        self.player1 = Player(config.WHITE, self.board.checkers[config.WHITE], self.board)
        self.player2 = Player(config.BLACK, self.board.checkers[config.BLACK], self.board)
        self.currentPlayer = self.player1
        self.player1.opponent = self.player2
        self.player2.opponent = self.player1

    def GameLoop(self):
        while self.player1.CheckersCount > 0 and self.player2.CheckersCount > 0:
            self.currentPlayer.Play()

            # Change turn.
            if self.currentPlayer == self.player1:
                self.currentPlayer = self.player2
            else:
                self.currentPlayer = self.player1

        # Who won?
        if (self.player1.CheckersCount > 0):
            print "WHITES win!"
        else:
            print "BLACKS win!"


# game = Game()
# game.GameLoop()
