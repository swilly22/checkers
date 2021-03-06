import board
import point
import config
import Tree
import checkers
from computer_player import CompPlayer
import checker
import dal


def TestInitializedBoard():
    game_board = board.Board()

    whites = game_board.checkers[config.WHITE]
    blacks = game_board.checkers[config.BLACK]

    assert ((len(whites) == 12) and (len(blacks) == 12))

    # Make sure every piece is in place.
    for x in range(config.BOARD_HEIGHT):
        for y in range(config.BOARD_WIDTH):
            if (x < 3):  # Black pieces.
                if (((x + y) % 2) == 0):
                    # There should be a white checker here.
                    assert (game_board[x][y] != None)
                    black_piece = game_board[x][y]
                    assert (black_piece.Color == config.WHITE)
                else:
                    # spot should be empty!
                    assert (game_board[x][y] == None)

            elif (x >= 3) and (x <= 4):
                # spot should be empty!
                assert (game_board[x][y] == None)

            else:
                if (((x + y) % 2) == 0):
                    # There should be a black checker here.
                    assert (game_board[x][y] != None)
                    black_piece = game_board[x][y]
                    assert (black_piece.Color == config.BLACK)
                else:
                    # spot should be empty!
                    assert (game_board[x][y] == None)
    return True


def TestSimpleMove():
    game_board = board.Board()

    originalWhites = list(game_board.checkers[config.WHITE])
    originalBlacks = list(game_board.checkers[config.BLACK])

    # No checker at this position
    game_board.Move(point.Point(0, 1), point.Point(0, 0))
    assert (originalWhites == game_board.checkers[config.WHITE])
    assert (originalBlacks == game_board.checkers[config.BLACK])

    # Stay put
    game_board.Move(point.Point(0, 0), point.Point(0, 0))
    assert (originalWhites == game_board.checkers[config.WHITE])
    assert (originalBlacks == game_board.checkers[config.BLACK])

    # Out of boundaries.
    game_board.Move(point.Point(0, 0), point.Point(1, -1))
    assert (originalWhites == game_board.checkers[config.WHITE])
    assert (originalBlacks == game_board.checkers[config.BLACK])

    # Straight line move.
    game_board.Move(point.Point(2, 0), point.Point(3, 0))
    assert (originalWhites == game_board.checkers[config.WHITE])
    assert (originalBlacks == game_board.checkers[config.BLACK])

    # Straight line move.
    game_board.Move(point.Point(2, 0), point.Point(2, 1))
    assert (originalWhites == game_board.checkers[config.WHITE])
    assert (originalBlacks == game_board.checkers[config.BLACK])

    # Moving to an occupied spot.
    game_board.Move(point.Point(0, 0), point.Point(1, 1))
    assert (originalWhites == game_board.checkers[config.WHITE])
    assert (originalBlacks == game_board.checkers[config.BLACK])

    # Try removing a piece which doesn't exists.
    game_board.RemovePiece(point.Point(0, 1))
    assert (originalWhites == game_board.checkers[config.WHITE])
    assert (originalBlacks == game_board.checkers[config.BLACK])

    # Try removing a piece which doesn't exists.
    game_board.RemovePiece(point.Point(-1, 0))
    assert (originalWhites == game_board.checkers[config.WHITE])
    assert (originalBlacks == game_board.checkers[config.BLACK])

    # Remove a piece from the board.
    game_board.RemovePiece(point.Point(1, 1))
    assert (originalWhites != game_board.checkers[config.WHITE])
    assert (originalBlacks == game_board.checkers[config.BLACK])
    assert (len(game_board.checkers[config.WHITE]) == 11)
    assert (len(game_board.checkers[config.BLACK]) == 12)

    # Remove a piece from the board.
    game_board.RemovePiece(point.Point(7, 1))
    assert (originalWhites != game_board.checkers[config.WHITE])
    assert (originalBlacks != game_board.checkers[config.BLACK])
    assert (len(game_board.checkers[config.BLACK]) == 11)

    # Set originals.
    originalWhites = game_board.checkers[config.WHITE]
    originalBlacks = game_board.checkers[config.BLACK]

    # Can't move backwards.
    game_board.Move(point.Point(2, 2), point.Point(1, 1))
    assert (originalWhites == game_board.checkers[config.WHITE])
    assert (originalBlacks == game_board.checkers[config.BLACK])

    # Can't move backwards.
    game_board.RemovePiece(point.Point(6, 2))
    game_board.Move(point.Point(5, 1), point.Point(6, 2))
    assert (originalWhites == game_board.checkers[config.WHITE])
    assert (originalBlacks == game_board.checkers[config.BLACK])

    game_board.Move(point.Point(0, 0), point.Point(1, 1))
    assert (game_board[0][0] == None)
    assert (game_board[1][1] != None)

    piece = originalWhites[9]  # (2,4)
    assert ((piece.Position.x == 2) and (piece.Position.y == 4))
    game_board.Move(piece.Position, point.Point(3, 5))
    assert ((piece.Position.x == 3) and (piece.Position.y == 5))
    assert ((game_board[2][4] == None) and (game_board[3][5] != None))

    return True


