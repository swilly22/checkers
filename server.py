import checkers
import config
import ws4py
import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

cherrypy.config.update({'server.socket_port': 9000})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()


class server(ws4py.websocket.WebSocket):

    def received_message(self, message):
        #self.send(message.data, message.is_binary)

        self.MsgHandler(message.data)

        print "message received."

    def opened(self):
        global game
        print "connection opened."

        game = checkers.Game()
        human = checkers.HumanPlayer(config.WHITE, game.board.checkers[config.WHITE], game.board, self)
        comp = checkers.CompPlayer(config.WHITE, game.board.checkers[config.BLACK], game.board)
        game.JoinPlayer(human)
        game.JoinPlayer(comp)
        game.GameLoop()

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