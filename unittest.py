import board
import point
import config
import Tree
import checkers

def TestInitializedBoard():
	game_board = board.Board()

	whites = game_board.checkers[config.WHITE]
	blacks = game_board.checkers[config.BLACK]

	assert ((len(whites) == 12) and (len(blacks) == 12))

	# Make sure every piece is in place.
	for x in range(config.BOARD_HEIGHT):
		for y in range(config.BOARD_WIDTH):
			if(x < 3): # Black pieces.
				if(((x + y) % 2) == 0):
					# There should be a white checker here.
					assert (game_board[x][y] != None)
					black_piece = game_board[x][y]
					assert (black_piece.Color == config.WHITE)
				else:
					# spot should be empty!
					assert (game_board[x][y] == None)

			elif(x >= 3) and (x <= 4):
				# spot should be empty!
				assert (game_board[x][y] == None)

			else:
				if(((x + y) % 2) == 0):
					# There should be a black checker here.
					assert (game_board[x][y] != None)
					white_piece = game_board[x][y]
					assert (white_piece.Color == config.BLACK)
				else:
					# spot should be empty!
					assert (game_board[x][y] == None)
	return True

def TestSimpleMove():
	game_board = board.Board()

	originalWhites = list(game_board.checkers[config.WHITE])
	originalBlacks = list(game_board.checkers[config.BLACK])

	# No checker at this position
	game_board.Move(point.Point(0,0), point.Point(0,0))
	assert(originalWhites == game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])

	# No checker at this position
	game_board.Move(point.Point(0,0), point.Point(1,1))
	assert(originalWhites == game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])

	# No checker at this position
	game_board.Move(point.Point(1,1), point.Point(0,0))
	assert(originalWhites == game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])

	# Stay put
	game_board.Move(point.Point(0,1), point.Point(0,1))
	assert(originalWhites == game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])

	# Out of boundries.
	game_board.Move(point.Point(0,1), point.Point(1,-1))
	assert(originalWhites == game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])

	# Out of boundries.
	game_board.Move(point.Point(0,1), point.Point(-1,-1))
	assert(originalWhites == game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])

	# Stright line move.
	game_board.Move(point.Point(0,1), point.Point(1, 1))
	assert(originalWhites == game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])

	# Stright line move.
	game_board.Move(point.Point(0,1), point.Point(0, 2))
	assert(originalWhites == game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])

	# Moving to not an empty spot.
	game_board.Move(point.Point(0,1), point.Point(1, 2))
	assert(originalWhites == game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])

	# Try removing a piece which doesn't exsists.
	game_board.RemovePiece(point.Point(0,1))
	assert(originalWhites == game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])

	# Try removing a piece which doesn't exsists.
	game_board.RemovePiece(point.Point(-1,0))
	assert(originalWhites == game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])
	
	# Remove a piece from the board.
	game_board.RemovePiece(point.Point(1,1))
	assert(originalWhites != game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])
	assert(len(game_board.checkers[config.WHITE]) == 11)	

	# Remove a piece from the board.
	game_board.RemovePiece(point.Point(7,1))
	assert(originalWhites != game_board.checkers[config.WHITE])
	assert(originalBlacks != game_board.checkers[config.BLACK])
	assert(len(game_board.checkers[config.BLACK]) == 11)

	# Set originals.
	originalWhites = game_board.checkers[config.WHITE]
	originalBlacks = game_board.checkers[config.BLACK]
	
	# Can't move backwards.
	game_board.Move(point.Point(2, 2), point.Point(1, 1))
	assert(originalWhites == game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])

	# Can't move backwards.
	game_board.Move(point.Point(2, 2), point.Point(1, 1))
	assert(originalWhites == game_board.checkers[config.WHITE])
	assert(originalBlacks == game_board.checkers[config.BLACK])

	game_board.Move(point.Point(0, 0), point.Point(1, 1))
	assert(game_board[0][0] == None)
	assert(game_board[1][1] != None)
	
	piece = originalWhites[9] # (2,4)
	assert((piece.Position.x == 2) and (piece.Position.y == 4))
	game_board.Move(piece.Position, point.Point(3, 5))
	assert((piece.Position.x == 3) and (piece.Position.y == 5))
	assert((game_board[2][4] == None) and (game_board[3][5] != None))

	return True

def TestEatMoves():
	game_board = board.Board()

	whites = game_board.checkers[config.WHITE]
	blacks = game_board.checkers[config.BLACK]

	game_board.Move(point.Point(2,2), point.Point(3,1))
	game_board.Move(point.Point(5,1), point.Point(4,0))
	game_board.Move(point.Point(4,0), point.Point(2,2))
	assert(len(blacks) == 12)
	assert(len(whites) == 11)
	assert(game_board[3][1] == None)
	assert(game_board[4][0] == None)
	assert(game_board[2][2] != None)


	game_board.Move(point.Point(2,6), point.Point(3,7))
	game_board.Move(point.Point(5,5), point.Point(4,6))
	game_board.Move(point.Point(3,7), point.Point(5,5))
	assert(len(blacks) == 11)
	assert(len(whites) == 11)
	assert(game_board[4][6] == None)
	assert(game_board[3][7] == None)
	assert(game_board[5][5] != None)

	return True