def TestEatMoves():
    game_board = board.Board()

    whites = game_board.checkers[config.WHITE]
    blacks = game_board.checkers[config.BLACK]

    game_board.Move(point.Point(2, 2), point.Point(3, 1))
    game_board.Move(point.Point(5, 1), point.Point(4, 0))
    game_board.Move(point.Point(4, 0), point.Point(2, 2))
    assert (len(blacks) == 12)
    assert (len(whites) == 11)
    assert (game_board[3][1] == None)
    assert (game_board[4][0] == None)
    assert (game_board[2][2] != None)

    game_board.Move(point.Point(2, 6), point.Point(3, 7))
    game_board.Move(point.Point(5, 5), point.Point(4, 6))
    game_board.Move(point.Point(3, 7), point.Point(5, 5))
    assert (len(blacks) == 11)
    assert (len(whites) == 11)
    assert (game_board[4][6] == None)
    assert (game_board[3][7] == None)
    assert (game_board[5][5] != None)

    return True


def TestUndoMove():
    game_board = board.Board()

    whites = game_board.checkers[config.WHITE]
    blacks = game_board.checkers[config.BLACK]

    # Test Undo simple move.
    move = game_board.Move(point.Point(2, 0), point.Point(3, 1))

    assert (game_board[2][0] == None)
    assert (game_board[3][1] != None)

    game_board.UndoMove(move)

    assert (game_board[2][0] != None)
    assert (game_board[3][1] == None)

    # Test Undo for 'eat' move.
    game_board.Move(point.Point(2, 6), point.Point(3, 7))
    game_board.Move(point.Point(5, 5), point.Point(4, 6))
    move = game_board.Move(point.Point(3, 7), point.Point(5, 5))
    assert (len(blacks) == 11)
    assert (game_board[4][6] == None)
    assert (game_board[3][7] == None)
    assert (game_board[5][5] != None)

    game_board.UndoMove(move)
    print(len(blacks))
    assert (len(blacks) == 12)
    assert (game_board[4][6] != None)
    assert (game_board[3][7] != None)
    assert (game_board[5][5] == None)
    assert (game_board[4][6].Color == config.BLACK)
    assert (game_board[3][7].Color == config.WHITE)

    # Test Undo Queen eats 3 checkers.
    game_board.ClearBoard()
    queen = checker.Queen(config.WHITE, point.Point(0,0), game_board)
    checker1 = checker.Checker(config.BLACK, point.Point(4,4), game_board)
    checker2 = checker.Checker(config.BLACK, point.Point(4,6), game_board)
    checker3 = checker.Checker(config.BLACK, point.Point(2,6), game_board)

    game_board.AddPiece(queen, queen.Position)
    game_board.AddPiece(checker1, checker1.Position)
    game_board.AddPiece(checker2, checker2.Position)
    game_board.AddPiece(checker3, checker3.Position)

    moves = queen.PossibleMoves()
    play = game_board.MultipleMove(moves[0])

    assert(len(game_board.checkers[config.BLACK]) == 0)

    game_board.MultipleUndoMove(play)
    assert(len(game_board.checkers[config.BLACK]) == 3)

    assert (game_board[4][4] != None)
    assert (game_board[4][4].Color == config.BLACK)
    assert (game_board[4][4].Type == config.CHECKER)

    assert (game_board[4][6] != None)
    assert (game_board[4][6].Color == config.BLACK)
    assert (game_board[4][6].Type == config.CHECKER)

    assert (game_board[2][6] != None)
    assert (game_board[2][6].Color == config.BLACK)
    assert (game_board[2][6].Type == config.CHECKER)


    # Test Undo Checker eats 2 queens.
    game_board.ClearBoard()
    piece = checker.Checker(config.WHITE, point.Point(3,3), game_board)
    queen1 = checker.Queen(config.BLACK, point.Point(4,4), game_board)
    queen2 = checker.Queen(config.BLACK, point.Point(4,6), game_board)

    game_board.AddPiece(piece, piece.Position)
    game_board.AddPiece(queen1, queen1.Position)
    game_board.AddPiece(queen2, queen2.Position)

    moves = piece.PossibleMoves()
    play = game_board.MultipleMove(moves[0])

    assert(len(game_board.checkers[config.BLACK]) == 0)

    game_board.MultipleUndoMove(play)
    assert(len(game_board.checkers[config.BLACK]) == 2)

    assert (game_board[4][4] != None)
    assert (game_board[4][4].Color == config.BLACK)
    assert (game_board[4][4].Type == config.QUEEN)

    assert (game_board[4][6] != None)
    assert (game_board[4][6].Color == config.BLACK)
    assert (game_board[4][6].Type == config.QUEEN)

    return True


