import checkers
import config
import ws4py
import cherrypy
import json
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

cherrypy.config.update({'server.socket_port': 9000})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()


class server(ws4py.websocket.WebSocket):

    def received_message(self, message):
        #self.send(message.data, message.is_binary)
        print "message received."
        if(self.MsgHandler != None):
            self.MsgHandler(message.data)
        else:
            response = {}
            response['result'] = True
            self.send(json.dumps(response))

            # Assuming we've received a JOIN MSG.
            human = checkers.HumanPlayer(config.WHITE, checkers.game.board.checkers[config.WHITE], checkers.game.board, self)
            comp = checkers.CompPlayer(config.WHITE, checkers.game.board.checkers[config.BLACK], checkers.game.board)
            checkers.game.JoinPlayer(human)
            checkers.game.JoinPlayer(comp)
    def opened(self):
        self.MsgHandler = None
        print "connection opened."
        checkers.game = checkers.Game()

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