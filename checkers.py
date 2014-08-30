import board
import checker
import config
import json
import uuid

class Game(object):
    def __init__(self):
        self.board = board.Board()
        self.players = []
        self.currentPlayer = None
        self.id = uuid.uuid4()
        self.spectators = []

    def __del__(self):
        print("Game destructor")

    def IsGameFull(self):
        return True if (len(self.players) == 2) else False

    def JoinPlayer(self, player):
        if(len(self.players) == 2):
            print "Game full."
            return

        # Check for player's color, make sure there's no conflict (tow players of the same color)
        if len(self.players) == 1:
            if(self.players[0].color == player.color):
                raise Exception("Color %s already in used by other player"%(player.color))

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
            player.opponent.OpponentLeft()

    def JoinSpectator(self, spectator):
        if spectator in self.spectators:
            return

        # Send viewer the current board layout.
        self.spectators.append(spectator)

        spectator.game = self
        spectator.Joined()

    def DropSpectator(self, spectator):
        if spectator in self.spectators:
            self.spectators.remove(spectator)

    def ChangeTurn(self):
        # Change turn.
        self.currentPlayer.Wait()
        if self.currentPlayer == self.players[0]:
            self.currentPlayer = self.players[1]
        else:
            self.currentPlayer = self.players[0]

    def RecordMove(self, move):
        hFile = open('game_record.txt', 'a')
        hFile.write(json.dumps(move))
        hFile.write('\r')
        hFile.close()

    #def OnMove(self, src, dest):
    def OnMove(self, move):
        from time import sleep
        sleep(2)

        self.RecordMove(move)

        # Update other player about the move.
        self.currentPlayer.opponent.OpponentMove(move)

        # Update spectators about the move.
        for spectator in self.spectators:
            spectator.PlayerMove(move)

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
                # Let spectators know about this new queen.
                for spectator in self.spectators:
                    spectator.Queen(dest)
        
        self.ChangeTurn()
        self.GameLoop()

    def GameLoop(self):

        # Do we have two players in the game?
        if len(self.players) != 2:
            return

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
