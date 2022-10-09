const title_tag = document.querySelector("#clickventure-header");
const main_tag = document.querySelector("main");
const img_tag = document.querySelector("#clickventure-img");
const body_tag = document.querySelector("#clickventure-body");
const links_tag = document.querySelector("#clickventure-links");

function is_no_animation() {
	const isReduced = window.matchMedia(`(prefers-reduced-motion: reduce)`) === true || window.matchMedia(`(prefers-reduced-motion: reduce)`).matches === true;
	if (isReduced) {
		return true;
	}
	return localStorage.getItem('no-animation') == "true";
}

//called from settings.js
function on_is_no_animation_changed() {
	if (is_no_animation()) {
		document.body.classList.add("no-animation")
	} else {
		document.body.classList.remove("no-animation")
	}
}

// setinterval that automatically cancels/calls the previous interval
function delayifyer() {
	currtimeout = -1;
	lastop = function(){};
	return function(func, timeout) {
		lastop();
		window.clearTimeout(currtimeout);
		currtimeout = window.setTimeout(function(){
			currtimeout = -1;
			lastop = function(){};
			func();
		}, timeout);
		lastop = func;
	}
}

const IMAGE_ROOT = "../img/"
function get_image(node) {
	if ('img' in node && node['img'] != undefined) {
		return IMAGE_ROOT + node['img']
	}
	return IMAGE_ROOT + "null.jpg"
}

async function start_game(url) {
  const response = await fetch(url);
  const gamedata = await response.json();
  let nodemap = {};
  for (const node of gamedata['nodes']) {
  	nodemap[node['id']] = node;
  }
  const startid = gamedata['start'];
	title_tag.textContent = gamedata['title']
	document.title = gamedata['title'] + " | Clickventure Archive"

	function change_hash(hash) {
		const waschanged = window.location.hash.substring(1) != hash;
		console.log(waschanged)
		window.location.hash = hash;
		if (!waschanged) { onhashchange(); }
	}

	let preloads = []
	function get_image_tag(node) {
		const imgsrc = get_image(node);
		for (const preload of preloads) {
			if (preload.src == imgsrc) {
				return preload;
			}
		}
		var img=new Image();
		img.src=imgsrc;
		return img;
	}

	async function show_node(node) {
		img = get_image_tag(node);
		img_tag.textContent = "";
		img_tag.appendChild(img);
		body_tag.innerHTML = node['body'];
		links_tag.textContent = "";
		if (node['type'] == 'end') {
			main_tag.classList.add("clickventure-end");
		} else {
			main_tag.classList.remove("clickventure-end");
		}
		preloads = []
		for (const [i, link] of node['links'].entries()) {
			let btn = document.createElement("button");
			btn.innerHTML = link['content'];
			let target = link['target'];
			btn.onclick = function() {
				change_hash(target);
			};
			btn.classList.add("link-type-"+link['type'])
			links_tag.appendChild(btn);
			if (i != node['links'].length - 1 || node['type'] == 'end') {
				links_tag.appendChild(document.createElement("br"));
			}

			preloads.push(get_image_tag(nodemap[target]));
		}
		if (node['type'] == 'end') {
			let btn = document.createElement("button");
			btn.innerHTML = "Start Over";
			btn.onclick = function() {
				change_hash(startid);
			};
			btn.classList.add("link-type-start-over")
			links_tag.appendChild(btn);
		}
		main_tag.classList.remove("hidden");
	}

	const delayer = delayifyer();
	function onhashchange() {
		main_tag.classList.add("hidden");
		hash = window.location.hash.substring(1);
		delayer(function() {
			if (isNaN(hash) == false && hash != "") {
				show_node(nodemap[parseInt(hash, 10)]);
			} else {
				show_node(nodemap[startid]);
			}

		}, is_no_animation() ? 0 : 200);
	}
	window.addEventListener('hashchange', onhashchange);
	onhashchange();
}

start_game("./data.json");