def TestPossibleMoves():
    game_board = board.Board()

    blacks = game_board.checkers[config.BLACK]

    stuckPiece = game_board[0][0]
    moves = stuckPiece.PossibleMoves()
    assert (len(moves) == 0)

    stuckPiece = game_board[1][7]
    moves = stuckPiece.PossibleMoves()
    assert (len(moves) == 0)

    oneMovePiece = game_board[2][0]
    moves = oneMovePiece.PossibleMoves()
    assert (len(moves) == 1)
    assert (moves[0][0]['to'].x == 3 and moves[0][0]['to'].y == 1 and moves[0][0]['eat'] == False)

    twoMovePiece = game_board[2][2]
    moves = twoMovePiece.PossibleMoves()
    assert (len(moves) == 2)
    assert (moves[0][0]['to'].x == 3 and moves[0][0]['to'].y == 1 and moves[0][0]['eat'] == False)
    assert (moves[1][0]['to'].x == 3 and moves[1][0]['to'].y == 3 and moves[1][0]['eat'] == False)

    game_board.ClearBoard()
    eater = checker.Checker(config.WHITE, point.Point(2, 4), game_board)
    eaten = checker.Checker(config.BLACK, point.Point(3, 3), game_board)
    game_board.AddPiece(eater, eater.Position)
    game_board.AddPiece(eaten, eaten.Position)

    moves = eater.PossibleMoves()
    assert (len(moves) == 1)
    assert (moves[0][0]['to'].x == 4 and moves[0][0]['to'].y == 2 and moves[0][0]['eat'] == True)

    # Eat backwards.
    game_board.ClearBoard()
    eater = checker.Checker(config.WHITE, point.Point(2, 2), game_board)
    eaten = checker.Checker(config.BLACK, point.Point(3, 3), game_board)
    eatenBack = checker.Checker(config.BLACK, point.Point(3, 5), game_board)
    
    game_board.AddPiece(eater, eater.Position)
    game_board.AddPiece(eaten, eaten.Position)
    game_board.AddPiece(eatenBack, eatenBack.Position)

    moves = eater.PossibleMoves()
    assert (len(moves) == 1)
    assert (len(moves[0]) == 2)
    assert (moves[0][0]['from'].x == 2 and moves[0][0]['from'].y == 2 and moves[0][0]['eat'] == True)
    assert (moves[0][0]['to'].x == 4 and moves[0][0]['to'].y == 4 and moves[0][0]['eat'] == True)
    assert (moves[0][1]['from'].x == 4 and moves[0][1]['from'].y == 4 and moves[0][1]['eat'] == True)
    assert (moves[0][1]['to'].x == 2 and moves[0][1]['to'].y == 6 and moves[0][1]['eat'] == True)

    game_board.MultipleMove(moves[0])
    assert (len(blacks) == 0)

    # four eats.
    game_board.ClearBoard()
    eater = checker.Checker(config.WHITE, point.Point(2,0), game_board)
    a = checker.Checker(config.BLACK, point.Point(3, 1), game_board)
    b = checker.Checker(config.BLACK, point.Point(3, 3), game_board)
    c = checker.Checker(config.BLACK, point.Point(3, 5), game_board)
    d = checker.Checker(config.BLACK, point.Point(5, 5), game_board)
    
    game_board.AddPiece(eater, eater.Position)
    game_board.AddPiece(a, a.Position)
    game_board.AddPiece(b, b.Position)
    game_board.AddPiece(c, c.Position)
    game_board.AddPiece(d, d.Position)

    assert (len(blacks) == 4)

    moves = eater.PossibleMoves()
    assert (len(moves) == 1)
    assert (len(moves[0]) == 4)
    assert (moves[0][0]['from'].x == 2 and moves[0][0]['from'].y == 0 and moves[0][0]['eat'] == True)
    assert (moves[0][0]['to'].x == 4 and moves[0][0]['to'].y == 2 and moves[0][0]['eat'] == True)

    assert (moves[0][1]['from'].x == 4 and moves[0][1]['from'].y == 2 and moves[0][1]['eat'] == True)
    assert (moves[0][1]['to'].x == 2 and moves[0][1]['to'].y == 4 and moves[0][1]['eat'] == True)

    assert (moves[0][2]['from'].x == 2 and moves[0][2]['from'].y == 4 and moves[0][0]['eat'] == True)
    assert (moves[0][2]['to'].x == 4 and moves[0][2]['to'].y == 6 and moves[0][0]['eat'] == True)
    
    assert (moves[0][3]['from'].x == 4 and moves[0][3]['from'].y == 6 and moves[0][1]['eat'] == True)
    assert (moves[0][3]['to'].x == 6 and moves[0][3]['to'].y == 4 and moves[0][1]['eat'] == True)

    game_board.MultipleMove(moves[0])
    assert (len(blacks) == 0)

    # four eats.
    game_board.ClearBoard()
    eater = checker.Checker(config.WHITE, point.Point(1,1), game_board)
    a = checker.Checker(config.BLACK, point.Point(2, 2), game_board)
    b = checker.Checker(config.BLACK, point.Point(2, 4), game_board)
    c = checker.Checker(config.BLACK, point.Point(2, 6), game_board)
    d = checker.Checker(config.BLACK, point.Point(4, 6), game_board)
    
    game_board.AddPiece(eater, eater.Position)
    game_board.AddPiece(a, a.Position)
    game_board.AddPiece(b, b.Position)
    game_board.AddPiece(c, c.Position)
    game_board.AddPiece(d, d.Position)

    assert (len(blacks) == 4)

    moves = eater.PossibleMoves()
    assert (len(moves) == 1)
    assert (len(moves[0]) == 4)
    assert (moves[0][0]['from'].x == 1 and moves[0][0]['from'].y == 1 and moves[0][0]['eat'] == True)
    assert (moves[0][0]['to'].x == 3 and moves[0][0]['to'].y == 3 and moves[0][0]['eat'] == True)

    assert (moves[0][1]['from'].x == 3 and moves[0][1]['from'].y == 3 and moves[0][1]['eat'] == True)
    assert (moves[0][1]['to'].x == 1 and moves[0][1]['to'].y == 5 and moves[0][1]['eat'] == True)

    assert (moves[0][2]['from'].x == 1 and moves[0][2]['from'].y == 5 and moves[0][0]['eat'] == True)
    assert (moves[0][2]['to'].x == 3 and moves[0][2]['to'].y == 7 and moves[0][0]['eat'] == True)
    
    assert (moves[0][3]['from'].x == 3 and moves[0][3]['from'].y == 7 and moves[0][1]['eat'] == True)
    assert (moves[0][3]['to'].x == 5 and moves[0][3]['to'].y == 5 and moves[0][1]['eat'] == True)

    game_board.MultipleMove(moves[0])
    assert (len(blacks) == 0)

    # Incase a piece turns queen it shouldn't keep eating (when possible).
    game_board.ClearBoard()
    eater = checker.Checker(config.WHITE, point.Point(5, 3), game_board)
    a = checker.Checker(config.BLACK, point.Point(6, 4), game_board)
    b = checker.Checker(config.BLACK, point.Point(6, 6), game_board)

    game_board.AddPiece(eater, eater.Position)
    game_board.AddPiece(a, a.Position)
    game_board.AddPiece(b, b.Position)

    moves = eater.PossibleMoves()
    assert (len (moves) == 1)

    play = moves[0]
    assert (len(play) == 1)

    assert (play[0]['from'].x == 5 and play[0]['from'].y == 3 and play[0]['eat'] == True)
    assert (play[0]['to'].x == 7 and play[0]['to'].y == 5 and play[0]['eat'] == True)

    return True


