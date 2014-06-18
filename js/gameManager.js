function GameManager () {
  this.JoinGame = JoinGame;
  this.RequestBoard = RequestBoard;
  this.HandleRequestBoard = HandleRequestBoard;
}

function JoinGame() {
  var request = {"action" : ACTIONS.JOIN};
  server.Send(request, function(response) {
    if(response.result == true) {
      this.RequestBoard();
    }
  });
}

function RequestBoard() {
  var request = {"action" : ACTIONS.INIT};
  server.Send(request, this.HandleRequestBoard);
}

function HandleRequestBoard(data) {
  for(var idx = 0; idx < data.whites.length; idx++) {
    var piecePos = data.whites[idx];
    board.AddChecker(piecePos, COLOR_WHITE);
  }

  for(var idx = 0; idx < data.blacks.length; idx++) {
    var piecePos = data.blacks[idx];
    board.AddChecker(piecePos, COLOR_BLACK);
  }
}