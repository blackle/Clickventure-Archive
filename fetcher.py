#!/usr/bin/env python3

import unicodedata
import re
import urllib.request
import os
import json
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
from PIL import Image
import imagehash
import numpy as np
import io

def fetch(url):
	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
	headers={'User-Agent':user_agent,} 
	request=urllib.request.Request(url,None,headers)
	response = urllib.request.urlopen(request)
	data = response.read()
	return data

def to_file(data, filename, mode):
	with open(filename, mode) as f:
		f.write(data)

def inner_html(node):
	return node.encode_contents().decode("utf8").strip()

def slugify(value, allow_unicode=False):
	"""
	Taken from https://github.com/django/django/blob/master/django/utils/text.py
	Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
	dashes to single dashes. Remove characters that aren't alphanumerics,
	underscores, or hyphens. Convert to lowercase. Also strip leading and
	trailing whitespace, dashes, and underscores.
	"""
	value = str(value)
	if allow_unicode:
		value = unicodedata.normalize('NFKC', value)
	else:
		value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
	value = re.sub(r'[^\w\s-]', '', value.lower())
	return re.sub(r'[-\s]+', '-', value).strip('-_')

# extract from iframe
def get_true_url(url):
	data = fetch(url).decode('utf-8')
	soup = BeautifulSoup(data, features="lxml")
	return soup.find('iframe')['src']

# [(title, slug, url, thumbnail)]
def get_adventures():
	adventures=[]
	for x in range(16):
		data = fetch(f"https://clickhole.com/category/clickventures/page/{x+1}/").decode('utf-8')
		soup = BeautifulSoup(data, features="lxml")
		for article in soup.find_all("article"):
			thumbnail = ""
			img = article.find("img")
			if img is not None:
				thumbnail = img['src']
			a = article.find_all("a")[-1]
			title = inner_html(a)
			url = get_true_url(a['href'])
			slug = slugify(title)
			assert(url != "" and url is not None)
			assert(title != "" and title is not None)
			adventures.append((title, slug, url, thumbnail))
	return adventures

def classes(node):
	for x in node["class"]:
		yield x

def decompile_nodes_from_html(html, baseurl):
	soup = BeautifulSoup(html, features="lxml")

	schema = json.loads(inner_html(soup.find('script', {'type': 'application/ld+json'})))
	start_id = -1
	nodes = []
	for node in soup.find_all(class_='clickventure-node'):
		node_data = {}
		node_id = int(node["data-node-id"])
		node_data['id'] = node_id
		node_data['name'] = node["data-node-name"]
		is_finish = "clickventure-node-finish" in classes(node)
		is_start  = "clickventure-node-start" in classes(node)
		if is_start:
			start_id = node_id

		node_data['type'] = 'start' if is_start else ('end' if is_finish else 'node')
		imgs = node.find_all('img')
		if len(imgs) > 1:
			# the only messed up images are repeats
			imgs = imgs[:1]
		assert(len(imgs) <= 1)
		for img in imgs:
			# fetch image here
			node_data['img'] = img["data-src"]
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
		if (len(links_data) == 0 and is_finish == False):
			print("woops!", node_data['body'], node_id)
		assert(len(links_data) > 0 or is_finish)

		node_data['links'] = links_data
		nodes.append(node_data)
	assert(start_id != -1)
	return {"schema": schema, "start": start_id, "nodes": nodes}

def with_ztransform_preprocess(hashfunc, hash_size=8):
	def function(image):
		image = image.convert("L").resize((hash_size, hash_size), Image.ANTIALIAS)
		data = image.getdata()
		quantiles = np.arange(100)
		quantiles_values = np.percentile(data, quantiles)
		zdata = (np.interp(data, quantiles_values, quantiles) / 100 * 255).astype(np.uint8)
		image.putdata(zdata)
		return hashfunc(image)
	return function

phash_z_transformed = with_ztransform_preprocess(imagehash.phash, hash_size = 8)

def optimize_image(url):
	try:
		data = fetch(url)
	except:
		print("couldn't fetch", url)
		return "null.jpg"
	try:
		image = Image.open(io.BytesIO(data)).convert('RGB')
		image.thumbnail((620, 620))
		hsh = str(phash_z_transformed(image))
		image.save("./out/img/" + hsh + ".jpg", quality=95, optimize=True, progressive=True)
		return hsh + ".jpg"
	except:
		print("couldn't convert", url)
		return "null.jpg"

def fetch_and_replace_images(adventures):
	for adventure in tqdm(adventures):
		if 'img' in adventure:
			adventure['img'] = optimize_image(adventure['img'])
		for node in tqdm(adventure['nodes'], leave=False):
			if 'img' in node:
				node['img'] = optimize_image(node['img'])
	return adventures

adventures = get_adventures()
print(adventures)

adventures_data = []
for title, slug, url, thumbnail in adventures:
	if "embed-twine" in url:
		# skip the twine-based bird game for now
		continue
	if slug == 'mr-circle-goes-to-shape-city':
		# skip mr circle, totally busted :(
		continue
	print(f"fetching '{title}'")
	html = fetch(url).decode('utf-8')
	adventure = decompile_nodes_from_html(html, url)
	adventure["title"] = title
	adventure["slug"] = slug
	adventure["url"] = url
	adventure["img"] = thumbnail

	adventures_data.append(adventure)

try:
	os.mkdir("out")
	os.mkdir("out/img")
except:
	print("couldn't make out folders, probably already there")

print("fetching/optimizing images!")
adventures_data = fetch_and_replace_images(adventures_data)

for adventure in adventures_data:
	outfolder = f"out/{adventure['slug']}"
	try:
		os.mkdir(outfolder)
	except:
		pass
	jsn = json.dumps(
    adventure,
    sort_keys=True,
    indent=4,
    separators=(',', ': ')
	)
	to_file(jsn, outfolder + "/data.json", "w")