def TestTree():
    # Construct 3 level Tree.
    root = Tree.Tree(0)
    node1 = root.AddNode(1)
    node2 = root.AddNode(2)
    node3 = root.AddNode(3)

    node4 = node1.AddNode(4)
    node5 = node1.AddNode(5)
    node6 = node1.AddNode(6)

    node7 = node2.AddNode(7)
    node8 = node2.AddNode(8)
    node9 = node2.AddNode(9)

    node10 = node3.AddNode(10)
    node11 = node3.AddNode(11)
    node12 = node3.AddNode(12)

    assert (node9.Value == 9)
    assert (node12.IsLeaf)
    assert (node8.IsLeaf)
    assert (node4.IsLeaf)
    assert (len(node2.Nodes) == 3)
    assert (len(node10.Nodes) == 0)
    assert (node3.Nodes[0] == node10)
    assert (node3.Nodes[1] == node11)
    assert (node3.Nodes[2] == node12)
    assert (node11.Parent == node3)
    assert (node7.Parent == node2)
    assert (node4.Parent == node1)
    assert (node1.Parent == root)
    assert (root.Parent == None)

    def Print(str):
        print str

    Tree.DFS(root, Print)
    return True


def TestLookAhead():
    game = checkers.Game()
    game_board = game.board
    player1 = game.player1
    player2 = game.player2

    player1.Play()

    return True


