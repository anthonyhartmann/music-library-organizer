from Tags import list_contents, get_tags, save_tags
import tkinter as tk
import os
ID3DICT = {'TALB' : 'Album', 'TPE1' : 'Artist', 'TIT2' : 'Title', 'TRCK' : 'Track', 'TDRC' : 'Year', 'TCON' : 'Genre'}

def list_folder(folder, currFolder, box):
	if folder == ".":
		if box.size() != 0:
			box.delete('0','end')
		retlist = list_contents(folder)
		for item in retlist:
			aitem = item
			box.insert(tk.END, aitem)
		return "."
	else:
		if folder == "":
			return None
		if box.size() != 0:
			box.delete('0','end')
		folder = currFolder + os.sep + folder
		retlist = list_contents(folder)
		for item in retlist:
			aitem = item
			box.insert(tk.END, aitem)
		return folder

def back_button(box):
	cf = box.currFolder
	index = cf.rfind(os.sep)
	folder = cf[:index]
	list_folder(folder, cf, box)
	box.currFolder = folder

def list_button(box):
	if box.curselection():
		box.currFolder = list_folder(box.get(box.curselection()), box.currFolder, box)
	return

def tags_button(box):
	if box.curselection():
		tags = get_tags(box.get(box.curselection()), box.currFolder)
		tp = tk.Toplevel()
		rw = 0
		for item in ID3DICT.values():
			label = tk.Label(tp, text=item)
			entry = tk.Entry(tp, width=30)
			if tags.get(item):
				entry.insert(0, tags.get(item))
			label.grid(column=0, row=rw)
			entry.grid(column=1, row=rw)
			rw += 1
		tp.grid_columnconfigure(1, weight=1)
		sbutton= tk.Button(tp, text="Save", command=lambda: save_button(tp, box.get(box.curselection()), box.currFolder))
		sbutton.grid(column=0, row=rw)
	return

def save_button(window, file, directory):
	print(file)
	print(directory)
	wlist = window.winfo_children()
	types = []
	items = []
	for elem in wlist:
		if elem.winfo_class() == 'Entry':
			items.append(elem.get())
		if elem.winfo_class() == 'Label':
			types.append(elem.cget("text"))
	newTags = {}
	for i in range(0, len(types)):
		if items[i] == '':
			continue
		newTags[types[i]] = items[i]
	save_tags(file, directory, newTags)
	return
	