
function Server() {    
  this.address = 'ws://10.0.0.5:8080/ws';
  this.callbackQueue = [];
  this.connection = null;
  this.Send = Send;
  this.InitWSConnection = InitWSConnection;
  this.RequestPossibleMoves = RequestPossibleMoves;
  this.UpdatePiecePosition = UpdatePiecePosition;
  this.ActionHandler = ActionHandler;
}

function ActionHandler(data) {
  switch(data.action) {
    case ACTIONS.MOVE:
      for(var idx = 0; idx < data.moves.length; idx++) {
        var src = {'x' : data.moves[idx].from[0], 'y' : data.moves[idx].from[1]};
        var dest = {'x' : data.moves[idx].to[0], 'y' : data.moves[idx].to[1]};
        var bEat = data.moves[idx].eat;
        var checker = board.checkers[src.x][src.y];
        if(checker == null) {
          console.log("Error, missing piece");
          return;
        }

        board.MoveChecker(src, dest, bEat);
      }
      break;

    case ACTIONS.PLAY:
      console.log("your turn");
      bMyTurn = true;
      break;

    case ACTIONS.WAIT:
      console.log("waiting for other player to make his move.");
      bMyTurn = false;
      break;

    case ACTIONS.QUEENED:
      console.log("queened");
      var piece = board.checkers[data.position.x][data.position.y];
      if(piece == null) {
        console.log("Error, piece missing, probebly out of sync.");
        // TODO Request board.
        break;
      }
      piece.Queened();

    case ACTIONS.OPPONENT_LEFT:
        console.log("Opponent has left the game");
        // Just for fun alow player to move pieces around
        bMyTurn = true;
        break;

    default:
      console.log("Unknow action " + data.action);
      break;
  }
}

// Sends a request over websocket.
function Send(request, callback) {
  
  if(callback != null) {
    this.callbackQueue.push(callback);
  }

  this.connection.send(JSON.stringify(request));
}

function InitWSConnection() {
  this.connection = new WebSocket(this.address);
  var me = this;
  
  this.connection.onopen = function() {
   /*Send a small message to the console once the connection is established */
   console.log('Connection open!');
   game.JoinGame();
   
   //connection.send('Join');
  }

  this.connection.onclose = function() {
   console.log('Connection closed');
  }

  this.connection.onerror = function(error) {
   console.log('Error detected: ' + error);
  }

  this.connection.onmessage = function(e) {
    var server_message = e.data;
    console.log(server_message);

    var data = JSON.parse(e.data);
    if('fromServer' in data) {
      // This is a message generated by the server, no callback is set for it.
      action = data.action;
      return me.ActionHandler(data);
    }
    else {  // This is a response from the server to one of our requests.
      // Pop callback from queue.
      var callback = me.callbackQueue.shift();
      callback(data);
    }
  }
}

function RequestPossibleMoves(position, callback) {
  var request = {"action" : ACTIONS.POSSIBLE_MOVES, "piece_position" : position };
  this.Send(request, callback);
}

//function UpdatePiecePosition(from, to, callback) {
function UpdatePiecePosition(moves, callback) {
  var request = {'action' : ACTIONS.MOVE, "moves" : moves};
  this.Send(request, callback);
}