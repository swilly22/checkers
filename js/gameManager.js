function GameManager () {
  this.JoinGame = JoinGame;
  this.RequestBoard = RequestBoard;
  this.HandleRequestBoard = HandleRequestBoard;
}

function JoinGame() {
  var request = {"action" : ACTIONS.JOIN};
  server.Send(request, function(response) {
    if(response.result == true) {
      player_color = response.player_color;
      SetUpCameraViewingPosition(player_color);

      // Add light.
      SetUpLights(player_color);
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
    board.AddChecker("Checker", piecePos, PLAYER_WHITE);
  }

  for(var idx = 0; idx < data.blacks.length; idx++) {
    var piecePos = data.blacks[idx];
    var black_color = colors[2];
    board.AddChecker("Checker", piecePos, PLAYER_BLACK);
  }
}