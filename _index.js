const container = document.querySelector(".container");
const clickventure_template = document.querySelector("#clickventure-template");

//called from settings.js
function on_is_no_animation_changed() {}

const IMAGE_ROOT = "img/"
function get_image(node) {
	if ('img' in node && node['img'] != undefined) {
		return IMAGE_ROOT + node['img']
	}
	return IMAGE_ROOT + "null.jpg"
}

function sortByKey(array, key) {
	return array.sort(function(a, b) {
		var x = key(a); var y = key(b);
		return ((x < y) ? 1 : ((x > y) ? -1 : 0));
	});
}

async function generate_list(url) {
  const response = await fetch(url);
  let gamelist = await response.json();
  gamelist = sortByKey(gamelist, function(game) {
  	return game['schema']['datePublished'];
  });
  for (const game of gamelist) {
  	var clickventure = clickventure_template.content.cloneNode(true);

  	const title = clickventure.querySelector("h2");
  	const img = clickventure.querySelector("img");
  	const date = clickventure.querySelector(".date-published");
  	const nodecount = clickventure.querySelector(".node-count");
  	const originalurl = clickventure.querySelector(".original-url");
  	const indicator = clickventure.querySelector(".indicator");
  	const value = clickventure.querySelector(".value");
  	const play = clickventure.querySelector(".play");
  	img.src = get_image(game);

  	date.textContent = game['schema']['datePublished'].substr(0,10);

  	originalurl.textContent = game['url'];
  	originalurl.href = game['url'];

  	nodecount.innerHTML = "<b>" + game['num_nodes'] + "</b>";

  	const ratio = Math.round(game['num_imgs'] / game['num_nodes'] * 1000) / 10
  	indicator.style.width = ratio + "%";
  	value.textContent = ratio + "%";

  	play.href = game['slug'] + "/";

  	title.innerHTML = game['title'];
  	container.appendChild(clickventure);
  }
}

generate_list("data.json")