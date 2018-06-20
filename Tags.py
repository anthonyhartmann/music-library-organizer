import os
import collections
import shutil
import re
import mutagen
import pickle

PARENS = ['(', '[', ')', ']']
ERR_MSGS = {'fmt' : "The name isn't formatted correctly.", 'parens' : "The name contains parenthesis and/or brackets.", "notAN" : "The name contains non-alphanumeric characters."}
OPTIONS = ["y", "yes", "Y", "Yes", "no", "N", "n", "No"]
ERR_DICT = {''}
IMPLEMENTED = ["parens"]
ACCEPTABLE_TYPES = [".mp3", ".flac", ".jpg", ".png", ".nfo"]
MUSIC_TYPES = ACCEPTABLE_TYPES[:2]
EXCEPTIONS = []

def init():
	global EXCEPTIONS
	if not os.path.exists("bin"):
		os.makedirs("bin")
	if not os.path.exists("exceptions.txt"):
		expt = open("exceptions.txt", "wb+")
		new = []
		pickle.dump(new, expt)
	expt = open("exceptions.txt", "rb")
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

def fix(name, err):
	if (err == "parens"):
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


init()
expt = open("exceptions.txt", "wb+")
#This section extracts subfolders from folders: Each folder in a library should be a collection of mp3 files with no subdirectories.
done = False
while (not done):
	done = True
	text = getInput("Do you want to extract subdirectories to the main directory?\n", OPTIONS)
	if text in OPTIONS[:4]:
		for subd in os.walk("."):
			title = subd[0]
			if title in EXCEPTIONS:
				continue
			text = getInput(subd[0][2:] + "\n is a deep folder. Do you want to extract it?", OPTIONS)
			if text in OPTIONS[4:]:
				name = subd[0]
				depth = dirDepth(name)
				newName = name
				path = name
				if (depth > 0):
					done = False
					newName = name[2:].replace('\\', ' ')
					index = path.rfind('\\') + 1
					newPath = path[:index] + newName
					os.rename(path, newPath)
					finalPath = ".\\" + newName
					shutil.move(newPath, finalPath)
			else:
				continue
	else:
		done = True
#This section iterates through each folder, and checks the name correctness
i = 0
for subd in os.walk("."):
	title = subd[0]
	#os walk will always check the "." directory before any of it's subd's, so I'm skipping that iteration here.
	if (i == 0):
		i += 1
		continue
	if title in EXCEPTIONS:
		continue
	if os.sep in subd[0][2:]:
		continue

	name = subd[0][2:]
	print("\n\n" + name)
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
	
	if not fixIt:
		continue

	errors = find_errors(name)

	if (not errors):
		print("good name!\n")
	else:
		print("\nSeems like a bad name. Reasons:")
		for err in errors:
			print(ERR_MSGS[err])
		text = getInput("Would you like to fix it? (y/n)\n", OPTIONS)
		if text in OPTIONS[:4]:
			done = True
			for err in errors:
				if err in IMPLEMENTED:
					name = fix(name, err)
				else:
					done = False
			if (not done):
				text = getInput("This name can't be fixed automatically. Do you want to input a new name? (y/n)\n", OPTIONS)
				if text in OPTIONS[:4]:
					rename(name)
				else:
					print("Okay.")
			print("Done.")
		else:
			text = getInput("\nOkay. Do you want to add this to the exceptions? (y/n)\n", OPTIONS)
			if text in OPTIONS[:4]:
				EXCEPTIONS.append(title)
				pickle.dump(EXCEPTIONS, expt)
				print("Okay.")
pickle.dump(EXCEPTIONS, expt)