def TestQueen():
    game_board = board.Board()
    whites = game_board.checkers[config.WHITE]
    blacks = game_board.checkers[config.BLACK]

    # Remove all pieces from board.
    game_board.ClearBoard()

    queen = checker.Queen(config.WHITE, point.Point(7, 7), game_board)
    assert (game_board.AddPiece(queen, queen.Position) == True)
    assert (len(whites) == 1)

    moves = queen.PossibleMoves()
    assert (len(moves) == config.BOARD_HEIGHT - 1)

    x = config.BOARD_HEIGHT - 2
    y = config.BOARD_WIDTH - 2
    for move in moves:
        assert (move[0]['from'] == queen.Position)
        assert (move[0]['to'].x == x and move[0]['to'].y == y)
        x -= 1
        y -= 1

    game_board.Move(queen.Position, point.Point(3, 3))
    assert (queen.Position.x == 3 and queen.Position.y == 3)
    moves = queen.PossibleMoves()
    assert (len(moves) == 13)

    # Queen eat
    game_board.ClearBoard()
    queen = checker.Queen(config.WHITE, point.Point(0, 0), game_board)
    a = checker.Checker(config.BLACK, point.Point(3, 3), game_board)
    b = checker.Checker(config.BLACK, point.Point(5, 3), game_board)
    c = checker.Checker(config.BLACK, point.Point(5, 1), game_board)
    
    game_board.AddPiece(queen, queen.Position)
    game_board.AddPiece(a, a.Position)
    game_board.AddPiece(b, b.Position)
    game_board.AddPiece(c, c.Position)

    moves = queen.PossibleMoves()

    assert (queen.Position.x == 0 and queen.Position.y == 0)
    assert(len(moves) == 1)
    assert(len(moves[0]) == 3)
    assert (moves[0][0]['from'].x == 0 and moves[0][0]['from'].y == 0 and moves[0][0]['eat'] == True)
    assert (moves[0][0]['to'].x == 4 and moves[0][0]['to'].y == 4 and moves[0][0]['eat'] == True)

    assert (moves[0][1]['from'].x == 4 and moves[0][1]['from'].y == 4 and moves[0][1]['eat'] == True)
    assert (moves[0][1]['to'].x == 6 and moves[0][1]['to'].y == 2 and moves[0][1]['eat'] == True)

    assert (moves[0][2]['from'].x == 6 and moves[0][2]['from'].y == 2 and moves[0][1]['eat'] == True)
    assert (moves[0][2]['to'].x == 4 and moves[0][2]['to'].y == 0 and moves[0][1]['eat'] == True)

    game_board.MultipleMove(moves[0])
    assert(len(blacks) == 0)

    # Another test, make sure we don't jump over friends.
    game_board.ClearBoard()
    queen = checker.Queen(config.BLACK, point.Point(0, 0), game_board)
    friend = checker.Checker(config.BLACK, point.Point(3, 3), game_board)
    game_board.AddPiece(queen, queen.Position)
    game_board.AddPiece(friend, friend.Position)

    moves = queen.PossibleMoves()
    assert (len(moves) == 2)

    # Test queen doesn't eat more than one piece in each move.
    game_board.ClearBoard()
    queen = checker.Queen(config.WHITE, point.Point(7, 5), game_board)
    opponent1 = checker.Checker(config.BLACK, point.Point(6, 4), game_board)
    opponent2 = checker.Checker(config.BLACK, point.Point(5, 3), game_board)
    friend = checker.Checker(config.WHITE, point.Point(6, 6), game_board)

    game_board.AddPiece(queen, queen.Position)
    game_board.AddPiece(opponent1, opponent1.Position)
    game_board.AddPiece(opponent2, opponent2.Position)
    game_board.AddPiece(friend, friend.Position)

    moves = queen.PossibleMoves()
    assert (len(moves) == 0)
    return True


