#!/usr/bin/env python3
import unicodedata
import re
from html.parser import HTMLParser
from pathlib import Path
import urllib.request
import os
class MyHTMLParser(HTMLParser):
  def handle_starttag(self, tag, attrs):
  	if tag == "iframe":
  		self.src = dict(attrs)["src"]

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

from xml.dom.minidom import parse

dom = parse("../index.xml")

for el in dom.getElementsByTagName("div"):
	a = el.getElementsByTagName("a")[0]
	url = a.getAttribute("href")
	name = a.firstChild.nodeValue
	img = a.getElementsByTagName("img")[0].getAttribute("src")
	slug = slugify(name)

	parser = MyHTMLParser()
	parser.feed(fetch(url).decode('utf-8'))
	url = parser.src
	assert(url is not None)
	print(url, img, slug, name)
	assert("interactives" in url)

	content = fetch(url).decode('utf-8')
	img_data = fetch(img)
	os.mkdir(slug)
	to_file(content, slug + "/index.html.original", "w")
	to_file(img_data, slug + "/thumb.jpg", "wb")
	to_file(name, slug + "/title.txt", "w")
	to_file(url, slug + "/url.txt", "w")


