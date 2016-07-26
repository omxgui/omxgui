
import glob,tkFileDialog,os,Tkinter,pexpect,dbus,time,re,os,getpass,sys

from xml.etree.ElementTree import parse, Element
from time import sleep
from Xlib import display
no=dbus.ObjectPath('/not/used')

glob.g['pxcontrol']=95
pxcontrol=glob.g['pxcontrol']
glob.g['seekTImeout']=-1
glob.g['transparent']=-1
glob.g['vol']=0
glob.g['omxState']=0
glob.g['dbusState']=0
glob.g['route']=''
glob.g['mousex']=0
glob.g['seek']=0
glob.g['onfull']=0

def run():
	
	createControls()
	glob.g['mainWindow'].bind("<Configure>", updateCall)
	if len(sys.argv)>1:
		glob.g['route']=sys.argv[1]
		loadFile(glob.g['route'])
		
	
def createControls():
	#buttons and sliders
	glob.g['frame']= Tkinter.Frame(glob.g['mainWindow'],background="black")
	
	glob.g['slSeek'] = Tkinter.Scale(glob.g['mainWindow'], from_=0, to=1000, orient=Tkinter.HORIZONTAL,width=16,showvalue=False)
	
	glob.g['imPlay'] = Tkinter.PhotoImage(file="/etc/omxguirpi/images/control.png")
	glob.g['btPlay'] = Tkinter.Button(glob.g['mainWindow'],image=glob.g['imPlay'],command=playpa,padx=4,pady=4)
	
	glob.g['imStop'] = Tkinter.PhotoImage(file="/etc/omxguirpi/images/control-stop-square.png")
	glob.g['btStop'] = Tkinter.Button(glob.g['mainWindow'],image=glob.g['imStop'],command=stop,padx=4,pady=4)
	
	glob.g['imFull'] = Tkinter.PhotoImage(file="/etc/omxguirpi/images/arrow-in-out.png")
	glob.g['btFull'] = Tkinter.Button(glob.g['mainWindow'],image=glob.g['imFull'],command=fullscreen,padx=4,pady=4)
	
	glob.g['slVol'] = Tkinter.Scale(glob.g['mainWindow'], from_=0, to=1,resolution=0.01, orient=Tkinter.HORIZONTAL,width=16,showvalue=False)
	
	#Context menu
	glob.g['context'] = Tkinter.Menu(glob.g['mainWindow'], tearoff=0)
	glob.g['context'].add_command(label="Open file", command=contextOpenFile)
	#glob.g['context'].add_command(label="Settings", command=generalSettings)
	glob.g['frame'].bind("<Button-3>", contextUp)
	glob.g['frame'].bind("<Button-1>", contextDown)


def getDbus():
	done=0
	retry=0
	while done==0:
		try:
			with open('/tmp/omxplayerdbus.{0}'.format(getpass.getuser()),'r+') as c:
				omxplayerdbus = c.read().strip()
				
			bus = dbus.bus.BusConnection(omxplayerdbus)
			object = bus.get_object('org.mpris.MediaPlayer2.omxplayer','/org/mpris/MediaPlayer2',introspect=False)
			glob.g['dbusProp'] = dbus.Interface(object,'org.freedesktop.DBus.Properties')
			glob.g['dbusPlayer']= dbus.Interface(object,'org.mpris.MediaPlayer2.Player')
			done=1
			glob.g['dbusState']=1
			glob.g['videoW']=glob.g['dbusProp'].ResWidth();		
			glob.g['videoH']=glob.g['dbusProp'].ResHeight();
			updateCall('force')
			glob.g['slVol'].set(xmlconf('vol'))
		except:
			retry+=1
			sleep(0.5)
			if retry >= 10:
				print retry
				raise SystemExit
def loadFile(route):
	cmd = "/usr/bin/omxplayer '{0}' --win '0 0 1 1'".format(glob.g['route'])
	glob.g['video']=pexpect.spawn(cmd)
	getDbus()

def contextOpenFile():
	glob.g['route']=tkFileDialog.askopenfilename(initialdir=xmlconf('lastFolder')).encode('utf-8')
	if glob.g['route']!='' and glob.g['route']!=():
		loadFile(glob.g['route'])
		xmlconf('lastFolder',os.path.dirname(glob.g['route']))
		glob.g['mainWindow'].title(os.path.basename(glob.g['route']))
def generalSettings():
	more = Tkinter.Toplevel()
	more.wm_title("Configuracion")
	
def contextUp(event):
	glob.g['context'].post(event.x_root, event.y_root)

def contextDown(event=None):
	glob.g['context'].unpost()
	
def playpa():
	if glob.g['dbusState']==1:
		glob.g['dbusPlayer'].PlayPause()	
	contextDown()
	updateCall('force')
def stop():
	if glob.g['dbusState']==1:
		glob.g['dbusPlayer'].Stop()
		glob.g['dbusState']=0
	contextDown()
	
