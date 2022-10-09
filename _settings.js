const settings_link = document.querySelector("#clickventure-settings");
const settings_back = document.querySelector("#settings-back");
const settings_container = document.querySelector("#settings-container");
const disable_animations = document.querySelector("#disable-animations");

function init_tabblable_elements() {
	const focusable_elements = document.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
	for (const el of focusable_elements) {
		tabindex = el.getAttribute("tabindex");
		if (tabindex != '') {
			el.dataset.tabindex = tabindex
		}
	}
}

function set_tabbable_state(state) {
	const focusable_elements = document.querySelectorAll('button, [href], input, select, textarea, [tabindex]');
	for (const el of focusable_elements) {
		if (settings_container.contains(el) == state) {
			el.setAttribute("tabindex", "-1")
		} else {
			el.removeAttribute("tabindex")
			if ("tabindex" in el.dataset) {
				el.setAttribute("tabindex", el.dataset.tabindex)
			}
		}
	}
}

function toggle_settings() {
	if (settings_container.classList.contains("hidden")) {
		settings_container.classList.remove("hidden");
		set_tabbable_state(false);
	} else {
		settings_container.classList.add("hidden");
		set_tabbable_state(true);
	}
}

init_tabblable_elements();
set_tabbable_state(true);

function settings_key_toggler(target) {
	return function(e) {
		if (e.keyCode == 13) {
			toggle_settings();
			return false;
		}
	};
}

function settings_toggler(target) {
	return function(e) {
		if (e.target == target) {
			toggle_settings();
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