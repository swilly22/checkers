import board
import checker
import point
import config
import Tree
import json
import random
from abc import ABCMeta, abstractmethod


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
    __metaclass__ = ABCMeta
    def __init__(self, _color, _checkers, _game_board):
        self.color = _color
        self.checkers = _checkers
        self.game_board = _game_board
        self.subscribers = [] # Used for Event mechanism.

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

    def OpponentMove(self, src, dest):
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

    def FireMove(self, src, dest):
        for subscriber in self.subscribers:
            subscriber(src, dest)

class HumanPlayer(Player):
    
    def __init__(self, _color, _checkers, _game_board, _socket):
        # Call parent constructor.
        Player.__init__(self, _color, _checkers, _game_board)
        self.socket = _socket
        self.socket.MsgHandler = self.HandleMsg

    def Play(self):
        # Send message to player, letting him / her know its her turn to play.
        response = {}
        response['fromServer'] = True
        response['action'] = config.PLAY
        self.socket.send(json.dumps(response))
        pass

    def Wait(self):
        # Send message to player.
        response = {}
        response['fromServer'] = True
        response['action'] = config.WAIT
        self.socket.send(json.dumps(response))

    def Queened(self, position):
        # Send message to player.
        response = {}
        response['fromServer'] = True
        response['action'] = config.QUEENED
        response['position'] = {}
        response['position']['x'] = position.x
        response['position']['y'] = position.y
        self.socket.send(json.dumps(response))

    def JoinedGame(self):
        pass

    def OpponentMove(self, src, dest):
        # Send message to player, letting him / her know its her turn to play.
        response = {}
        response['fromServer'] = True
        response['action'] = config.MOVE
        response['src'] = {}
        response['dest'] = {}
        response['src']['x'] = src.x
        response['src']['y'] = src.y
        response['dest']['x'] = dest.x
        response['dest']['y'] = dest.y
        self.socket.send(json.dumps(response))

    # TODO, move this Method to some place else.
    def InitialBoard(self):
        whitesPositions = []
        blacksPosition = []

        for piece in self.game_board.checkers[config.WHITE]:
            whitesPositions.append({'x': piece.Position.x, 'y': piece.Position.y})

        for piece in self.game_board.checkers[config.BLACK]:
            blacksPosition.append({'x': piece.Position.x, 'y': piece.Position.y})

        data = {'whites': whitesPositions, 'blacks': blacksPosition}
        return data

    def HandleMsg(self, msg):
        request = json.loads(msg)

        if(request['action'] == config.INIT):
            response = self.InitialBoard()
            self.socket.send(json.dumps(response))

        elif (request['action'] == config.POSSIBLE_MOVES):
            piecePosition = request['piece_position']
            piece = self.game_board[piecePosition['x']][piecePosition['y']]
            if piece == None:
                print "No piece at given position."
                response = {}
                response['error'] = 'No piece at given position'
                self.socket.send(json.dumps(response))
            elif piece.Color != self.color:
                print "You don't own this piece."
                response = {}
                response['error'] = 'You do not own this piece.'
                self.socket.send(json.dumps(response))
            elif self.CanEat() and not piece.CanEat():
                print "Player must eat, this piece can't."
                response = {}
                response['error'] = "You must eat"
                response['possible_moves'] = []
                self.socket.send(json.dumps(response))
            else:
                moves = piece.PossibleMoves()
                response = {}
                response['possible_moves'] = moves
                self.socket.send(json.dumps(response))

        elif (request['action'] == config.MOVE):
            src = point.Point(request['from']['x'], request['from']['y'])
            dest = point.Point(request['to']['x'], request['to']['y'])
            piece = self.game_board[src.x][src.y]
            if piece.Color != self.color:
                print "You don't own this piece."
                response = {}
                response['error'] = 'You do not own this piece.'
                self.socket.send(json.dumps(response))
            else:
                res = self.game_board.Move(src, dest)
                response = {}
                response['result'] = res
                self.socket.send(json.dumps(response))
                self.FireMove(src, dest)

        else:
            print "Unknown action"

