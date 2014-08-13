function Animator() {
	this.Animate = Animate;
	this.AnimateCheckerMove = AnimateCheckerMove;
	this.AnimateCheckerEat = AnimateCheckerEat;
	this.animations = new Array();

	addEventListener("CheckerMove", this.AnimateCheckerMove, false);
	addEventListener("CheckerEat", this.AnimateCheckerEat, false);
}

function AnimateCheckerEat(e) {
	var start = new Date().getTime()/1000;

	// Take into account other animations which might be runnning.
	// Multiplying by animator.animations.length + 1
	// "waints" for previous animations to finish.
	start += 0.5 * (animator.animations.length + 1);
	var fromVector = BoardToSpaceCords(e.detail.from);
	var toVector = BoardToSpaceCords(e.detail.to);
	var direction = toVector.clone().sub(fromVector);
	var checker = e.detail.checker;
	
	function f() {
		var delta = new Date().getTime()/1000;
		delta = start - delta;
		delta /= 0.5;	// animation should take 1/2 seconds.
		delta = 1 - delta; // reverse, e.g. from -0.8 to -0.2
		//delta *= -1; // positive.
		delta = Math.abs(delta);
		var deltaVector = direction.clone().multiplyScalar(delta);
		console.log(delta);

		if(delta > 1) // Enough time has pass such that delta > start.
		{
			checker.world_position = toVector;
			checker.cylinder.position = checker.world_position;

			// Restore checker y value.
			checker.cylinder.position.y = checker.world_position.y
			return true;
		}

		if(checker.world_position.clone().sub(toVector).length() > 0.09) {
			checker.world_position = fromVector.clone().add(deltaVector);
			checker.cylinder.position = checker.world_position;

			// Bounch effect.
			// Map delta to 0 - pi/2
			x = Map(delta, 0, 1, 0, Math.PI);
			y = Math.sin(x);

			// Add sin value to checker's "BASE" y value.
			checker.cylinder.position.y = checker.world_position.y + y;
			// End of counch effect.

			return false;
		}

		// Restore checker y value.
		checker.cylinder.position.y = checker.world_position.y
		return true;
	}
	//this.animations.push(f);
	animator.animations.push(f);
}

function AnimateCheckerMove(e) {

	var start = new Date().getTime()/1000;

	// Take into account other animations which might be runnning.
	// Multiplying by animator.animations.length + 1
	// "waints" for previous animations to finish.
	start += 0.5 * (animator.animations.length + 1);
	var fromVector = BoardToSpaceCords(e.detail.from);
	var toVector = BoardToSpaceCords(e.detail.to);
	var direction = toVector.clone().sub(fromVector);
	var checker = e.detail.checker;
	
	function f() {
		var delta = new Date().getTime()/1000;
		delta = start - delta;
		delta /= 0.5;	// animation should take 1/2 seconds.
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

	// only one animation can execute on each frame.
	if(this.animations.length > 0) {
		var method = this.animations[0];
		if(method()) {
			this.animations.splice(0, 1); // Remove animation.
		}
	}
}

// Maps value from one range to another.
function Map(value, from1, to1, from2, to2) {
    return (value - from1) / (to1 - from1) * (to2 - from2) + from2;
}