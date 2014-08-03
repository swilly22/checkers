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


class GameQueue:
    def __init__(self):
        self.games = [checkers.Game()]

    def JoinPlayer(self, connection):
        # TODO: LOCK!

        # Get last game object in our list.
        game = self.games[-1]

        if game.IsGameFull():
            # Create a new game.
            game = checkers.Game()
            # Add game to list
            self.games.append(game)

        # Create a new player object.
        color = config.WHITE if (len(game.players) == 0) else config.BLACK
        humanPlayer = checkers.HumanPlayer(color, game.board.checkers[color], game.board, connection)

        # Add player to game.
        game.JoinPlayer(humanPlayer)

        return humanPlayer

    def PlayerLeft(self, player):

        # Get game object which given player takes part in.
        game = self.games[player.game_board]
        if (game == None):
            return

        # Drops player from game.
        game.DropPlayer(player)

        if (len(game.players) == 0):
            self.games.remove(game)


gGameQueue = GameQueue()


class server(ws4py.websocket.WebSocket):
    def received_message(self, message):
        global gGameQueue

        print "message received."
        if (self.MsgHandler != None):
            self.MsgHandler(message.data)
        else:
            # Assuming we've received a JOIN MSG.
            # human = checkers.HumanPlayer(config.WHITE, checkers.game.board.checkers[config.WHITE], checkers.game.board, self)
            #comp = checkers.CompPlayer(config.BLACK, checkers.game.board.checkers[config.BLACK], checkers.game.board)
            #checkers.game.JoinPlayer(human)
            #checkers.game.JoinPlayer(comp)
            player = gGameQueue.JoinPlayer(self)
            response = {}
            response['result'] = True
            response['player_color'] = player.color
            self.send(json.dumps(response))

    def opened(self):
        self.MsgHandler = None
        print "connection opened."

    def closed(self, code, reason=None):
        print "connection closed."


class Root(object):
    def __init__(self):
        pass

    @cherrypy.expose
    def ws(self):
        # you can access the class instance through
        handler = cherrypy.request.ws_handler


def main():
    # Start webserver
    cherrypy.config.update( {'server.socket_host': '0.0.0.0'} )
    cherrypy.quickstart(Root(), '/', config={'/ws': {'tools.websocket.on': True, 'tools.websocket.handler_cls': server},
                                             '/': {'tools.sessions.on': True, 'tools.staticdir.on': True,
                                                   'tools.staticdir.dir': os.path.abspath(os.getcwd())},
                                             '/js': {'tools.staticdir.on': True,
                                                     'tools.staticdir.dir': 'C:\\dev\\checkers\\js\\'},
                                             '/images': {'tools.staticdir.on': True,
                                                         'tools.staticdir.dir': 'C:\\dev\\checkers\\images\\'}})

    #cherrypy.server.socket_host = '0.0.0.0'
if __name__ == '__main__':
    main()