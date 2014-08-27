function Checker(position, color)
{
  this.color = colors[color];
  this.board_position = position;
  this.world_position = BoardToSpaceCords(this.board_position);
  this.cylinder = CreateCylinder(BOARD_WIDTH / 20 , BOARD_WIDTH / 20, 0.1, 32, this.color);
  this.cylinder.position = this.world_position;
  this.cylinder.checker = this;
  this.Selected = Selected;
  this.UnSelect = UnSelect;
  this.Move = Move;
  this.Remove = Remove;
  this.AnimateMove = AnimateMove;
  this.SetColor = SetColor;
  this.Queened = Queened;
}

function Remove() {
  this.cylinder = null;
}

function SetColor(color) {
  if(this.cylinder == null) { return; }
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
  // TODO: think of a better way figuring out if this is an eat move,
  // Maybe pass eat as a parameter to this function.
  event_type = "CheckerMove";
  if(Math.abs(src.y - dest.y) > 1) {
    event_type = "CheckerEat";
  }

  var event = new CustomEvent(event_type, 
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

function Queened() {
  // Fire event.
  event_type = "CheckerQueened";
  var event = new CustomEvent(event_type, 
    {
      detail:{
        checker:this
      }, 
      bubbles: true,
      cancelable: true
    });

    dispatchEvent(event);
}

function CreateCylinder(radiusTop, radiusBottom, height, segments, _color) {    
    var material = new THREE.MeshPhongMaterial( {color: _color} );
    cylinder = new THREE.Mesh(checker_geometry, material);      
    return cylinder;
}