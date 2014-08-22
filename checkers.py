import board
import checker
import point
import config
import Tree
import json
import uuid
import random
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

class HumanPlayer(Player):
    
    #def __init__(self, _color, _checkers, _game_board, _socket, game):
    def __init__(self, _color, _socket, game):
        # Call parent constructor.
        #Player.__init__(self, _color, _checkers, _game_board, game)
        Player.__init__(self, _color, game)
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

    def OpponentMove(self, moves):
        # Send message to player.
        response = {}
        response['fromServer'] = True
        response['action'] = config.MOVE
        response['moves'] = moves
        self.socket.send(json.dumps(response))

    def OpponentLeft(self):
        self.opponent = None
        # Send message notifying player his opponent has left the game.
        message = {}
        message['fromServer'] = True
        message['action'] = config.OPPONENT_LEFT
        self.socket.send(json.dumps(message))

    def OpponentQueen(self, position):
        # Send message to player, currently I don't see a reason why not
        # reuse the Queened method, although it's not this player who's
        # getting a new queen.
        self.Queened(position)

    # TODO, move this Method to some place else.
    def InitialBoard(self):
        whitesPositions = []
        blacksPosition = []

        #Test
        #self.game_board.ClearBoard()
        #checker1 = checker.Checker(config.WHITE, point.Point(6,6), self.game_board)
        #checker2 = checker.Checker(config.BLACK, point.Point(2,0), self.game_board)
        #self.game_board.AddPiece(checker1, checker1.Position)
        #self.game_board.AddPiece(checker2, checker2.Position)
        #EndOfTest

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
            # Sanity check on first move.
            requestedMoves = request['moves']
            firstMove = requestedMoves[0]
            src = point.Point(firstMove['from']['x'], firstMove['from']['y'])
            piece = self.game_board[src.x][src.y]
            if piece == None:
                print "Missing piece."
                response = {}
                response['error'] = 'Missing piece, probably out of sync.'
                self.socket.send(json.dumps(response))
                return

            if piece.Color != self.color:
                print "You don't own this piece."
                response = {}
                response['error'] = 'You do not own this piece.'
                self.socket.send(json.dumps(response))
                return

            # Make sure passed moves are valid, Get piece possible moves.
            for possibleMove in piece.PossibleMoves():
                # Sanity validation on number of moves.
                if(len(possibleMove) != len(requestedMoves)):
                    continue
                else:
                    idx = 0
                    # Make sure each move is valid.
                    for move in possibleMove:
                        if(move['from'].x != requestedMoves[idx]['from']['x'] or
                        move['from'].y != requestedMoves[idx]['from']['y'] or
                        move['to'].x != requestedMoves[idx]['to']['x'] or
                        move['to'].y != requestedMoves[idx]['to']['y'] ):
                            break

                        # Advance
                        idx+=1
                    # Out of loop did we make it to the end of our check list?
                    if(idx == len(requestedMoves) and idx == len(possibleMove)):
                        # legit request, i've decided to pass possibleMove instade of
                        # requetedMoves as it in a bit different format, which is supported
                        # by the underline functions.
                        res = self.game_board.MultipleMove(possibleMove)
                        # TODO think what to do incase res equals false.
                        response = {}
                        response['result'] = True if(res != None) else False
                        self.socket.send(json.dumps(response))

                        # Let subscribers know about the move just performed.
                        self.FireMove(possibleMove)

                        # We're done!
                        return

            print "Given move request was denied."
            response = {}
            response['error'] = 'invalid move request.'
            self.socket.send(json.dumps(response))
        else:
            print "Unknown action"

class CompPlayer(Player):

    #def __init__(self, _color, _checkers, _game_board, game):
    def __init__(self, _color, game):
        #Player.__init__(self, _color, _checkers, _game_board, game)
        Player.__init__(self, _color, game)

    def Play(self, specificPiece = None, eat_mode = False):
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
            root = Tree.Tree([0, 0])
            forest.append((checker.Position, root))

            for move in checker.PossibleMoves(eat_mode):
                if (move[0]['eat'] == 1):
                    node = root.AddNode([len(move), 0])
                else:
                    node = root.AddNode([0, 0])

                node.move_to = move[0]['to']
                # Experimental
                node.move_taken = move
                # End of Experimental
                performedMoves = self.game_board.MultipleMove(move)
                self.LookAHead(node, 4)
                self.game_board.MultipleUndoMove(performedMoves)

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
        SelectedNode = None
        for node in SelectedTree.Nodes:
            wins = node.Value[0]
            losses = node.Value[1]
            diff = wins - losses
            if(diff > MaxDiff):
                MaxDiff = diff
                dest = node.move_to
                SelectedNode = node

        # Perform move.
        #res = self.game_board.Move(src, dest)
        self.game_board.MultipleMove(SelectedNode.move_taken)
        #self.FireMove(src, dest)
        self.FireMove(SelectedNode.move_taken)

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

class Game(object):
    def __init__(self):
        self.board = board.Board()
        self.players = []
        self.currentPlayer = None
        self.id = uuid.uuid4()

    def IsGameFull(self):
        return True if (len(self.players) == 2) else False

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

    def DropPlayer(self, player):
        if player in self.players:
            self.players.remove(player)

        if player.opponent != None:
            opponent = player.opponent
            opponent.UnRegisterOnMove(self.OnMove)
            opponent.OpponentLeft()

    def ChangeTurn(self):
        # Change turn.
        self.currentPlayer.Wait()
        if self.currentPlayer == self.players[0]:
            self.currentPlayer = self.players[1]
        else:
            self.currentPlayer = self.players[0]

    #def OnMove(self, src, dest):
    def OnMove(self, move):
        # Update other player about the move.

        self.currentPlayer.opponent.OpponentMove(move)

        # Did checker reached the end of the board? if so queen it.
        #bQueen = False
        lastMove = move[len(move) - 1]
        dest = lastMove['to']
        piece = self.board[dest.x][dest.y]
        if(piece.__class__.__name__ == "Checker"):
            if((piece.AdvanceDirection == 1 and piece.Position.x == config.BOARD_HEIGHT - 1) or
            (piece.AdvanceDirection == -1 and piece.Position.x == 0)):
                print("Queened!")
                # bQueen = True
                queen = checker.Queen(piece.Color, dest, self.board)
                # Remove old piece.
                self.board.RemovePiece(dest)
                # Add new queen.
                self.board.AddPiece(queen, dest)
                # Let player know he / she just got a new queen.
                self.currentPlayer.Queened(dest)
                # Let opponent know about this new queen.
                self.currentPlayer.opponent.OpponentQueen(dest)
        
        self.ChangeTurn()
        self.GameLoop()

    def GameLoop(self):
        # Do we still have pieces on the board?
        if(self.players[0].CheckersCount > 0 and self.players[1].CheckersCount > 0):
            # Check for draw, both players can't move.
            if(len(self.players[0].AllMoves()) == 0 and len(self.players[1].AllMoves()) == 0):
                # Draw.
                return

            # Can current player move?
            if(len(self.currentPlayer.AllMoves()) == 0):
                # Player can't move.
                self.ChangeTurn()
                
            self.currentPlayer.Play()

        else:
            # Who won?
            if (self.players[0].CheckersCount > self.players[1].CheckersCount):
                print "player1 win!"
            else:
                print "player2 win!"

game = None