def TestClearBoard():
    game_board = board.Board()
    whites = game_board.checkers[config.WHITE]
    blacks = game_board.checkers[config.BLACK]
    game_board.ClearBoard()

    assert(len(whites) == 0)
    assert(len(blacks) == 0)

    for x in range(config.BOARD_HEIGHT):
        for y in range(config.BOARD_WIDTH):
            piece = game_board[x][y]
            assert (piece == None)

    return True


def TestBoardSeralization():
    game_board = board.Board()
    serialized = game_board.Serialize()
    empty = 0
    white_checker = 1
    black_checker = 2
    white_queen = 3
    black_queen = 4

    for row in range(config.BOARD_HEIGHT):
        for col in range(config.BOARD_WIDTH):
            idx = (config.BOARD_WIDTH * row) + col
            if row in range(3):
                if ((col + row) % 2) == 0:
                    assert serialized[idx] == white_checker
                else:
                    assert serialized[idx] == empty
            elif row in range(3, 5):
                assert serialized[idx] == empty
            else:
                if((col + row) % 2) == 0:
                    assert serialized[idx] == black_checker
                else:
                    assert serialized[idx] == empty

    # Test serialized with queens.
    game_board.ClearBoard()
    queenA = checker.Queen(config.BLACK, point.Point(3,3), game_board)
    queenB = checker.Queen(config.WHITE, point.Point(6,2), game_board)
    game_board.AddPiece(queenA, queenA.Position)
    game_board.AddPiece(queenB, queenB.Position)

    serialized = game_board.Serialize()

    for row in range(config.BOARD_HEIGHT):
        for col in range(config.BOARD_WIDTH):
            idx = (config.BOARD_WIDTH * row) + col
            if row == 3 and col == 3:
                assert serialized[idx] == black_queen
            elif row == 6 and col == 2:
                assert serialized[idx] == white_queen
            else:
                assert serialized[idx] == empty

    return True