class CompPlayer(Player):

    def __init__(self, _color, _checkers, _game_board):
        Player.__init__(self, _color, _checkers, _game_board)

    def Play(self):
        # Step 1. Incase we've got a piece which is able to 'eat' we must use it.
        # Determin if there's such piece.
        bMustEat = self.CanEat()

        # construct a list of checkers to test, each checker will be identified by it's position
        # this is because our list might change over time, and we'll might calculate a result
        # for the same piece multiple times, misleading ourselves.
        checkersPositionsList = []
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
            root = Tree.Tree([0, 0])
            forest.append((checker.Position, root))

            for move in checker.PossibleMoves():
                if (move[0]['eat'] == 1):
                    node = root.AddNode([len(move), 0])
                else:
                    node = root.AddNode([0, 0])

                node.move_to = move[0]['to']
                self.game_board.MultipleMove(move)
                self.LookAHead(node, 4)
                self.game_board.MultipleUndoMove(move)

            self.Ratio(root)
            #print root.Value

        print("Position\twins\tlosses\twin ration\tlose ration")

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
            winRatio = float(wins) / (wins + losses)
            loseRatio = 1 - winRatio
            print ("%s\t%d\t%d\t%f\t%f")% (checker.Position, wins, losses, winRatio, loseRatio)
            if((wins - losses) > MaxDiff):
                MaxDiff = (wins - losses)
                SelectedTree = tree
                src = checkerPosition

        MaxDiff = float("-inf") # - infinity.
        for node in SelectedTree.Nodes:
            wins = node.Value[0]
            losses = node.Value[1]
            diff = wins - losses
            if(diff > MaxDiff):
                MaxDiff = diff
                dest = node.move_to

        # Perform move.
        res = self.game_board.Move(src, dest)
        self.FireMove(src, dest)

    def Wait(self):
        pass

    def JoinedGame(self):
        pass

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

    def Ratio(self, root):
        if (root == None):
            return

        for node in root.Nodes:
            self.Ratio(node)
            root.Value[0] = root.Value[0] + node.Value[0]
            root.Value[1] = root.Value[1] + node.Value[1]

class Game(object):
    def __init__(self):
        self.board = board.Board()
        self.players = []
        self.currentPlayer = None

    def JoinPlayer(self, player):
        if(len(self.players) == 2):
            print "Game full."
            return
        
        self.players.append(player)

        if(len(self.players) == 2):
            self.players[0].opponent = self.players[1]
            self.players[0].RegisterOnMove(self.OnMove)

            self.players[1].opponent = self.players[0]
            self.players[1].RegisterOnMove(self.OnMove)

            self.currentPlayer = self.players[0]
            self.GameLoop()

    def ChangeTurn(self):
        # Change turn.
        self.currentPlayer.Wait()
        if self.currentPlayer == self.players[0]:
            self.currentPlayer = self.players[1]
        else:
            self.currentPlayer = self.players[0]

    def OnMove(self, src, dest):
        # Update other player about the move.
        self.currentPlayer.opponent.OpponentMove(src, dest)

        # Did checker reached the end of the board? if so queen it.
        bQueen = False
        piece = self.board[dest.x][dest.y]
        if(piece.__class__.__name__ == "Checker"):
            if((piece.AdvanceDirection == 1 and piece.Position.x == config.BOARD_HEIGHT - 1) or
            (piece.AdvanceDirection == -1 and piece.Position.x == 0)):
                print("Queened!")
                bQueen = True
                queen = checker.Queen(piece.Color, dest, self.board)
                # Remove old piece.
                self.board.RemovePiece(dest)
                # Add new queen.
                self.board.AddPiece(queen, dest)
                #Let player know he / she just got a new queen.
                self.currentPlayer.Queened(dest)

        # We'll figure out if a move was an "eat" move by the distance of the move.
        bEat = abs (src.x - dest.x) == 2
        if(bEat == True and piece.CanEat() and not bQueen):
            # Keep eating...
            self.currentPlayer.Play()
            return

        self.ChangeTurn()
        self.GameLoop()

    def GameLoop(self):
        # Do we still have pieces on the board?
        if(self.players[0].CheckersCount > 0 and self.players[1].CheckersCount > 0):
            # Check for draw, both players can't move.
            if(len(self.players[0].AllMoves()) == 0 and len(self.players[1].AllMoves()) == 0):
                #Draw.
                return

            # Can current player move?
            if(len(self.currentPlayer.AllMoves()) == 0):
                # Player can't move.
                self.ChangeTurn()
                
            self.currentPlayer.Play()

        else:
            # Who won?
            if (self.player[0].CheckersCount > self.player[1].CheckersCount):
                print "player1 win!"
            else:
                print "player2 win!"

game = None
# game.GameLoop()