def fullscreen():
	if glob.g['onfull']==0:
		glob.g['onfull']=1
		glob.g['mainWindow'].attributes("-fullscreen", True)
		
	else:
		glob.g['onfull']=0
		glob.g['mainWindow'].attributes("-fullscreen", False)	
	
	contextDown()

def updateCall(event):
	if event=='force' or event.widget==glob.g['mainWindow']:
		if event=='force':
			w=glob.g['mainWindowW']
			h=glob.g['mainWindowH']
			x=glob.g['mainWindowX']
			y=glob.g['mainWindowY']
		else:
			w=event.width
			h=event.height
			x=event.x
			y=event.y
			glob.g['mainWindowW']=w
			glob.g['mainWindowH']=h
			glob.g['mainWindowX']=x
			glob.g['mainWindowY']=y
			
		if glob.g['onfull']==0:
			pxcontrol=95	#space reserved for controls
			pxslide=0
		else:
			
			if glob.g['transparent']>0:
				pxslide=0
				pxcontrol=95
			else:
				pxslide=120	#avoid fullscreen control overlapping
				pxcontrol=0
		#resize buttons and sliders
		glob.g['frame'].place(x=0,y=0,width=w, height=h-pxcontrol)
		glob.g['slSeek'].place(x=10,y=h-80+pxslide,width=w-20,height=20)
		glob.g['btPlay'].place(x=10,y=h-50+pxslide,width=32,height=32)
		glob.g['btStop'].place(x=47,y=h-50+pxslide,width=32,height=32)
		glob.g['btFull'].place(x=w-42,y=h-50+pxslide,width=32,height=32)
		glob.g['slVol'].place(x=w-247,y=h-45+pxslide,width=200,height=20)
		
		if glob.g['dbusState']==1:
			#ressize omxvideo
			he=h-pxcontrol
			videoalto=int(glob.g['videoH']*w/glob.g['videoW'])
			videoancho=w
			sobran=(he-videoalto)/2
			sobral=0
			if videoalto>he:
				videoalto=he
				videoancho=int(glob.g['videoW']*he/glob.g['videoH'])
				sobran=0
				sobral=(w-videoancho)/2
			
			glob.g['dbusPlayer'].VideoPos(no,'{0} {1} {2} {3}'.format(x+sobral,y+sobran,x+videoancho+sobral,y+videoalto+sobran))
			
			
#xml getter/setter editable configurations
def xmlconf(attr,val=''):
	doc = parse(glob.g['confFile'])
	conf = doc.getroot()
	if val=='':
		target=conf.getchildren().index(conf.find(attr))
		return conf.find(attr).text	
	else:
		target=conf.getchildren().index(conf.find(attr))
		conf.remove(conf.find(attr))
		e = Element(attr)
		e.text = val
		conf.insert(target,e)
		doc.write(glob.g['confFile'], xml_declaration=True)
		
		

def loop():
	if glob.g['dbusState']==1:
		#mouse move transparency/timeout control
		data=display.Display().screen().root.query_pointer()
		
		if data.root_x <> glob.g['mousex']:							#if mouse position change
			glob.g['transparent']=4									#keep on transparent
			glob.g['mousex']=data.root_x
			glob.g['dbusPlayer'].SetAlpha(no,long(100))
			updateCall('force')
			
		if glob.g['transparent']>0:									#while keeping on transparent
			glob.g['transparent']-=1
			if glob.g['seek']<>glob.g['slSeek'].get():				#check if slider change
				glob.g['seekTImeout']=1								#and keep timeout
				
		elif glob.g['transparent']==0:								#transparency should gone do things
				glob.g['dbusPlayer'].SetAlpha(no,long(255))			
				updateCall('force')
				
				
					
		#sek control
		if glob.g['seekTImeout']==-1:																				#timeout -1 seek slider auto update
			val=int(glob.g['dbusProp'].Position()*1000/glob.g['dbusProp'].Duration())
			glob.g['slSeek'].set(val);
			glob.g['seek']=glob.g['slSeek'].get()
		elif glob.g['seekTImeout']==0:																				#timeout 0 seek to slider pos and return to minus
			glob.g['dbusPlayer'].SetPosition(no,long(glob.g['slSeek'].get()*glob.g['dbusProp'].Duration()/1000))
			glob.g['seekTImeout']=-1
		else:																										#timeout >0 wait
			glob.g['seekTImeout']-=1
			
		#volume control
		if glob.g['vol']<>glob.g['slVol'].get():
			glob.g['vol']=glob.g['slVol'].get()
			print glob.g['dbusProp'].Volume(glob.g['slVol'].get())
			xmlconf('vol',str(glob.g['slVol'].get()))
		#check movie end
		if glob.g['slSeek'].get()>=999:
			glob.g['dbusState']=0


