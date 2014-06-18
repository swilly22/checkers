function Animator() {
	this.Animate = Animate;
	this.BLA = BLA;
	this.animations = new Array();

	addEventListener("CheckerMove", this.BLA, false);
}

//function BLA(checker, from, to) {
function BLA(e) {

	var start = new Date().getTime()/1000;
	start += 1;
	var fromVector = BoardToSpaceCords(e.detail.from);
	var toVector = BoardToSpaceCords(e.detail.to);
	var direction = toVector.clone().sub(fromVector);
	var checker = e.detail.checker;
	
	function f() {
		var delta = new Date().getTime()/1000;
		delta = Math.abs(start - delta);
		delta /= 1;	// animation should take 2 seconds.
		delta = 1 - delta; // reverse, e.g. from -0.8 to -0.2
		//delta *= -1; // positive.
		delta = Math.abs(delta);
		var deltaVector = direction.clone().multiplyScalar(delta);
		console.log(checker.world_position.clone().sub(toVector).length());
		if(checker.world_position.clone().sub(toVector).length() > 0.01) {
			//checker.world_position.add(deltaVector);
			checker.world_position = fromVector.clone().add(deltaVector);
			checker.cylinder.position = checker.world_position;
			return false;
		}
		return true;
	}
	//this.animations.push(f);
	animator.animations.push(f);
}

function Animate() {
	for(var i = 0; i < this.animations.length; i++) {
		var method = this.animations[i];
		if(method()) {
			this.animations.splice(i, 1); // Remove animation. 
		}
	}
}