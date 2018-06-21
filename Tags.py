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
EXCEPTIONS = [".\\bin", ".\.git"]
here = os.path.dirname(os.path.abspath(__file__))

def init():
	global EXCEPTIONS
	if not os.path.exists("bin"):
		os.makedirs("bin")
	if not os.path.exists("exceptions.txt"):
		expt = open(os.path.join(here, "exceptions.txt"), "wb+")
		new = ["./bin", "./.git"]
		pickle.dump(EXCEPTIONS, expt)
		expt.close()
		print("dumped")
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


if __name__ == '__main__':
	init()
#This section extracts subfolders from folders: Each folder in a library should be a collection of mp3 files with no subdirectories.
	done = False
	while (not done):
		done = True
		text = getInput("\nDo you want to extract subdirectories to the main directory?\n", OPTIONS)
		if text in OPTIONS[:4]:
			i = 0
			for parent in os.walk("."):
				if (i == 0):
					i += 1
					continue
				title = parent[0]
				if title in EXCEPTIONS:
					continue
				if os.sep in parent[0][2:]:
					continue
				deep = False
				for subd in os.walk(title):
					if dirDepth(subd[0]) > 0 and deep == False:
						text = getInput("\n" + title[2:] + " is a deep folder. Do you want to extract it?\n", OPTIONS)
						if text in OPTIONS[:4]:
							deep = True
							continue
						else: 
							break
				if deep == True:
					name = parent[0]
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
					EXCEPTIONS.append(title)
					pickle.dump(EXCEPTIONS, expt)
					print("Okay.")