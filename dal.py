import sqlite3
import json

class DAL:
    def __init__(self, database):

        import os.path
        bShouldCreateTable = os.path.isfile(database)

        self.connection = sqlite3.connect(database)
        self.cur = self.connection.cursor()

        if(bShouldCreateTable == False):
            self.CreateMovesTable()

    def CreateMovesTable(self):
        sql = """CREATE TABLE `moves` (
                    `look_ahead`	INTEGER NOT NULL,
                    `strategy`	INTEGER NOT NULL,
                    `board`	TEXT NOT NULL,
                    `move`	TEXT NOT NULL,
                    PRIMARY KEY(look_ahead, strategy, board));"""

        self.cur.execute(sql)
        self.connection.commit()

    def InsertMove(self, look_ahead, strategy, board, move):
        # Serialize and stringify.
        board_str = json.dumps(board.Serialize())

        query = "insert into moves (look_ahead, strategy, board, move) values (?, ?, ?, ?)"
        self.cur.execute(query, (look_ahead, strategy, board_str, json.dumps(move)))
        self.connection.commit()

    def GetMove(self, look_ahead, strategy, board):

        # Serialize and stringify.
        board_str = json.dumps(board.Serialize())

        self.cur.execute("select move from moves where look_ahead = ? and strategy = ? and board = ?",
            (look_ahead, strategy, board_str))

        moves = self.cur.fetchone()

        # Couldn't find move in DB.
        if moves == None:
            return None

        else:
            ret = []
            moves = moves[0]
            moves = json.loads(moves)
            import point

            # Expecting an array of moves.
            for move in moves:
                _from = point.Point(move['from'][0], move['from'][1])
                _to = point.Point(move['to'][0], move['to'][1])
                ret.append({'from': _from, 'to' : _to, 'eat' : move['eat']})
            return ret

    def ClearMovesTable(self):
        sql = "delete from moves"
        self.cur.execute(sql)
        self.connection.commit()