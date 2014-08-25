import checkers
import config
import random
import dal

class predicted_player(checkers.Player):
    def __init__(self, _color, game, level, strategy):
        #Player.__init__(self, _color, _checkers, _game_board, game)
        checkers.Player.__init__(self, _color, game)
        self.movesdb = dal.DAL(config.DB_NAME) # todo consider changing dal method to static.
        self.level = level
        self.strategy = strategy

    def __del__(self):
        print("ComPlayer destructor")

    def JoinedGame(self):
        pass

    def Wait(self):
        pass

    def Play(self, specificPiece = None, eat_mode = False):

        # Step 1. Incase we've got a piece which is able to 'eat' we must use it.
        # Determine if there's such piece.
        bMustEat = True if eat_mode or self.CanEat() else False

        # construct a list of checkers to test, each checker will be identified by it's position
        # this is because our list might change over time, and we'll might calculate a result
        # for the same piece multiple times, misleading ourselves.
        checkersPositionsList = []
        if(specificPiece != None):
            checkersPositionsList.append(specificPiece.Position)
        else:
            for checker in self.checkers:
                if (len(checker.PossibleMoves()) == 0):  # Piece can't move.
                    continue

                if(checker.CanEat() != bMustEat): # We must 'eat' and this piece can't.
                    continue

                checkersPositionsList.append(checker.Position)

        # counts number of possible moves.
        moves_counter = 0

        for checkerPos in checkersPositionsList:
            checker = self.game_board[checkerPos.x][checkerPos.y]
            for move in checker.PossibleMoves(eat_mode):
                moves_counter += 1
                performedMoves = self.game_board.MultipleMove(move)
                # check to see if this new board state already exists in the database?
                if self.movesdb.GetMove(self.level, self.strategy, self.game_board) is None:
                    # Nope, we've never seen this state before, play.
                    self.FireMove(move)
                    return

                # No luck restore to previous state and keep searching.
                self.game_board.MultipleUndoMove(performedMoves)

        random_move_index = random.randrange(0, moves_counter)

        # if we're here this means all possible moves have already been cached.
        # in that case pick a random move.
        for checkerPos in checkersPositionsList:
            checker = self.game_board[checkerPos.x][checkerPos.y]
            for move in checker.PossibleMoves(eat_mode):
                moves_counter -= 1
                if moves_counter == random_move_index:
                    # Perform move.
                    self.game_board.MultipleMove(move)
                    self.FireMove(move)

        raise Exception("We're not supposed to be here, Something went wrong with our counting.")


    def OpponentLeft(self):
        self.opponent = None
        # Drop your self from the game.
        self.game.DropPlayer(self)

def main():

    for i in range(100):
        game = checkers.Game()
        comp = checkers.CompPlayer(config.WHITE, game, config.INTERMEDIATE, config.OFFENSIVE)
        predicted = predicted_player(config.BLACK, game, config.INTERMEDIATE, config.OFFENSIVE)

        game.JoinPlayer(comp)
        game.JoinPlayer(predicted)

if __name__ == '__main__':
    main()