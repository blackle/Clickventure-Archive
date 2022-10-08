#!/usr/bin/env python3
import glob
import unicodedata
import re
from bs4 import BeautifulSoup
import urllib.request
import os.path
from hashlib import sha256

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

def sha256sum(data):
	h = sha256()
	h.update(data)
	return h.hexdigest()

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

def from_file(filename):
	with open(filename, "rb") as f:
		return f.read().decode('utf8')

for adventure in glob.glob('./*')[71:]:
	if adventure == "./embed":
		continue
	url = from_file(adventure + "/url.txt")
	html = from_file(adventure + "/index.html.original")
	print(adventure)
	soup = BeautifulSoup(html, features="lxml")
	for img in soup.find_all('img'):
		src = img["data-src"]
		if src is not None:
			print("getting ", src)
			base = os.path.basename(src)
			try:
				data = fetch(src)
			except:
				data = b''
			newname = sha256sum(data)
			local_src = "embed/static/img/" + newname + ".jpg"
			to_file(data, "./" + local_src, "wb")
			img["data-src"] = "/" + local_src
	to_file(str(soup), adventure + "/index.html", "w")
