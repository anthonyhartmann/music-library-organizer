import os
import collections
import shutil
import re
from mutagen.mp3 import *
import mutagen.id3
import pickle
from os.path import *

PARENS = ['(', '[', ')', ']']
ERR_MSGS = {'fmt' : "The name isn't formatted correctly.", 'parens' : "The name contains parenthesis and/or brackets.", "notAN" : "The name contains non-alphanumeric characters."}
OPTIONS = ["y", "yes", "Y", "Yes", "no", "N", "n", "No"]
ERR_DICT = {''}
IMPLEMENTED = ["parens"]
ACCEPTABLE_TYPES = [".mp3", ".flac"]
MUSIC_TYPES = ACCEPTABLE_TYPES[:2]
EXCEPTIONS = ["", "_junk", ".git", "Tags.py", "Commands.py", "tktest.py", "AdjBox.py", "exceptions.txt", "__pycache__", "__TAGS__"]
ID3DICT = {'TALB' : 'Album', 'TPE1' : 'Artist', 'TIT2' : 'Title', 'TRCK' : 'Track', 'TDRC' : 'Year', 'TCON' : 'Genre'}


CLEAR_EXCEPTIONS = True

here = "."

def init():
	global EXCEPTIONS
	os.chdir("C:/Music")
	if not os.path.isdir("junk"):
		os.makedirs("junk")
	if CLEAR_EXCEPTIONS:
		os.remove("exceptions.txt")
	if not os.path.exists("exceptions.txt"):
		expt = open(os.path.join(here, "exceptions.txt"), "wb+")
		new = ["./bin", "./.git"]
		pickle.dump(EXCEPTIONS, expt)
		expt.close()
	expt = open(os.path.join(here, "exceptions.txt"), "rb")
	EXCEPTIONS = pickle.load(expt)

def getInput(prompt, options):
	text = input(prompt)
	while (text not in options):
			print("Please select a valid option")
			text = input(prompt)
	return text

def remove_parens(name):
	ret = ''
	skip1c = 0
	skip2c = 0
	for char in name:
		if char == '[':
			skip1c += 1
		elif char == '(':
			skip2c += 1
		elif char == ']' and skip1c > 0:
			skip1c -= 1
		elif char == ')'and skip2c > 0:
			skip2c -= 1
		elif skip1c == 0 and skip2c == 0:
			ret += char
	return ret

def rename(name):
	path = "./" + name
	text = input("Enter a new name for this album.\n")
	newPath = "./" + text
	os.rename(path, newPath)
	EXCEPTIONS.append(newPath)
	return

def dirDepth(dirName):
	d = collections.defaultdict(int)
	for c in dirName:
		d[c] += 1
	return d['\\'] - 1

def fixParens(name):
	path = "./" + name
	name = remove_parens(name)
	newPath = "./" + name
	os.rename(path, newPath)
	return name


def find_errors(name):
	#tests for non-alphanumeric characters, text in parenthesis, 
	errors = set()
	match = re.fullmatch("((\w| )+ - (\w| )+)", name)
	if (match != None):
		return errors
	else:
		alph = name.replace("'", "")
		AN = re.fullmatch("(\w| |-|\(|\[|\)|\])+", alph)
		if (AN == None):
			errors.add("notAN")
		fmt = re.fullmatch("([^-]+ - [^-]+)", name)
		if (fmt == None):
			errors.add("fmt")
		for char in PARENS:
			if char in name:
				errors.add("parens")
				break
		return errors

def list_contents(folder):
	"""This scans through the entire directory, and lists all folders
	 and files in the root directory."""
	retlist = []
	for file in os.listdir(folder):
		if file not in EXCEPTIONS:
			retlist.append(file)
	return retlist
def isMusic(folder):
	nest = []
	for file in os.listdir(folder):
		if file == folder:
			continue
		elif isdir(file):
			nest.append(file)
		elif any([file.endswith(typ) for typ in ACCEPTABLE_TYPES]):
			return True
	if any([isMusic(item) for item in nest]):
		return True
	return False

#Sorts through all folders in the main folder via a stack. 
#If there are no folders in the root, return.
def remove_junk():
	to_move = []
	done = False
	for item in os.listdir(here):
		if isdir(item) and (not isMusic(item)):
			to_move.append(item)
		if isfile(item):
			to_move.append(item)
	filtered = [x for x in to_move if x not in EXCEPTIONS]
	prev = ["./" + x for x in filtered]
	dest = ["./_junk/" + x for x in filtered]
	for i in range(0, len(prev)):
		shutil.move(prev[i], dest[i])

def get_tags(file, directory):
	pathbase = os.getcwd() + directory[1:] + os.sep + file
	data = MP3(pathbase)
	tags = {}
	for key in ID3DICT.keys():
		if data.get(key):
			tags[ID3DICT[key]] = data.get(key).text[0]
	return tags

#tags is a dictionary of {TYPE : ITEM} where type is the plain name of an ID3 tag type, and item is this item's tag.
def save_tags(file, directory, tags):
	pathbase = os.getcwd() + directory[1:] + os.sep + file
	data = MP3(pathbase)
	if not data.get('TIT2'):
		print("ERROR: SONG HAS NO TITLE TAG?")
		return
	enc = data.get('TIT2').encoding
	testdict = {}
	for key in tags.keys():
		id3key = [x for x in ID3DICT.keys() if ID3DICT[x] == key][0]
		data[id3key] = getattr(mutagen.id3, id3key)(encoding = enc, text=[tags[key]])
	data.save(pathbase)
	return