import glob,Tkinter,requests,urllib,shutil,os
from time import sleep

descriptionTextarea=None
installButton=None
uninstallButton=None
selectedPlugin=None
active=''
def run():
	glob.g['context'].add_command(label="Plugins", command=contextPluginOpen)
	
	
def loop():
	a=0

def contextPluginOpen():
	global descriptionTextarea,installButton,uninstallButton
	pluginWIndow = Tkinter.Toplevel()
	pluginWIndow.title('Plugins  0.1')
	pluginWIndow.geometry("800x400+120+120")
	
	w = Tkinter.Label(pluginWIndow, text="Installed")
	w.grid(row=0,column=0)
	
	w = Tkinter.Label(pluginWIndow, text="Available")
	w.grid(row=0,column=1)
	
	installedListbox = Tkinter.Listbox(pluginWIndow)
	installedListbox.grid(row=1,column=0,sticky=Tkinter.W+Tkinter.E+Tkinter.N+Tkinter.S)
	installedListbox.bind("<ButtonRelease-1>", installedMouseUp)
	
	availableListbox = Tkinter.Listbox(pluginWIndow)
	availableListbox.grid(row=1,column=1, sticky=Tkinter.W+Tkinter.E+Tkinter.N+Tkinter.S)
	availableListbox.bind("<ButtonRelease-1>", availableMouseUp)
	
	descriptionTextarea = Tkinter.Text (pluginWIndow,wrap=Tkinter.WORD)
	descriptionTextarea.grid(row=0,column=2,rowspan=3,columnspan=2, sticky=Tkinter.W+Tkinter.E+Tkinter.N+Tkinter.S)
	
	installButton = Tkinter.Button(pluginWIndow, text="Install/Update",state=Tkinter.DISABLED)
	installButton.grid(row=2,column=1)
	installButton.bind("<ButtonRelease-1>", installMouseUp)
	
	uninstallButton = Tkinter.Button(pluginWIndow, text="Uninstall",state=Tkinter.DISABLED)
	uninstallButton.grid(row=2,column=0)
	uninstallButton.bind("<ButtonRelease-1>", uninstallMouseUp)
	
	pluginWIndow.rowconfigure(1, weight=2)
	pluginWIndow.columnconfigure(2, weight=2)
	pluginWIndow.columnconfigure(3, weight=2)
	

	
	x=0
	for e in glob.g['installedPlugins']:
		p=e.split('.')
		if p[1]=='py' and p[0]!='omxgui' and p[0]!='glob':
			installedListbox.insert(Tkinter.END,p[0])
			x+=1
		
	pluginsData = requests.get('http://www.omxgui.com/plugins.php').json()
	for e in pluginsData:
		availableListbox.insert(Tkinter.END,e)

	
def availableMouseUp(event):
	global descriptionTextarea,selectedPlugin,active,installButton,uninstallButton
	active='install'
	installButton.config(state=Tkinter.NORMAL)
	uninstallButton.config(state=Tkinter.DISABLED)
	selected= event.widget.curselection()[0]
	selectedPlugin=event.widget.get(selected)
	pluginInfo = requests.get('http://www.omxgui.com/plugins.php?plugin={0}'.format(selectedPlugin)).json()
	descriptionTextarea.delete("1.0",Tkinter.END)
	descriptionTextarea.insert(Tkinter.END, pluginInfo)

def installedMouseUp(event):
	global selectedPlugin,active,installButton,uninstallButton
	active='uninstall'
	installButton.config(state=Tkinter.DISABLED)
	uninstallButton.config(state=Tkinter.NORMAL)
	selected= event.widget.curselection()[0]
	selectedPlugin=event.widget.get(selected)

def installMouseUp(event):
	global selectedPlugin,active
	print active
	if active=='install':
		pluginInstall = requests.get('http://www.omxgui.com/plugins.php?plugin={0}&install=simple'.format(selectedPlugin)).json()
		acciones=pluginInstall.split("|||")
		for accion in acciones:
			partes=accion.split('>>>')
			if partes[0]=='getput':
				testfile = urllib.URLopener()
				print partes[1]
				testfile.retrieve(partes[1], "/etc/omxguirpi{0}".format(partes[2]))
			
			if partes[0]=='mkdir':
				os.mkdir("/etc/omxguirpi{0}".format(partes[1]))
				
			elif partes[0]=='end':
				descriptionTextarea.delete("1.0",Tkinter.END)
				descriptionTextarea.insert(Tkinter.END, 'Plugin installed restart the application to update changes')

			
def uninstallMouseUp(event):
	global selectedPlugin,active
	print active
	if active=='uninstall':
		os.remove('/etc/omxguirpi/{0}.py'.format(selectedPlugin))
		if os.path.exists('/etc/omxguirpi/{0}'.format(selectedPlugin))==True:
			shutil.rmtree('/etc/omxguirpi/{0}'.format(selectedPlugin))
		descriptionTextarea.delete("1.0",Tkinter.END)
		descriptionTextarea.insert(Tkinter.END, 'Plugin uninstalled restart the application to update changes')