def TestUndoMove():
	game_board = board.Board()

	whites = game_board.checkers[config.WHITE]
	blacks = game_board.checkers[config.BLACK]

	#Test Undo simple move.
	game_board.Move(point.Point(2,0), point.Point(3,1))

	assert(game_board[2][0] == None)
	assert(game_board[3][1] != None)

	game_board.UndoMove(point.Point(2,0), point.Point(3,1))

	assert(game_board[2][0] != None)
	assert(game_board[3][1] == None)

	# Test Undo for 'eat' move.
	game_board.Move(point.Point(2,6), point.Point(3,7))
	game_board.Move(point.Point(5,5), point.Point(4,6))
	game_board.Move(point.Point(3,7), point.Point(5,5))
	assert(len(blacks) == 11)
	assert(game_board[4][6] == None)
	assert(game_board[3][7] == None)
	assert(game_board[5][5] != None)

	game_board.UndoMove(point.Point(3,7), point.Point(5,5))
	assert(len(blacks) == 12)
	assert(game_board[4][6] != None)
	assert(game_board[3][7] != None)
	assert(game_board[5][5] == None)
	assert(game_board[4][6].Color == config.BLACK)
	assert(game_board[3][7].Color == config.WHITE)
	
	return True

def TestPossibleMoves():
	game_board = board.Board()

	whites = game_board.checkers[config.WHITE]
	blacks = game_board.checkers[config.BLACK]

	stuckPiece = game_board[0][0]
	moves = stuckPiece.PossibleMoves()
	assert(len(moves) == 0)

	stuckPiece = game_board[1][7]
	moves = stuckPiece.PossibleMoves()
	assert(len(moves) == 0)

	oneMovePiece = game_board[2][0]
	moves = oneMovePiece.PossibleMoves()
	assert(len(moves) == 1)
	assert(moves[0][0]['to'].x == 3 and moves[0][0]['to'].y == 1 and moves[0][0]['eat'] == False)

	twoMovePiece = game_board[2][2]
	moves = twoMovePiece.PossibleMoves()
	assert(len(moves) == 2)
	assert(moves[0][0]['to'].x == 3 and moves[0][0]['to'].y == 3 and moves[0][0]['eat'] == False)
	assert(moves[1][0]['to'].x == 3 and moves[1][0]['to'].y == 1 and moves[1][0]['eat'] == False)

	toEatPiece = game_board[5][7]
	eater = game_board[2][4]

	game_board.Move(toEatPiece.Position, point.Point(4,6))
	game_board.Move(toEatPiece.Position, point.Point(3,5))
	assert(toEatPiece.Position.x == 3 and toEatPiece.Position.y == 5)
	
	moves = eater.PossibleMoves()
	assert(len(moves) == 1)
	assert(moves[0][0]['to'].x == 4 and moves[0][0]['to'].y == 6 and moves[0][0]['eat'] == True)

	#Eat backwards.
	game_board = board.Board()
	whites = game_board.checkers[config.WHITE]
	blacks = game_board.checkers[config.BLACK]

	toEatPiece = game_board[5][1]
	backwardsToEatPiece = game_board[5][3]
	eater = game_board[2][2]

	game_board.Move(toEatPiece.Position, point.Point(4, 2))

	game_board.Move(backwardsToEatPiece.Position, point.Point(4, 4))

	game_board.Move(eater.Position, point.Point(3, 1))

	moves = eater.PossibleMoves()
	assert(len(moves) == 1)
	assert(len(moves[0]) == 2)
	assert(moves[0][0]['from'].x == 3 and moves[0][0]['from'].y == 1 and moves[0][0]['eat'] == True)
	assert(moves[0][0]['to'].x == 5 and moves[0][0]['to'].y == 3 and moves[0][0]['eat'] == True)
	assert(moves[0][1]['from'].x == 5 and moves[0][1]['from'].y == 3 and moves[0][1]['eat'] == True)
	assert(moves[0][1]['to'].x == 3 and moves[0][1]['to'].y == 5 and moves[0][1]['eat'] == True)

	game_board.MultipleMove(moves[0])
	assert(len(blacks) == 10)
	
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

	assert(node9.Value == 9)
	assert(node12.IsLeaf)
	assert(node8.IsLeaf)
	assert(node4.IsLeaf)
	assert(len(node2.Nodes) == 3)
	assert(len(node10.Nodes) == 0)
	assert(node3.Nodes[0] == node10)
	assert(node3.Nodes[1] == node11)
	assert(node3.Nodes[2] == node12)
	assert(node11.Parent == node3)
	assert(node7.Parent == node2)
	assert(node4.Parent == node1)
	assert(node1.Parent == root)
	assert(root.Parent == None)

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

if(TestInitializedBoard() != True):
	print "TestInitializedBoard failed"

if(TestSimpleMove() != True):
	print "TestSimpleMove failed"

if(TestEatMoves() != True):
	print "TestSimpleMove failed"

if(TestUndoMove() != True):
	print "TestUndoMove failed"

if(TestPossibleMoves() != True):
	print "TestPossibleMoves failed"

if(TestTree() != True):
	print"TestTree failed"

#if(TestLookAhead() != True):
	#print "TestLookAhead failed"

print "test suite completed"