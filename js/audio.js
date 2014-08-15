sounds_files = ["sounds/move_1.mp3", "sounds/piece_1.mp3"]; 
sounds = new Array(sounds_files.length);

var SOUND_CHECKER_MOVE = 0;
var SOUND_CHECKER_EAT = 1;

function PlayCheckerMove() {
	PlaySound(SOUND_CHECKER_MOVE);
}

function PlayCheckerEat() {
	PlaySound(SOUND_CHECKER_EAT);
}

// Plays the specified sound.
function PlaySound(sound_id) {
	var sound = sounds[sound_id]
	sound.play();
}

// Loads all sounds specified in the sounds_files array.
// TODO make sure all sounds have been loaded before trying to play any of them.
function LoadSounds() {
	for(var sound_idx = 0; sound_idx < sounds_files.length; sound_idx++) {
		console.log("Loading sound " + sounds_files[sound_idx])
		sounds[sound_idx] = new Audio(sounds_files[sound_idx]);
	}

	console.log("Done loading sounds."); // This might be not so true. (check for loaded callback) 
}

LoadSounds();