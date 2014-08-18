function Board() {
  
  this.MoveChecker = MoveChecker;
  this.AddChecker = AddChecker;
  this.RemoveChecker = RemoveChecker;
  this.HighLightCell = HighLightCell;
  this.WithInBounds = WithInBounds;

  this.checkers = new Array();

  for(var row = 0; row < BOARD_HEIGHT; row++) {
    this.checkers[row] = new Array();
    for(var col = 0; col < BOARD_WIDTH; col++) {
      this.checkers[row][col] = null;
    }
  }
}

function HighLightCell (position) {
  // TODO shine given position. 
}

function WithInBounds(position) {
  
  if(position.x < 0 || position.x > BOARD_HEIGHT || position.y < 0 || position.y > BOARD_WIDTH) {
    console.log("out of bounds.")
    return false;
  }

  return true;
}

function AddChecker(type, position, color) {
  if(!this.WithInBounds(position)) {
    return false;
  }

  if(this.checkers[position.x][position.y] != null) {
    console.log("There's already a piece at given position.");
    return false;
  }
  var piece = new Checker(position, color);

  if(type == "Queen") {
    piece.Queened();
  }

  this.checkers[position.x][position.y] = piece;
  scene.add(piece.cylinder);
  return true;
}

function RemoveChecker(position) {
  if(!this.WithInBounds(position)) {
    return false;
  }

  if(this.checkers[position.x][position.y] == null) {
    console.log("There's no piece at given position.");
    return false;
  }

  var checker = this.checkers[position.x][position.y];
  scene.remove(checker.cylinder);
  checker.Remove();
  delete this.checkers[position.x][position.y];
  this.checkers[position.x][position.y] = null;
  return true;
}

function MoveChecker(from, to, eat) {
  if(!this.WithInBounds(from) || !this.WithInBounds(to)) {
    return false;
  }

  if(this.checkers[from.x][from.y] == null) {
    return false;
  }

  if(this.checkers[to.x][to.y] != null) {
    return false;
  }

  // TODO: There are more checks we can perform here, but for the meantime this is enough.
  checker = this.checkers[from.x][from.y];
  this.checkers[from.x][from.y] = null;
  this.checkers[to.x][to.y] = checker;
  checker.Move(to);

  if(eat) {
    console.log("Eat move.");

    // Move direction
    var xDirection = (to.x - from.x) / Math.abs((to.x - from.x));
    var yDirection = (to.y - from.y) / Math.abs((to.y - from.y));
    
    // Determin which piece(s) to remove.
    var deadPiecePosition = {'x':to.x - xDirection, 'y':to.y - yDirection};
    
    var dead = board.checkers[deadPiecePosition.x][deadPiecePosition.y];
    if(dead == null) { 
      console.log("Dead piece missing.");
    }
    this.RemoveChecker(deadPiecePosition);
  }
}