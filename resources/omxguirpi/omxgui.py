#!/usr/bin/python
import threading,glob,Tkinter
from os import listdir
from os.path import isfile, join
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
d=glob.g['appFolder']

glob.g['mainWindow'] = Tkinter.Tk()
glob.g['mainWindow'].title('OMXgui 0.1')
glob.g['mainWindow'].geometry("800x500")
img = Tkinter.PhotoImage(file='/etc/omxguirpi/images/film.png')
glob.g['mainWindow'].tk.call('wm', 'iconphoto', glob.g['mainWindow']._w, img)

glob.g['installedPlugins'] = sorted([f for f in listdir(d) if isfile(join(d, f))])
x=0

for e in glob.g['installedPlugins']:
	p=e.split('.')
	if p[1]=='py' and p[0]!='omxgui' and p[0]!='glob':
		glob.m[p[0]]=__import__(p[0])
		glob.m[p[0]].run()
		x+=1


def task():
	for cont in glob.m.values():
		cont.loop()

	glob.g['mainWindow'].after(200,task)


glob.g['mainWindow'].after(200,task)
glob.g['mainWindow'].mainloop()
