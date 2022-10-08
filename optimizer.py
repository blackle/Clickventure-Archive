#!/usr/bin/env python3
import glob
import json
from PIL import Image
import imagehash
import numpy as np
from tqdm import tqdm
import io

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

def optimize_image(filename):
	try:
		realname = "../adventures/embed/static/img/" + filename
		bts = b''
		with open(realname, "rb") as file:
			bts = file.read()
		image = Image.open(io.BytesIO(bts)).convert('RGB')
		image.thumbnail((620, 390))
		hsh = str(phash_z_transformed(image))
		image.save("./optimized/img/" + hsh + ".jpg", quality=95, optimize=True, progressive=True)
		return hsh + ".jpg"
	except:
		print("couldn't convert", filename)
		return "null.jpg"

adventures = glob.glob('*.json')
# adventures = ["youve-been-elected-to-congress-can-you-pass-even-one-goddamn-bill.json"]
for adventure in tqdm(adventures):
	with open(adventure, "r") as file:
		abenteuer = json.load(file)
	abenteuer['img'] = optimize_image(abenteuer['img'])
	for node in tqdm(abenteuer['nodes'], leave=False):
		if 'img' in node:
			node['img'] = optimize_image(node['img'])
	with open("optimized/"+adventure, "w") as file:
		json.dump(
			abenteuer,
			file,
			sort_keys=True,
			indent=4,
			separators=(',', ': ')
		)
