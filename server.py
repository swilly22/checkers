import checkers
import point
import config
import ws4py
import cherrypy
import json
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

INIT = 0
POSSIBLE_MOVES = 1
MOVE = 2

cherrypy.config.update({'server.socket_port': 9000})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()


class server(ws4py.websocket.WebSocket):
    def InitialBoard(self):
        whitesPositions = []
        blacksPosition = []

        for piece in self.game.board.checkers[config.WHITE]:
            whitesPositions.append({'x': piece.Position.x, 'y': piece.Position.y})

        for piece in self.game.board.checkers[config.BLACK]:
            blacksPosition.append({'x': piece.Position.x, 'y': piece.Position.y})

        data = {'whites': whitesPositions, 'blacks': blacksPosition}
        return data

    def HandleMsg(self, msg):
        request = json.loads(msg)
        if(request['action'] == INIT):
            response = self.InitialBoard()
            response['response_to'] = INIT
            self.send(json.dumps(response))

        elif (request['action'] == POSSIBLE_MOVES):
            piecePosition = request['piece_position']
            piece = self.game.board[piecePosition['x']][piecePosition['y']]
            if piece == None:
                print "No piece at given position."
            else:
                moves = piece.PossibleMoves()
                response = {}
                response['response_to'] = POSSIBLE_MOVES
                response['possible_moves'] = moves
                self.send(json.dumps(response))
        elif (request['action'] == MOVE):
            src = point.Point(request['from']['x'], request['from']['y'])
            dest = point.Point(request['to']['x'], request['to']['y'])
            res = self.game.board.Move(src, dest)
            response = {}
            response['result'] = res
            self.send(json.dumps(response))

        else:
            print "Unknow action"

    def received_message(self, message):
        #self.send(message.data, message.is_binary)

        self.HandleMsg(message.data)

        print "message received."

    def opened(self):
        print "connection opened."
        self.game = checkers.Game()

    def closed(self, code, reason=None):
        print "connection closed."


class Root(object):
    @cherrypy.expose
    def index(self):
        return 'some HTML with a websocket javascript connection'

    @cherrypy.expose
    def ws(self):
        # you can access the class instance through
        handler = cherrypy.request.ws_handler


cherrypy.quickstart(Root(), '/', config={'/ws': {'tools.websocket.on': True, 'tools.websocket.handler_cls': server}})