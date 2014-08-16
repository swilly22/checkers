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

function MoveChecker(from, to) {
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

  // Check if this is an eat move.
  if(Math.abs(from.x - to.x) > 1) {
    console.log("Eat move.");

    // Determin which piece(s) to remove.
    var middel = {'x' : (from.x + to.x) / 2, 'y' : (from.y + to.y) / 2};

    var dead = board.checkers[middel.x][middel.y];
    if(dead == null) { 
      console.log("Dead piece missing.");
    }
    this.RemoveChecker(middel);
  }
}