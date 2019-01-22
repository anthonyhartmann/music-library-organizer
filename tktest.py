from tkinter import *
from Tags import *
from AdjBox import *
from Commands import *
from os import *
from pathlib import *
global CURRENT_FOLDER



main = Tk()

main.title("Comb")
init()

f1 = Frame(main)
f2 = Frame(main)
b1 = Frame(f2)
b2 = Frame(f2)
b3 = Frame(f2)
empty = Frame(f2)
empty.pack(side=BOTTOM, pady=140)
b1.pack(pady=1)
b2.pack(pady=1)
b3.pack(pady=1)
f1.pack(side=LEFT)
f2.pack(side=RIGHT, padx=5)

listc = Button(b1, text="List Contents", command= lambda: list_button(output), width=10, padx=20)
listc.pack(side=TOP)

back = Button(b2, text="Back", command= lambda: back_button(output), width=10, padx=20)
back.pack(side=TOP)

junk = Button(b3, text="Remove Junk", command= remove_junk, width=10, padx=20)
junk.pack(side=TOP)

sb = Scrollbar(f1, orient=VERTICAL)
output = AdjBox(f1, ".", width = 100, height = 30, yscrollcommand=sb.set)
sb.config(command=output.yview)
sb.pack(side=RIGHT, fill=Y)
output.pack(side= LEFT,fill=BOTH, expand=1)

list_folder(".", None, output)

main.mainloop()