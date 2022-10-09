const settings_link = document.querySelector("#clickventure-settings");
const settings_back = document.querySelector("#settings-back");
const settings_container = document.querySelector("#settings-container");
const disable_animations = document.querySelector("#disable-animations")

function settings_toggler(target) {
	return function(e) {
		if (e.target == target) {
			settings_container.classList.toggle("hidden");
		}
	}
}

settings_link.onclick = settings_toggler(settings_link);
settings_back.onclick = settings_toggler(settings_back);
settings_container.onclick = settings_toggler(settings_container);

function on_is_no_animation_changed() {
	if (is_no_animation()) {
		document.body.classList.add("no-animation")
	} else {
		document.body.classList.remove("no-animation")
	}
}

disable_animations.checked = localStorage.getItem('no-animation') == "true";
disable_animations.onchange = function () {
	localStorage.setItem('no-animation', disable_animations.checked ? "true" : "false");
	on_is_no_animation_changed();
}
on_is_no_animation_changed();