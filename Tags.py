import os
import collections
import shutil
import re
from mutagen.mp3 import *
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
	#print(to_move

"""if __name__ == '__main__':
	init()
#This section extracts subfolders from folders: Each folder in a library should be a collection of mp3 files with no subdirectories.

	#This section iterates through each folder, and checks the name correctness
	i = 0
	for subd in os.walk("."):
		title = subd[0]
		name = str(subd[0][2:])

		#os walk will always check the "." directory before any of it's subd's, so I'm skipping that iteration here.
		if (i == 0):
			i += 1
			continue
		if title in EXCEPTIONS:
			continue
		if os.sep in name:
			continue

		print(repr(name))
		fixIt = True
		notMusic = False
		hasMusic = False
		for file in subd[2]:
			if os.path.splitext(file)[1] in MUSIC_TYPES:
				hasMusic = True
		if hasMusic == False:
			text = getInput("This doesn't look like a music folder. Do you want to move it?\n", OPTIONS)
			if text in OPTIONS[:4]:
				shutil.move(subd[0], "./bin")
				print("Okay, it was moved.")
				fixIt = False
			else:
				text = getInput("\nOkay. Do you want to add this to the exceptions? (y/n)\n", OPTIONS)
				if text in OPTIONS[:4]:
					EXCEPTIONS.append(title)
					pickle.dump(EXCEPTIONS, expt)
					print("Okay.")
					continue

	
		if not fixIt:
			continue

		errors = find_errors(name)

		if (not errors):
			print("good name!\n")
		else:
			print("\nSeems like a bad name. Reasons:")
			for err in errors:
				print(ERR_MSGS[err])
			if 'parens' in errors:
				text = getInput("Parentheses and brackets can be removed automatically. Do you want to remove them?\n", OPTIONS)
				if text in OPTIONS[:4]:
					newName = fixParens(name)
					print("Okay, they were removed. The new name is " + newName +"\n")
					name = newName
					text = getInput("Want to do anything else with this name? (y/n)\n", OPTIONS)
					if text in OPTIONS[4:]:
						print("Okay.")
						continue
			text = getInput("Would you like to input a new name? (y/n)\n", OPTIONS)
			if text in OPTIONS[:4]:
				rename(name)
				print("Okay.")
			else:
				text = getInput("\nOkay. Do you want to add this to the exceptions? (y/n)\n", OPTIONS)
				if text in OPTIONS[:4]:
					expt = open(os.path.join(here, "exceptions.txt"), "wb")
					EXCEPTIONS.append(title)
					pickle.dump(EXCEPTIONS, expt)
					print("Okay.")
"""					