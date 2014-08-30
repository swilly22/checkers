import checkers
from human_player import HumanPlayer
from computer_player import CompPlayer
from spectator import Spectator
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

    def JoinHumanPlayer(self, connection):
        # TODO: LOCK!

        # Get last game object in our list.
        game = self.last_added_game

        if game.IsGameFull():
            self.CreateGame()

        # Create a new player object.
        color = config.WHITE if (len(game.players) == 0) else config.BLACK
        humanPlayer = HumanPlayer(color, connection, game)

        # Add player to game.
        game.JoinPlayer(humanPlayer)

        return humanPlayer

    def JoinCompPlayer(self, level, strategy):
        # TODO: LOCK!

        # Get last game object in our list.
        game = self.last_added_game

        if game.IsGameFull():
            self.CreateGame()

        # Create a new player object.
        color = config.WHITE if (len(game.players) == 0) else config.BLACK
        compPlayer = CompPlayer(color, game, level, strategy)

        # Add player to game.
        game.JoinPlayer(compPlayer)

        return compPlayer

    def PlayerLeft(self, player):

        game = player.game
        game_id = game.id

        if game_id in self.games:
            del self.games[game_id]

        # Drops player from game.
        game.DropPlayer(player)

        # Only if last_add_game is the game we've just removed, create a new game.
        if self.last_added_game.id == game_id:
            self.CreateGame()

gGameQueue = GameQueue()


class server(ws4py.websocket.WebSocket):
    def received_message(self, message):
        global gGameQueue

        print "message received."

        request = json.loads(message.data)
        if(request['action'] == config.JOIN):
            player = gGameQueue.JoinHumanPlayer(self)

            # Add a computer opponent.
            #gGameQueue.JoinCompPlayer(config.INTERMEDIATE, config.OFFENSIVE)

            # assign player with connection
            self.player = player

            # Respond to player.
            response = {}
            response['result'] = True
            response['player_color'] = player.color
            self.send(json.dumps(response))

        elif(request['action'] == config.VIEWER_JOIN):
            spectator = Spectator(self)
            self.player = spectator
            gGameQueue.last_added_game.JoinSpectator(spectator)

        else:
            if (self.player != None):
                self.player.HandleMsg(message.data)

            # Testing
            from predicted_player import predicted_player
            comp1 = CompPlayer(config.WHITE, gGameQueue.last_added_game, 2, config.OFFENSIVE)
            #comp2 = CompPlayer(config.BLACK, gGameQueue.last_added_game, 3, config.OFFENSIVE)

            gGameQueue.last_added_game.JoinPlayer(comp1)
            #gGameQueue.last_added_game.JoinPlayer(comp2)

            #predicted1 = predicted_player(config.WHITE, gGameQueue.last_added_game, config.AMATEUR, config.OFFENSIVE)
            predicted2 = predicted_player(config.BLACK, gGameQueue.last_added_game, config.AMATEUR, config.OFFENSIVE)

            #gGameQueue.last_added_game.JoinPlayer(predicted1)
            gGameQueue.last_added_game.JoinPlayer(predicted2)

            # end of Testing

    def opened(self):
        self.MsgHandler = None
        print "connection opened."

    def closed(self, code, reason=None):
        if(self.player is not None):
            if isinstance(self.player, checkers.HumanPlayer):
                gGameQueue.PlayerLeft(self.player)
                print "Player has left the game."
                del self.player
            elif isinstance(self.player, checkers.Spectator):
                self.player.game.DropSpectator(self.player)
                del self.player
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