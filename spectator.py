import json
import config

class Spectator:
    def __init__(self, socket):
        self.socket = socket
        self.game = None

    def PlayerMove(self, moves):
        if self.socket is not None:
            msg = {}
            msg['fromServer'] = True
            msg['action'] = config.MOVE
            msg['moves'] = moves
            self.socket.send(json.dumps(msg))

    def Queen(self, position):
        # Send message to player.
        response = {}
        response['fromServer'] = True
        response['action'] = config.QUEENED
        response['position'] = {}
        response['position']['x'] = position.x
        response['position']['y'] = position.y
        self.socket.send(json.dumps(response))

    def Joined(self):
        msg = {}
        msg['result'] = True
        self.socket.send(json.dumps(msg))

    def HandleMsg(self, msg):
        request = json.loads(msg)

        if(request['action'] == config.INIT):
            response = self.game.board.GetPiecesPosition()
            self.socket.send(json.dumps(response))
        else:
            print "Unknown action"
