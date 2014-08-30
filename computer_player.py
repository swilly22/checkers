import config
from dal import DAL
from player import Player
from Tree import Tree

class CompPlayer(Player):

    def __init__(self, _color, game, level, strategy):
        #Player.__init__(self, _color, _checkers, _game_board, game)
        Player.__init__(self, _color, game)
        self.movesdb = DAL(config.DB_NAME) # todo concider changing dal method to static.
        self.level = level
        self.strategy = strategy

    def __del__(self):
        print("ComPlayer destructor")

    def Play(self, specificPiece = None, eat_mode = False):

        # Check to see if we've calculated this scenario in the past.
        cached_move = self.movesdb.GetMove(self.level, self.strategy, self.game_board)
        if cached_move is not None:
            # Indeed we did, perform cached move.
            self.game_board.MultipleMove(cached_move)
            self.FireMove(cached_move)
            return

        # Step 1. Incase we've got a piece which is able to 'eat' we must use it.
        # Determine if there's such piece.
        bMustEat = True if eat_mode or self.CanEat() else False

        # construct a list of checkers to test, each checker will be identified by it's position
        # this is because our list might change over time, and we'll might calculate a result
        # for the same piece multiple times, misleading ourselves.
        checkersPositionsList = []
        if(specificPiece != None):
            checkersPositionsList.append(specificPiece.Position)
        else:
            for checker in self.checkers:
                if (len(checker.PossibleMoves()) == 0):  # Piece can't move.
                    continue

                if(checker.CanEat() != bMustEat): # We must 'eat' and this piece can't.
                    continue

                checkersPositionsList.append(checker.Position)

        forest = []
        # foreach checker to consider, see what moves can we perform.
        for checkerPos in checkersPositionsList:
            checker = self.game_board[checkerPos.x][checkerPos.y]

            # Create Tree root.
            root = Tree([0, 0])
            root.queened = False
            forest.append((checker.Position, root))

            for move in checker.PossibleMoves(eat_mode):
                if (move[0]['eat'] == 1):
                    node = root.AddNode([len(move), 0])
                else:
                    node = root.AddNode([0, 0])

                #node.move_to = move[0]['to']
                node.queened = checker.ShouldTurnIntoQueen(move[-1]['to'])
                node.move_taken = move
                performedMoves = self.game_board.MultipleMove(move)
                self.LookAHead(node, self.level)
                self.game_board.MultipleUndoMove(performedMoves)

            self.Ratio(root)
            #print root.Value

        print("Position\twins\tlosses\twin ration\tlose ration\tqueen")

        # TODO think how to pick the 'best' play.
        SelectedTree = None
        MaxDiff = float("-inf") # - infinity.
        src = None
        dest = None
        for item in forest:
            checkerPosition = item[0]
            tree = item[1]
            checker = self.game_board[checkerPosition.x][checkerPosition.y]
            wins = tree.Value[0]
            losses = tree.Value[1]
            if (wins + losses) == 0:
                winRatio = 0
                loseRatio = 0
                wins = 1
                losses = 1
            else:
                winRatio = float(wins) / (wins + losses)
                loseRatio = 1 - winRatio

            # Incase this move can get us a queen, Increase chances for this move to get picked.
            if tree.queened == True:
                # todo think of a clever way to boost win ratio.
                winRatio += 0.1

            print ("%s\t%d\t%d\t%f\t%f\t%d")% (checker.Position, wins, losses, winRatio, loseRatio, tree.queened)
            #if((wins - losses) > MaxDiff):
            if((winRatio - loseRatio) > MaxDiff):
                MaxDiff = (winRatio - loseRatio)
                SelectedTree = tree
                src = checkerPosition

        # Select "best" node from "best" tree.
        MaxDiff = float("-inf") # - infinity.
        SelectedNode = None
        for node in SelectedTree.Nodes:
            wins = node.Value[0]
            losses = node.Value[1]
            if (wins + losses) == 0:
                winRatio = 0
                loseRatio = 0
                wins = 1
                losses = 1
            else:
                winRatio = float(wins) / (wins + losses)
                loseRatio = 1 - winRatio

            # Incase this move can get us a queen, Increase chances for this move to get picked.
            if node.queened == True:
                # todo think of a clever way to boost win ratio.
                winRatio += 0.1

            #diff = wins - losses
            diff = winRatio - loseRatio
            if(diff > MaxDiff):
                MaxDiff = diff
                SelectedNode = node

        # Cache move so we won't have to recalculate it.
        self.movesdb.InsertMove(self.level, self.strategy, self.game_board, SelectedNode.move_taken)

        # Perform move.
        self.game_board.MultipleMove(SelectedNode.move_taken)
        self.FireMove(SelectedNode.move_taken)

    def Wait(self):
        pass

    def JoinedGame(self):
        pass

    def OpponentLeft(self):
        self.opponent = None
        # Drop your self from the game.
        self.game.DropPlayer(self)

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
            checker = self.game_board[move[0]['from'].x][move[0]['from'].y]
            # Add new node.
            if (move[0]['eat'] == 1):
                if (multipler == 1):
                    node = root.AddNode([len(move), 0])  # points.
                else:
                    node = root.AddNode([0, len(move)])  # points.
            else:
                node = root.AddNode([0, 0])  # neutral.

            node.queened = checker.ShouldTurnIntoQueen(move[-1]['to'])

            # Perform move.
            performedMoves = self.game_board.MultipleMove(move)

            # Call recursive.
            self.LookAHead(node, depth - 1)

            # Restore state.
            self.game_board.MultipleUndoMove(performedMoves)

    def Ratio(self, root):
        if (root == None):
            return

        for node in root.Nodes:
            self.Ratio(node)
            root.Value[0] = root.Value[0] + node.Value[0]
            root.Value[1] = root.Value[1] + node.Value[1]
            if node.queened == True:
                root.queened = True