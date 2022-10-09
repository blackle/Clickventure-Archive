#!/usr/bin/env python3
from glob import glob
import json
import shutil
import os

os.chdir("out")

shutil.copyfile("../_index.html", "index.html")
shutil.copyfile("../_index.js", "index.js")
shutil.copyfile("../_index.css", "index.css")
shutil.copyfile("../_settings.js", "settings.js")

shutil.copyfile("../_viewer.js", "viewer.js")
shutil.copyfile("../_viewer.html", "viewer.html")
shutil.copyfile("../null.jpg", "img/null.jpg")

clickventures = []
for filename in glob("./*/data.json"):
	with open(filename, "r") as file:
		data = json.load(file)
	num_nodes = len(data["nodes"])
	num_imgs = len([node for node in data["nodes"] if 'img' in node and node['img'] != "null.jpg"])
	clickventure = {
		"img": data["img"],
		"title": data["title"],
		"schema": data["schema"],
		"slug": data["slug"],
		"url": data["url"],
		"num_nodes": num_nodes,
		"num_imgs": num_imgs,
	}
	clickventures.append(clickventure)

	path = os.path.join(os.path.dirname(filename), "index.html")
	try:
		os.remove(path)
	except:
		pass
	os.symlink("../viewer.html", path)
with open("data.json", "w") as file:
	json.dump(clickventures, file)