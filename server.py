import checkers
import config
import ws4py
import cherrypy
import json
import os
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

cherrypy.config.update({'server.socket_port': 80})
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

    def __init__(self):
        hIndex = open("index.html", "r")
        self.index_page = hIndex.read()
        hIndex.close()

    @cherrypy.expose
    def index(self):
        return self.index_page

    @cherrypy.expose
    def ws(self):
        # you can access the class instance through
        handler = cherrypy.request.ws_handler


cherrypy.quickstart(Root(), '/', config={'/ws': {'tools.websocket.on': True, 'tools.websocket.handler_cls': server},
                                         '/': {'tools.sessions.on': True, 'tools.staticdir.root': os.path.abspath(os.getcwd())},
                                         '/js': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'C:\\dev\\checkers\\js\\'},
                                         '/images': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'C:\\dev\\checkers\\images\\'}})