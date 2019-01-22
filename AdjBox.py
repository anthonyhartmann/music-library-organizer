from tkinter import *
from Tags import *
from Commands import *
"""Implements an adjusted listbox that adds right click functionality to selected items."""
class AdjBox(Listbox):


	def __init__(self, parent, folder, *args, **kwargs):
		Listbox.__init__(self, parent, *args, **kwargs)
		self.currFolder = folder
		self.popup_menu = Menu(self, tearoff=0)
		self.bind("<Button-3>", self.popup)
		self.popup_menu.add_command(label="Open", command= lambda: list_button(self))
		self.popup_menu.add_command(label="Tags", command=lambda: tags_button(self))

	def popup(self, event):
		try:
			self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
		finally:
			self.popup_menu.grab_release()