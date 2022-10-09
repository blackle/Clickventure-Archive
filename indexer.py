#!/usr/bin/env python3
from glob import glob
import json
import shutil

shutil.copyfile("_index.html", "out/index.html")
shutil.copyfile("_index.js", "out/index.js")

clickventures = []
for filename in glob("out/*/data.json"):
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
with open("./out/data.json", "w") as file:
	json.dump(clickventures, file)