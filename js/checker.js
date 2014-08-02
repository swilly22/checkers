function Checker(position, color)
{
  this.color = colors[color];
  this.board_position = position;
  this.world_position = BoardToSpaceCords(this.board_position);
  this.cylinder = CreateCylinder(BOARD_WIDTH / 20 , BOARD_WIDTH / 20, 0.2, 32, this.color);
  this.cylinder.position = this.world_position;
  this.cylinder.checker = this;
  this.Selected = Selected;
  this.UnSelect = UnSelect;
  this.Move = Move;
  this.Remove = Remove;
  this.AnimateMove = AnimateMove;
  this.SetColor = SetColor;
}

function Queen(position, color) {
  this.color = colors[color];
  this.board_position = position;
  this.world_position = BoardToSpaceCords(this.board_position);
  this.cylinder = CreateCube(BOARD_WIDTH / 20 , BOARD_WIDTH / 20, BOARD_WIDTH / 20, this.color);
  this.cylinder.position = this.world_position;
  this.cylinder.checker = this;
  this.Selected = Selected;
  this.UnSelect = UnSelect;
  this.Move = Move;
  this.Remove = Remove;
  this.AnimateMove = AnimateMove;
  this.SetColor = SetColor; 
}

function Remove() {
  this.cylinder = null;
}

function SetColor(color) {
  this.cylinder.material.color.setHex(color);
}

function AnimateMove(position) {
  this.world_position = position;
  this.cylinder.position = this.world_position;
}

function Move(position) {
  var src = this.board_position;
  var dest = position;

  // Fire move event.
  var event = new CustomEvent("CheckerMove", 
    {
      detail:{
        checker:this, from:src, to:dest
      }, 
      bubbles: true,
      cancelable: true
    });
  this.board_position = position;
  if(this.color != colors[player_color]) {
    dispatchEvent(event);
  }
}

function Selected() {  
  this.SetColor(this.color + COLOR_BRIGHTNESS_INC);
}

function UnSelect() {
  this.SetColor(this.color);
}

function CreateCylinder(radiusTop, radiusBottom, height, segments, _color) {
    var geometry = new THREE.CylinderGeometry( radiusTop, radiusBottom, height, segments);
    var material = new THREE.MeshBasicMaterial( {color: _color} );
    var cylinder = new THREE.Mesh( geometry, material );
    return cylinder;
}

function CreateCube(width, height, depth, _color) {
  var geometry = new THREE.BoxGeometry(width, height, depth);
  var material = new THREE.MeshBasicMaterial({color: _color});
  var cube = new THREE.Mesh(geometry, material);
  return cube;
}