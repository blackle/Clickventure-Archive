const settings_link = document.querySelector("#clickventure-settings");
const settings_back = document.querySelector("#settings-back");
const settings_container = document.querySelector("#settings-container");
const disable_animations = document.querySelector("#disable-animations");
const main_container = document.querySelector(".container");

const focusable_elements = settings_container.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');

let modal_showing = false;
document.addEventListener('keydown', function(e) {
  let isTabPressed = e.key === 'Tab' || e.keyCode === 9;

  if (!isTabPressed || !modal_showing) {
    return;
  }

  if (e.shiftKey) { // if shift key pressed for shift + tab combination
    if (document.activeElement === focusable_elements[0]) {
      focusable_elements[focusable_elements.length - 1].focus(); // add focus for the last focusable element
      e.preventDefault();
    }
  } else { // if tab key is pressed
    if (document.activeElement === focusable_elements[focusable_elements.length - 1]) { // if focused has reached to last focusable element then focus first focusable element after pressing tab
      focusable_elements[0].focus(); // add focus for the first focusable element
      e.preventDefault();
    }
  }
});

function toggle_settings(waskey) {
	if (settings_container.classList.contains("hidden")) {
		modal_showing = true;
		settings_container.classList.remove("hidden");
		if (waskey) { settings_back.focus(); }
	} else {
		modal_showing = false;
		settings_container.classList.add("hidden");
		if (waskey) { settings_link.focus(); }
	}
}

function settings_key_toggler(target) {
	return function(e) {
		if (e.keyCode == 13) {
			toggle_settings(true);
			return false;
		}
	};
}

function settings_toggler(target) {
	return function(e) {
		if (e.target == target) {
			toggle_settings(false);
		}
	}
}

settings_link.onclick = settings_toggler(settings_link);
settings_back.onclick = settings_toggler(settings_back);
settings_container.onclick = settings_toggler(settings_container);

settings_back.onkeydown = settings_key_toggler(settings_back);
settings_link.onkeydown = settings_key_toggler(settings_link);

disable_animations.checked = localStorage.getItem('no-animation') == "true";
disable_animations.onchange = function () {
	localStorage.setItem('no-animation', disable_animations.checked ? "true" : "false");
	on_is_no_animation_changed();
}
on_is_no_animation_changed();