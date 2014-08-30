import config
import json
from player import Player

class HumanPlayer(Player):
    
    #def __init__(self, _color, _checkers, _game_board, _socket, game):
    def __init__(self, _color, _socket, game):
        # Call parent constructor.
        Player.__init__(self, _color, game)
        self.socket = _socket

    def __del__(self):
        print("HumanPlayer destructor")

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

    def HandleMsg(self, msg):
        request = json.loads(msg)

        if(request['action'] == config.INIT):
            response = self.game_board.GetPiecesPosition()
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