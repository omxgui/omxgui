
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
glob.g['seeking']=-1
glob.g['onfull']=0
glob.g['filetype']='audio'
glob.g['videoDuration']=0
glob.g['playing']=0
glob.g['parcheDbus']=0
glob.g['playingMaster']='0010Main'

def run():
	
	createControls()
	glob.g['mainWindow'].bind("<Configure>", updateCall)
	#open file from command
	if len(sys.argv)>1:
		glob.g['route']=sys.argv[1]
		loadFile(glob.g['route'])	
	
def createControls():
	#buttons and sliders
	glob.g['mainFrame']= Tkinter.Frame(glob.g['mainWindow'],background="black")
	glob.g['seekFrame']= Tkinter.Frame(glob.g['mainWindow'])
	glob.g['buttonsFrame']= Tkinter.Frame(glob.g['mainWindow'])
	glob.g['volumeFrame']= Tkinter.Frame(glob.g['mainWindow'])
	
	glob.g['slSeek'] = Tkinter.Scale(glob.g['seekFrame'], from_=0, to=1000, orient=Tkinter.HORIZONTAL,width=16,showvalue=False)
	
	glob.g['imPlay'] = Tkinter.PhotoImage(file="/etc/omxguirpi/images/control.png")
	glob.g['btPlay'] = Tkinter.Button(glob.g['buttonsFrame'],image=glob.g['imPlay'],command=playpa,padx=4,pady=4,width=32,height=32)
	
	glob.g['imStop'] = Tkinter.PhotoImage(file="/etc/omxguirpi/images/control-stop-square.png")
	glob.g['btStop'] = Tkinter.Button(glob.g['buttonsFrame'],image=glob.g['imStop'],command=stop,padx=4,pady=4,width=32,height=32)
	
	glob.g['imFull'] = Tkinter.PhotoImage(file="/etc/omxguirpi/images/arrow-in-out.png")
	glob.g['btFull'] = Tkinter.Button(glob.g['volumeFrame'],image=glob.g['imFull'],command=fullscreen,padx=4,pady=4,width=32,height=32)
	
	glob.g['slVol'] = Tkinter.Scale(glob.g['volumeFrame'], from_=0, to=1,resolution=0.01, orient=Tkinter.HORIZONTAL,width=16,showvalue=False)
	
	#Context menu
	glob.g['context'] = Tkinter.Menu(glob.g['mainWindow'], tearoff=0)
	glob.g['context'].add_command(label="Open file", command=contextOpenFile)
	#glob.g['context'].add_command(label="Settings", command=generalSettings)
	glob.g['mainFrame'].bind("<Button-3>", contextUp)
	glob.g['mainFrame'].bind("<Button-1>", contextDown)
	
	glob.g['mainFrame'].place()
	glob.g['seekFrame'].place()
	glob.g['buttonsFrame'].place()
	glob.g['volumeFrame'].place()
	
	
	
	glob.g['slSeek'].pack(fill=Tkinter.X)
	glob.g['slSeek'].bind("<Button-1>", seekDown)
	glob.g['slSeek'].bind("<ButtonRelease-1>", seekUp)
	
	glob.g['btPlay'].pack(side=Tkinter.LEFT)
	glob.g['btStop'].pack(side=Tkinter.LEFT)
	
	glob.g['btFull'].pack(side=Tkinter.RIGHT)
	glob.g['slVol'].pack(side=Tkinter.RIGHT)


def getDbus():
	done=0
	retry=0
	while done==0:
		try:
			print 'trybus'
			with open('/tmp/omxplayerdbus.{0}'.format(getpass.getuser()),'r+') as c:
				omxplayerdbus = c.read().strip()
				
			bus = dbus.bus.BusConnection(omxplayerdbus)
			object = bus.get_object('org.mpris.MediaPlayer2.omxplayer','/org/mpris/MediaPlayer2',introspect=False)
			glob.g['dbusProp'] = dbus.Interface(object,'org.freedesktop.DBus.Properties')
			glob.g['dbusPlayer']= dbus.Interface(object,'org.mpris.MediaPlayer2.Player')
			
			
			if glob.g['filetype']=='video':
				glob.g['videoW']=glob.g['dbusProp'].ResWidth()	
				glob.g['videoH']=glob.g['dbusProp'].ResHeight()
			updateCall('force')
			glob.g['slVol'].set(xmlconf('vol'))
			glob.g['dbusProp'].Position()
			done=1
			glob.g['dbusState']=1
			glob.g['videoDuration']=glob.g['dbusProp'].Duration()
			print 'dbus up {0}'.format(glob.g['videoDuration'])
			glob.g['playing']=1
		except:
			retry+=1
			sleep(0.2)
			if retry >= 100:
				print 'dbus error'
				raise SystemExit