def TestDal():
    dbname = "testdb.db"
    movedb = dal.DAL(dbname)

    # Clears the database.
    movedb.ClearMovesTable()

    game_board = board.Board()
    move = [{'from' : point.Point(2,2), 'to' : point.Point(3,3), 'eat':False}]

    strategy = config.OFFENSIVE
    lookahead = 4

    # Add a move to the database.
    movedb.InsertMove(lookahead, strategy, game_board, move)

    # Retrieve recently add move.
    retrieved_move = movedb.GetMove(lookahead, strategy, game_board)

    assert (len(retrieved_move) == 1)
    retrieved_move = retrieved_move[0]

    assert (retrieved_move['from'].x == move[0]['from'].x and
            retrieved_move['from'].y == move[0]['from'].y and
            retrieved_move['to'].x == move[0]['to'].x and
            retrieved_move['to'].y == move[0]['to'].y and
            retrieved_move['eat'] == False)


    # Insert a multiple move.
    move = [{'from' : point.Point(2,0), 'to' : point.Point(4,2), 'eat':True},
            {'from' : point.Point(4,2), 'to' : point.Point(6,4), 'eat':True}]

    # We clear this board to make sure our insert key is unique.
    game_board.ClearBoard()

    # Add a move to the database.
    movedb.InsertMove(lookahead, strategy, game_board, move)

    # Retrieve recently add move.
    retrieved_move = movedb.GetMove(lookahead, strategy, game_board)

    assert (len(retrieved_move) == 2)

    assert (retrieved_move[0]['from'].x == move[0]['from'].x and
            retrieved_move[0]['from'].y == move[0]['from'].y and
            retrieved_move[0]['to'].x == move[0]['to'].x and
            retrieved_move[0]['to'].y == move[0]['to'].y and
            retrieved_move[0]['eat'] == True)

    assert (retrieved_move[1]['from'].x == move[1]['from'].x and
            retrieved_move[1]['from'].y == move[1]['from'].y and
            retrieved_move[1]['to'].x == move[1]['to'].x and
            retrieved_move[1]['to'].y == move[1]['to'].y and
            retrieved_move[1]['eat'] == True)

    retrieved_move = movedb.GetMove(lookahead, config.DEFENSIVE, game_board)
    assert (retrieved_move == None)

    retrieved_move = movedb.GetMove(lookahead - 1, config.OFFENSIVE, game_board)
    assert (retrieved_move == None)

    game_board.ClearBoard()
    piece = checker.Queen(config.WHITE, point.Point(6,2), game_board)
    game_board.AddPiece(piece, piece.Position)

    retrieved_move = movedb.GetMove(lookahead, strategy, game_board)
    assert (retrieved_move == None)

    # Make sure unique id is enforced.
    try:
        movedb.InsertMove(1,1,game_board, move)
        movedb.InsertMove(1,1,game_board, move)
        assert (False)
    except Exception, e:
        # We're supposed to end up here.
        pass

    # Clear db.
    movedb.ClearMovesTable()

    import os
    os.remove(dbname)
    return True


def TestGame():
    game = checkers.Game()
    comp1 = CompPlayer(config.WHITE, game, config.INTERMEDIATE, config.OFFENSIVE)
    comp2 = CompPlayer(config.WHITE, game, config.INTERMEDIATE, config.OFFENSIVE)

    game.JoinPlayer(comp1)

    try:
        game.JoinPlayer(comp2)
        assert False

    except Exception,e:
        return True


def main():
    if (TestInitializedBoard() != True):
        print "TestInitializedBoard failed"

    if(TestClearBoard() != True):
        print "TestClearBoard failed"

    if (TestSimpleMove() != True):
        print "TestSimpleMove failed"

    if (TestEatMoves() != True):
        print "TestSimpleMove failed"

    if (TestUndoMove() != True):
        print "TestUndoMove failed"

    if (TestPossibleMoves() != True):
        print "TestPossibleMoves failed"

    if (TestTree() != True):
        print "TestTree failed"

    # #if(TestLookAhead() != True):
    # #print "TestLookAhead failed"

    if (TestQueen() != True):
        print "TestQueen failed"

    if(TestBoardSeralization() != True):
        print "TestBoardSeralization failed"

    if(TestDal() != True):
        print "TestDal failed"

    if(TestGame() != True):
        print "TestGame failed"

    print "test suite completed"

# Main
if __name__ == "__main__":
    main()