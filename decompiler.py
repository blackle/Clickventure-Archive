#!/usr/bin/env python3
import glob
from bs4 import BeautifulSoup
import json
import os.path
from hashlib import sha256

def from_file(filename):
	with open(filename, "rb") as f:
		return f.read()

def classes(node):
	for x in node["class"]:
		yield x

def to_file(data, filename, mode):
	with open(filename, mode) as f:
		f.write(data)

def inner_html(node):
	return node.encode_contents().decode("utf8").strip()

def sha256sum(data):
	h = sha256()
	h.update(data)
	return h.hexdigest()

for adventure in glob.glob('./*'):
	if adventure == "./embed":
		continue
	title = from_file(adventure + "/title.txt").decode('utf8')
	html = from_file(adventure + "/index.html").decode('utf8')
	img_data = from_file(adventure + "/thumb.jpg")
	img_name = sha256sum(img_data) + ".jpg"
	to_file(img_data, "embed/static/img/" + img_name, "wb")
	print(adventure)
	soup = BeautifulSoup(html, features="lxml")
	schema = json.loads(inner_html(soup.find('script', {'type': 'application/ld+json'})))
	abenteuer = {'title':title, 'nodes':[], 'schema':schema, 'img': img_name}
	for node in soup.find_all(class_='clickventure-node'):
		node_data = {}
		node_id = int(node["data-node-id"])
		node_data['id'] = node_id
		node_data['name'] = node["data-node-name"]
		is_finish = "clickventure-node-finish" in classes(node)
		is_start  = "clickventure-node-start" in classes(node)
		if is_start:
			abenteuer['start'] = node_id

		node_data['type'] = 'start' if is_start else ('end' if is_finish else 'node')
		imgs = node.find_all('img')
		if len(imgs) > 1:
			# the only messed up images are repeats
			imgs = imgs[:1]
		assert(len(imgs) <= 1)
		for img in imgs:
			node_data['img'] = os.path.basename(img["data-src"])
		body = node.find(class_='clickventure-node-body')
		for s in body.select('img'):
			s.decompose()
		node_data['body'] = inner_html(body)

		# no need to add finish_links, they're all the same
		# finish_links = node.find(class_="clickventure-node-finish-links")
		# if finish_links is not None:
		# 	assert(is_finish)
		# 	links = finish_links.find_all(class_="clickventure-node-link-text")
		# 	assert(len(links) == 1)
		# 	for link in links:
		# 		assert(inner_html(link) == "Start Over")
		# else:
		# 	assert(is_finish == False)

		links_group = node.find(class_="clickventure-node-links")
		links = links_group.find_all(class_="clickventure-node-link")
		links_data = []
		# print("node", node_id)
		for link in links:
			target = int(link["data-target-node"])
			button = link.find(class_="clickventure-node-link-button")
			is_bubble = "clickventure-node-link-word-bubble" in classes(button)
			is_action = "clickventure-node-link-action" in classes(button)
			is_music = "clickventure-node-link-music" in classes(button)
			is_quiz = "clickventure-node-link-quiz" in classes(button)
			# print(link)
			assert(is_bubble or is_action or is_music or is_quiz)
			link_data = {}
			link_data["target"] = target
			link_data["type"] = "quiz" if is_quiz else ("music" if is_music else ("bubble" if is_bubble else "text"))
			link_data["content"] = inner_html(button.find(class_="clickventure-node-link-text"))
			links_data.append(link_data)
		assert(len(links_data) > 0 or is_finish)

		node_data['links'] = links_data
		abenteuer['nodes'].append(node_data)
	assert('start' in abenteuer)
	jsn = json.dumps(
    abenteuer,
    sort_keys=True,
    indent=4,
    separators=(',', ': ')
	)
	to_file(jsn, adventure + "/" + adventure + ".json", "w")
