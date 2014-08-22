import checkers
import config
import ws4py
import cherrypy
import json
import os
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool

cherrypy.config.update({'server.socket_port': 8080})
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()


class GameQueue:
    def __init__(self):
        # Adds an empty game.
        game = checkers.Game()
        self.games = {}
        self.games[game.id] = game
        self.last_added_game = game

    def CreateGame(self):
        game = checkers.Game()
        self.games[game.id] = game
        self.last_added_game = game

    def JoinPlayer(self, connection):
        # TODO: LOCK!

        # Get last game object in our list.
        game = self.last_added_game

        if game.IsGameFull():
            self.CreateGame()

        # Create a new player object.
        color = config.WHITE if (len(game.players) == 0) else config.BLACK
        #humanPlayer = checkers.HumanPlayer(color, game.board.checkers[color], game.board, connection, game)
        humanPlayer = checkers.HumanPlayer(color, connection, game)

        # Add player to game.
        game.JoinPlayer(humanPlayer)

        return humanPlayer

    def PlayerLeft(self, player):

        game_id = player.game.id

        if player.game.id in self.games:
            del self.games[player.game.id]

        # Drops player from game.
        player.game.DropPlayer(player)

        # Only if last_add_game is the game we've just removed, create a new game.
        if self.last_added_game.id == game_id:
            self.CreateGame()

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
            # assign player with connection
            self.player = player
            response = {}
            response['result'] = True
            response['player_color'] = player.color
            self.send(json.dumps(response))

    def opened(self):
        self.MsgHandler = None
        print "connection opened."

    def closed(self, code, reason=None):
        if(self.player != None):
            gGameQueue.PlayerLeft(self.player)
            print "Player has left the game."
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
    home_dir = os.path.dirname(os.path.realpath(__file__))
    js_dir = os.path.join(home_dir, "js")
    images_dir = os.path.join(home_dir, "images")
    sounds_dir = os.path.join(home_dir, "sounds")

    cherrypy.config.update( {'server.socket_host': '0.0.0.0'} )
    cherrypy.quickstart(Root(), '/', config={'/ws': {'tools.websocket.on': True, 'tools.websocket.handler_cls': server},
                                             '/': {'tools.sessions.on': True, 'tools.staticdir.on': True,
                                                   'tools.staticdir.dir': os.path.abspath(os.getcwd())},
                                             '/js': {'tools.staticdir.on': True,
                                                     'tools.staticdir.dir': js_dir},
                                             '/images': {'tools.staticdir.on': True,
                                                         'tools.staticdir.dir': images_dir},
                                            '/sounds': {'tools.staticdir.on': True,
                                                         'tools.staticdir.dir': sounds_dir}})

if __name__ == '__main__':
    main()