def loadFile(route,filetype='video'):
	glob.g['filetype']=filetype
	if filetype=='video':	
		cmd = "omxplayer '{0}' --win '0 0 1 1'".format(route)
		glob.g['btFull'].pack_forget()
		glob.g['btFull'].pack(side=Tkinter.RIGHT)
	else:
		glob.g['btFull'].pack_forget()
		cmd = 'omxplayer "{0}"'.format(route)
	print 'playing {0}'.format(cmd)
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
			#the force thing of bottom
			w=glob.g['mainWindowW']
			h=glob.g['mainWindowH']
			x=glob.g['mainWindowX']
			y=glob.g['mainWindowY']
		else:
			#get window size
			w=event.width
			h=event.height
			x=event.x
			y=event.y
			#store window sizes so we can 'force' without event
			glob.g['mainWindowW']=w
			glob.g['mainWindowH']=h
			glob.g['mainWindowX']=x
			glob.g['mainWindowY']=y
			
		if glob.g['onfull']==0:
			pxcontrol=60	#space reserved for controls							
			pxslide=0
		else:								
			
			if glob.g['transparent']>0:											
				pxslide=0
				pxcontrol=60
			else:
				pxslide=120	#avoid fullscreen control overlapping
				pxcontrol=0
		#resize frames
		glob.g['mainFrame'].place(x=0,y=0,width=w, height=h-pxcontrol)
		glob.g['seekFrame'].place(x=0,y=h-60+pxslide,width=w, height=40)
		glob.g['buttonsFrame'].place(x=0,y=h-40+pxslide, height=40)
		glob.g['volumeFrame'].place(x=w-glob.g['volumeFrame'].winfo_width(),y=h-40+pxslide, height=40)
		
		if glob.g['dbusState']==1 and glob.g['filetype']=='video':
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
			
			
#xml getter/setter persistent configurations
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
		
def seekDown(event):
	glob.g['seeking']=1	
	print 'seekno'
	
def seekUp(event):
	glob.g['seeking']=0	
	if glob.g['slSeek'].get()<999:
		glob.g['dbusPlayer'].SetPosition(no,long(glob.g['slSeek'].get()*glob.g['dbusProp'].Duration()/1000))#set ral position
	else:
		glob.g['slSeek'].set(998)
		#glob.g['dbusPlayer'].SetPosition(no,long(998*glob.g['dbusProp'].Duration()/1000))#set last position to make possible wait for end events
		#glob.g['dbusState']=0
	glob.g['seeking']=-1;


def loop():
	try:
		videopos=glob.g['dbusProp'].Position()
		glob.g['dbusState']=1
	except:
		glob.g['dbusState']=0
	
	if glob.g['videoDuration']==0:
		glob.g['dbusState']=0
		
	if glob.g['dbusState']==1 and glob.g['playing']==1:
		
		if videopos>0:
			if glob.g['seeking']==-1:
				val=int(videopos*1000/glob.g['videoDuration'])
				print val
				if val>=999:
					glob.g['dbusState']=0
					glob.g['playing']=0
					for elem in glob.m:
						try:
							glob.m[elem].onPlayEnds()
						except:
							a=0
				else:
					glob.g['slSeek'].set(val);
				
			
			#volume control
			newVolume=glob.g['slVol'].get()
			if glob.g['vol']<>newVolume:
				glob.g['vol']=newVolume
				glob.g['dbusProp'].Volume(newVolume)
				xmlconf('vol',str(newVolume))
			
	#mouse move transparency/timeout control
	data=display.Display().screen().root.query_pointer()
		
			

	if glob.g['filetype']=='video':
		if data.root_x <> glob.g['mousex']:							#if mouse position change
			glob.g['transparent']=4									#keep on transparent
			glob.g['mousex']=data.root_x
			updateCall('force')
			if glob.g['dbusState']==1 and glob.g['playing']==1:
				glob.g['dbusPlayer'].SetAlpha(no,long(100))
			
			
		if glob.g['transparent']>0:									#while keeping on transparent
			glob.g['transparent']-=1
					
	if glob.g['transparent']==0:								#transparency should gone do things
				
		updateCall('force')
		glob.g['transparent']=-1
		if glob.g['dbusState']==1 and glob.g['playing']==1:
			glob.g['dbusPlayer'].SetAlpha(no,long(255))		
		
			
				
				
			
			
		
		
	
 
