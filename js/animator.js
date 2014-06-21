function Animator() {
	this.Animate = Animate;
	this.BLA = BLA;
	this.animations = new Array();

	addEventListener("CheckerMove", this.BLA, false);
}

//function BLA(checker, from, to) {
function BLA(e) {

	var start = new Date().getTime()/1000;
	start += 0.5;
	var fromVector = BoardToSpaceCords(e.detail.from);
	var toVector = BoardToSpaceCords(e.detail.to);
	var direction = toVector.clone().sub(fromVector);
	var checker = e.detail.checker;
	
	function f() {
		var delta = new Date().getTime()/1000;
		delta = start - delta;
		delta /= 0.5;	// animation should take 1 seconds.
		delta = 1 - delta; // reverse, e.g. from -0.8 to -0.2
		//delta *= -1; // positive.
		delta = Math.abs(delta);
		var deltaVector = direction.clone().multiplyScalar(delta);
		console.log(delta);

		if(delta > 1) // Enough time has pass such that delta > start.
		{
			checker.world_position = toVector;
			checker.cylinder.position = checker.world_position;
			return true;
		}

		if(checker.world_position.clone().sub(toVector).length() > 0.09) {
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