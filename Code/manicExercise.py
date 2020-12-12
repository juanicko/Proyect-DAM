from infi.systray import SysTrayIcon	
from tkinter import messagebox
from tkinter import ttk
import tkinter.font as tkFont
from tkcalendar import *
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
from PIL import ImageTk, Image
import sqlite3 
import datetime
import threading
from win32api import GetLastInputInfo
import time
import os
import winsound
import json
import random
import pandas as pd
import webbrowser


def connect():
	connection=sqlite3.connect("exercises.db")
	cursor=connection.cursor()
													
	try:
		cursor.execute('''
			CREATE TABLE  "EXERCISE_TYPE" (
			"exercise_id"	INTEGER,
			"name"	TEXT NOT NULL,
			"description"	TEXT,
			"active"	INTEGER DEFAULT 1,
			PRIMARY KEY("exercise_id" AUTOINCREMENT))
			''')
		cursor.execute('''
			CREATE TABLE  "EXERCISE" (
			"id"	INTEGER NOT NULL,
			"date"	TEXT NOT NULL,
			"repetitions"	INTEGER NOT NULL,
			"type"	INTEGER NOT NULL,
			FOREIGN KEY("type") REFERENCES "EXERCISE_TYPE"("exercise_id") ON DELETE CASCADE,
			PRIMARY KEY("id" AUTOINCREMENT))
			''')	
		print("Database ON")
		cursor.execute("INSERT INTO EXERCISE_TYPE VALUES(NULL,'Squats','Strengthen your lower body and core muscles. Best Option',1)")
		cursor.execute("INSERT INTO EXERCISE_TYPE VALUES(NULL,'PushUps','Protect Your Shoulders from Injury',1)")
		cursor.execute("INSERT INTO EXERCISE_TYPE VALUES(NULL,'PectoralStretch','Can help make it easier for you to maintain proper posture',1)")
		cursor.execute("INSERT INTO EXERCISE_TYPE VALUES(NULL,'JumpingJacks','Help Increase Stamina. Good for weight loss',1)")
		cursor.execute("INSERT INTO EXERCISE_TYPE VALUES(NULL,'HipThrust','Good for your lower back, core and glutes',1)")
	except sqlite3.OperationalError as e:
		print(e)
	finally:
		connection.commit()
		connection.close()

#Check the database exists everytime you open the app
connect()

#Root
root=Tk()
root.title("ManicExercise")
root.config(bg='#FFFFFF')
root.iconbitmap('icon.ico')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

styleRoot = ttk.Style()
styleRoot.configure('TFrame', background='#FFFFFF')
styleRoot.configure('T.TLabel', background='#FFFFFF',font=('Verdana',10,'bold'))
styleRoot.configure('Time.TLabel',font=('Verdana',25,'bold'),foreground="black",background='#FFFFFF')

########################MENU Options 
def exportJson():
	connection = sqlite3.connect("exercises.db")
	connection.row_factory = sqlite3.Row # This enables column access by name: row['column_name'] 
	db = connection.cursor()

	rows = db.execute('''SELECT e.date,e.repetitions,t.name FROM EXERCISE e JOIN EXERCISE_TYPE t ON e.type=t.exercise_id''').fetchall()
	connection.close()
	return json.dumps( [dict(x) for x in rows] )

def saveJson():
	file=filedialog.asksaveasfilename(title="Save",initialdir="",filetypes=(("JSON","*.json"),),defaultextension=".json")
	if file=="":
		return
	archivo_texto=open(file,"w")
	archivo_texto.write(exportJson())
	archivo_texto.close()
	messagebox.showinfo("Export","JSON exported correctly")


def saveExcel():
	file=filedialog.asksaveasfilename(title="Save",initialdir="",filetypes=(("Excel","*.xlsx"),),defaultextension=".xlsx")
	if file=="":
		return
	connection=sqlite3.connect("exercises.db")
	script='''SELECT e.date,e.repetitions,t.name FROM EXERCISE e JOIN EXERCISE_TYPE t ON e.type=t.exercise_id'''
	df = pd.read_sql_query(script, connection)
	connection.close()
	writer = pd.ExcelWriter(file)
	df.to_excel(writer, sheet_name='Exercises')
	writer.save()
	messagebox.showinfo("Export","Excel exported correctly")

def confirmExit():
	value=messagebox.askquestion("Confirmation","Do you really want to exit?")
	if value=="yes":
		os._exit(0)

settingsOpened=False
def settings():
	global settingsOpened
	if not settingsOpened:
		settingsOpened=True
		top=Toplevel(root)
		top.iconbitmap('icon.ico')
		
		def destroyTop():
			global settingsOpened
			settingsOpened=False
			top.destroy()

		def chosenConfiguration():	
			if checkMinimizeTray.instate(['selected']):
				read['minimizeTray']=True
			else:
				read['minimizeTray']=False
		
		def saveConfiguration():
			global settingsOpened
			activeSound=spActiveSound.get()
			stopTime=spStopTime.get()
			if activeSound.isdigit() and int(activeSound)>0:
				if stopTime.isdigit() and int(stopTime)>0:
					read['activeSound']=int(activeSound)
					read['inactiveStop']=int(stopTime)

			with open('preferences.json', 'w') as json_file:
				json.dump(read, json_file,indent=6)

			if read['minimizeTray']:
				checkRootProtocol()

			settingsOpened=False
			messagebox.showinfo("Changed correcly","You have to restart the app to see the changes")
			top.destroy()
		
		read = json.loads(open('preferences.json').read())

		checkMinimizeTray=ttk.Checkbutton(top,text="Minimize to tray",command=chosenConfiguration)
		checkMinimizeTray.grid(row=1,column=0,columnspan=4)
		checkMinimizeTray.state(['!alternate'])
		if read['minimizeTray']:
			checkMinimizeTray.state(['selected'])
		
		lbNotificate=Label(top,text="Notificate after")
		lbNotificate.grid(row=2,column=0)
		spActiveSound = ttk.Spinbox(top, from_= 20,to=120,state="readonly")
		spActiveSound.set(read['activeSound'])
		spActiveSound.grid(row=2,column=1)
		lbNotificate1=Label(top,text="mins")
		lbNotificate1.grid(row=2,column=2,sticky="w")
		
		lbStopTime=Label(top,text="Reset sedentary time after")
		lbStopTime.grid(row=3,column=0)
		spStopTime=ttk.Spinbox(top,from_=5,to=120,state="readonly")
		spStopTime.set(read['inactiveStop'])
		spStopTime.grid(row=3,column=1)
		lbStopTime=Label(top,text="mins AFK")
		lbStopTime.grid(row=3,column=2,sticky="w")
		
		botonGuardado=ttk.Button(top,text="Save",command=saveConfiguration)
		botonGuardado.grid(row=4,column=0,columnspan=4,pady=10)

		top.protocol("WM_DELETE_WINDOW",destroyTop)
		top.resizable(False, False)

def about():
	messagebox.showinfo("ManicExercise","    End of grade project DAM\n\n" +
							"Juan José Manuel Sánchez - 2020\r\n" +
							"Version 0.1  Creative Commons (CC)")

def addExercisesDatabase(name,description,window):
	name=name.title()
	name=name.replace(" ", "")

	tupla=(name,description,1)
	connection=sqlite3.connect("exercises.db")
	cursor=connection.cursor()												
	try:
		cursor.execute("INSERT INTO EXERCISE_TYPE VALUES(NULL,?,?,?)",tupla)
	except sqlite3.OperationalError as e:
		print(e)
	finally:
		connection.commit()
		connection.close()
	window.destroy()
	messagebox.showinfo("Exercise added","Exercise added correctly.\nYou have to restart the app to see the changes")



def addExercisesTop():
	top=Toplevel(root)

	lbAddNameExercise=ttk.Label(top,text="Name",style='T.TLabel')
	lbAddNameExercise.grid(row=0,column=0,pady=5,columnspan=2)
	addExerciseTopText=StringVar()
	addExerciseTop=ttk.Entry(top,textvariable=addExerciseTopText,width=30)
	addExerciseTop.grid(row=1,column=0,pady=10,padx=10)

	lbAddDescription=ttk.Label(top,text="Description",style='T.TLabel')
	lbAddDescription.grid(row=2,column=0,pady=5,columnspan=2)
	descriptionText=Text(top,width=30,height=10)
	descriptionText.grid(row=3,column=0)

	scrollVert=Scrollbar(top,command=descriptionText.yview)
	scrollVert.grid(row=3,column=1,sticky="nsew")
	descriptionText.config(yscrollcommand=scrollVert.set)

	btAddExerciseTop=ttk.Button(top,text="Add Exercise",command=lambda:addExercisesDatabase(addExerciseTopText.get(),descriptionText.get(1.0,END),top))
	btAddExerciseTop.grid(row=4,column=0,columnspan=2,pady=10)

	top.resizable(False, False)


def seeExercisesDatabase():
	connection=sqlite3.connect("exercises.db")
	cursor=connection.cursor()
	try:
		cursor.execute('''SELECT name,description,active FROM EXERCISE_TYPE ''')
		tasks=cursor.fetchall()
		return tasks
	except sqlite3.OperationalError as e:
		print(e)
	finally:
		connection.commit()
		connection.close()

	
def seeExercisesTop():
	top=Toplevel(root)
	ejercicios={}
	
	for i in seeExercisesDatabase():
		ejercicios[i[0]]=[{"description":i[1],"active":i[2]}]

	keys=[]
	for i in ejercicios.keys():
		keys.append(i)

	def changeDescription():
	    connection=sqlite3.connect("exercises.db")
	    cursor=connection.cursor()
	
	    try:
	        cursor.execute('''UPDATE EXERCISE_TYPE SET description=(?),active=(?)
	                         WHERE name=(?) ''',(descriptionTextSee.get(1.0,END),var.get(),comboBoxTop.get()))

	       	ejercicios[comboBoxTop.get()]=descriptionTextSee.get(1.0,END)
			

	    except sqlite3.OperationalError as e:
	        print(e)
	    finally:
	        connection.commit()
	        connection.close()
	    messagebox.showinfo("Changed correctly","You have to restart the app to see the changes")

	def changeExercise(*args):
		lst = ejercicios[comboBoxTop.get()]
		for dic in lst:
			if dic['active']:
				var.set(1)
			else:
				var.set(0)


			descriptionTextSee.delete(1.0,END)
			if dic['description']==None:
				descriptionTextSee.insert(1.0," ")
			else:
				descriptionTextSee.insert(1.0,dic['description'])

	

	comboBoxTop=ttk.Combobox(top,values=keys,state="readonly")
	comboBoxTop.set("Pick an exercise")
	comboBoxTop.grid(row=0,column=0,pady=5)
	comboBoxTop.bind("<<ComboboxSelected>>", changeExercise)

	var = BooleanVar()
	checkActive=ttk.Checkbutton(top,text="Exercise active",variable=var)
	checkActive.grid(row=1,column=0,pady=5)
	
	descriptionTextSee=Text(top,width=30,height=10)
	descriptionTextSee.grid(row=2,column=0,pady=5)

	scrollVert=Scrollbar(top,command=descriptionTextSee.yview)
	scrollVert.grid(row=2,column=1,sticky="nsew")
	descriptionTextSee.config(yscrollcommand=scrollVert.set)
	
	btChangeDescription=ttk.Button(top,text="Modify exercise",command=changeDescription)
	btChangeDescription.grid(row=3,column=0,columnspan=2)

	top.resizable(False, False)

	
def deleteExerciseTop():
	top=Toplevel(root)

	def deleteExercise():
		value=messagebox.askyesnocancel("Delete","You can modify it to not active.\nDo you want to delete this exercise and all its records?",icon='warning')
		if value:
			connection=sqlite3.connect("exercises.db")
			cursor=connection.cursor()
			try:
				cursor.execute("PRAGMA foreign_keys = ON")
				cursor.execute('''DELETE FROM EXERCISE_TYPE WHERE name=(?)''',(comboBoxTop.get(),))
			except sqlite3.OperationalError as e:
				print(e)
			finally:
				connection.commit()
				connection.close()
			messagebox.showinfo("Exercise deleted","Exercise deleted correctly. You have to restart the app to see the changes")
			top.destroy()
	ejercicios=[]
	for i in seeExercisesDatabase():
		ejercicios.append(i[0])

	comboBoxTop=ttk.Combobox(top,values=ejercicios,state="readonly")
	comboBoxTop.set("Pick an exercise")
	comboBoxTop.grid(row=0,column=0,pady=10)

	btDeleteExercise=ttk.Button(top,text="Delete exercise",command=deleteExercise)
	btDeleteExercise.grid(row=1,column=0,pady=5)

	top.resizable(False, False)


menu=Menu(root)
root.config(menu=menu, width=1,height=1)

FileMenu=Menu(menu,tearoff=0)
FileSubMenu=Menu(FileMenu,tearoff=0)
menu.add_cascade(label="File", menu=FileMenu)
FileSubMenu.add_command(label="To Excel",command=saveExcel)
FileSubMenu.add_command(label="To JSON",command=saveJson)

FileMenu.add_cascade(label="Export data..",menu=FileSubMenu)
FileMenu.add_separator()
FileMenu.add_command(label="Exit",command=confirmExit)

ExercisesMenu=Menu(menu,tearoff=0)
ExercisesMenu.add_command(label="Add Exercise",command=addExercisesTop)
ExercisesMenu.add_command(label="Modify Exercises",command=seeExercisesTop)
ExercisesMenu.add_command(label="Delete Exercise",command=deleteExerciseTop)
menu.add_cascade(label="Exercises",menu=ExercisesMenu)

OptionsMenu=Menu(menu,tearoff=0)
OptionsMenu.add_command(label="Settings",command=settings)
menu.add_cascade(label="Options",menu=OptionsMenu)

HelpMenu=Menu(menu,tearoff=0)
HelpMenu.add_command(label="GitHub",command=lambda:webbrowser.open('https://github.com/juanicko'))
HelpMenu.add_separator()
HelpMenu.add_command(label="About",command=about)
menu.add_cascade(label="Help",menu=HelpMenu)


##FRAMES

frameTopLeftHome=ttk.Frame(root)
frameTopLeftHome.grid(row=0,column=0)
frameTopLeftHome.columnconfigure(0, weight=1)
frameTopLeftHome.rowconfigure(0, weight=1)

frameTopLeftStats=ttk.Frame(root)


frameTopRight=ttk.Frame(root)
frameTopRight.grid(row=0,column=1)
frameTopRight.columnconfigure(0, weight=1)
frameTopRight.rowconfigure(0, weight=1)

frameMiddleLeft=ttk.Frame(root)
frameMiddleLeft.grid(row=1,column=0,rowspan=2)
frameMiddleLeft.columnconfigure(0, weight=1)
frameMiddleLeft.rowconfigure(0, weight=1)

frameMiddleRight=ttk.Frame(root)
frameMiddleRight.grid(row=1,column=1)
frameMiddleRight.columnconfigure(0, weight=1)
frameMiddleRight.rowconfigure(0, weight=1)

frameBottom=ttk.Frame(root)
frameBottom.grid(row=2,column=1)
frameBottom.columnconfigure(0, weight=1)
frameBottom.rowconfigure(0, weight=1)


actualDate=datetime.date.today()
actualDateFormat=actualDate.strftime("%A, %d %B %Y ")
dayCounting=0




fromDate=datetime.date.today()
toDate=datetime.date.today()
strFromDate=datetime.datetime.now()
strToDate=datetime.datetime.now()

statsFrameShown=False
#Check if the statsFrame is shown
def hideAndShowFrame():
	global statsFrameShown
	if not statsFrameShown:
		statsFrameShown=True
		frameTopLeftHome.grid_forget()
		frameTopLeftStats.grid(row=0,column=0)
		exerciseGraph('stats')
	else:
		statsFrameShown=False
		frameTopLeftStats.grid_forget()
		frameTopLeftHome.grid(row=0,column=0)
		exerciseGraph('home')


topDateOpened=False

def date_function(option):
	global topDateOpened

	if not topDateOpened:
		topDateOpened=True
		top=Toplevel(root)
		top.iconbitmap('icon.ico')

		def closeDateFunction():
			global topDateOpened
			topDateOpened=False
			top.destroy()
	
		def grab_date():
			global strFromDate,strToDate,topDateOpened
			global fromDate,toDate
	
			if option=='home':
				global actualDate, dayCounting
				actualDate=cal.get_date()
				strpActualDate=datetime.datetime.strptime(actualDate, '%Y-%m-%d')

				diffDay=datetime.datetime.today()-strpActualDate
				dayCounting=diffDay.days
				
				fechaPuestaText.set(strpActualDate.strftime("%A, %d %B %Y "))
				exerciseGraph('home')
	
			elif option=="from":
				fromDate=cal.get_date()
				strFromDate=datetime.datetime.strptime(fromDate, '%Y-%m-%d')
				if strFromDate>strToDate:
					fechaPuestaToText.set(strFromDate.strftime("%A, %d %B %Y "))
					toDate=cal.get_date()
	
				fechaPuestaFromText.set(strFromDate.strftime("%A, %d %B %Y "))

				exerciseGraph('stats')
				
	
			elif option=="to":
				toDate=cal.get_date()
				strToDate=datetime.datetime.strptime(toDate, '%Y-%m-%d')
				if strFromDate>strToDate:
					fechaPuestaFromText.set(strToDate.strftime("%A, %d %B %Y "))
					fromDate=cal.get_date()

				fechaPuestaToText.set(strToDate.strftime("%A, %d %B %Y "))

				exerciseGraph('stats')

			topDateOpened=False
			top.destroy()

		cal=Calendar(top,date_pattern='yyyy-mm-dd')
		cal.pack(pady=20)
	
		calButton=ttk.Button(top,text="Get Date",command=grab_date)
		calButton.pack(pady=20)

		top.protocol("WM_DELETE_WINDOW",closeDateFunction)

###Stats

calendarPhoto=ImageTk.PhotoImage(Image.open('calendar.png'))

lbDateStats=ttk.Label(frameTopLeftStats,text="Stats",style='T.TLabel')
lbDateStats.grid(row=0,column=0,padx=10,pady=10,columnspan=6,sticky="n")

btBackActual=ttk.Button(frameTopLeftStats,text="Home",command=hideAndShowFrame)
btBackActual.grid(row=2,column=0,pady=15,padx=10,ipadx=10,sticky="s",columnspan=6)

lbFrom=ttk.Label(frameTopLeftStats,text="From",style='T.TLabel')
lbFrom.grid(row=1,column=0,padx=10,pady=10)

fechaPuestaFromText=StringVar()
fechaPuestaFrom=ttk.Entry(frameTopLeftStats,textvariable=fechaPuestaFromText,width=30,state="readonly")
fechaPuestaFromText.set(actualDateFormat)
fechaPuestaFrom.grid(row=1,column=1,pady=10)

btnCalendarFrom=ttk.Button(frameTopLeftStats,image=calendarPhoto,command=lambda:date_function('from'))
btnCalendarFrom.grid(row=1,column=2,pady=10)


lbTo=ttk.Label(frameTopLeftStats,text="To",style='T.TLabel')
lbTo.grid(row=1,column=3,padx=10,pady=10)

fechaPuestaToText=StringVar()
fechaPuestaTo=ttk.Entry(frameTopLeftStats,textvariable=fechaPuestaToText,width=30,state="readonly")
fechaPuestaToText.set(actualDateFormat)
fechaPuestaTo.grid(row=1,column=4,pady=10)

btnCalendarTo=ttk.Button(frameTopLeftStats,image=calendarPhoto,command=lambda:date_function('to'))
btnCalendarTo.grid(row=1,column=5,pady=10)


###Home


btStats=ttk.Button(frameTopLeftHome,text="Stats",command=hideAndShowFrame)
btStats.grid(row=3,column=0,padx=10,pady=10,ipadx=10,sticky="s",columnspan=5)

lbDate=ttk.Label(frameTopLeftHome,text="Date",style='T.TLabel')
lbDate.grid(row=1,column=0,columnspan=5,pady=10,sticky="n")

fechaPuestaText=StringVar()
fechaPuesta=ttk.Entry(frameTopLeftHome,textvariable=fechaPuestaText,width=40,state="readonly")
fechaPuestaText.set(actualDateFormat)
fechaPuesta.grid(row=2,column=0,padx=10)
	


btnCalendar=ttk.Button(frameTopLeftHome,image=calendarPhoto,command=lambda:date_function('home'))
btnCalendar.grid(row=2,column=1)



def moveDate(option):
	global dayCounting,actualDate
	if option=="-":
		dayCounting+=1
	elif option=="+":
		dayCounting-=1

	selected=datetime.date.today()-datetime.timedelta(days=dayCounting)

	actualDate=selected
	exerciseGraph('home')

	selected=selected.strftime("%A, %d %B %Y ")
	fechaPuestaText.set(selected)

def selectedToday():
	global dayCounting,actualDate
	dayCounting=0

	selected=datetime.date.today()

	actualDate=selected
	exerciseGraph('home')

	selected=selected.strftime("%A, %d %B %Y ")
	fechaPuestaText.set(selected)

btnBefore=ttk.Button(frameTopLeftHome,text="<",command=lambda:moveDate("-"))
btnBefore.grid(row=2,column=2)


btnAfter=ttk.Button(frameTopLeftHome,text=">",command=lambda:moveDate("+"))
btnAfter.grid(row=2,column=3)

btnToday=ttk.Button(frameTopLeftHome,text="Today",command=selectedToday)
btnToday.grid(row=2,column=4)


		
def getMinimizeTray():
	read = json.loads(open('preferences.json').read())
	return read['minimizeTray']

def inactiveStop():
	read = json.loads(open('preferences.json').read())
	return read['inactiveStop']
def activeSound():
	read = json.loads(open('preferences.json').read())
	return read['activeSound']

totalHours=0
totalMinutes=0
totalSeconds=0

activeHours=0
activeMinutes=0
activeSeconds=0

exitFlag=False
disableFollow=False

inactiveReset=inactiveStop()
makeSound=activeSound()


def tiempo():
	global totalSeconds,totalMinutes,totalHours
	global activeSeconds,activeMinutes,activeHours
	global inactiveReset,makeSound


	last_input = GetLastInputInfo()
	last_active = time.time()

	isPaused=False
	while True:
		time.sleep(1)
		
		if GetLastInputInfo() == last_input:
			notActive=time.time()-last_active
			
			if int(notActive)//60==inactiveReset:
				isPaused=True
				resetTime()
				#print('Not active for {} seconds.'.format(notActive))

		else:
			last_input = GetLastInputInfo()
			last_active = time.time()
			#print('Active!')
			isPaused=False


		if not isPaused:
			#Count all the time the app is ON
			totalSeconds+=1
			
			if totalSeconds>59:
				totalMinutes+=1
				totalSeconds=0
				if totalMinutes>59:
					totalHours+=1
					totalMinutes=0
			#strTotalSeconds="%02d"%totalSeconds
			strTotalMinutes="%02d"%totalMinutes
			strTotalHour="%02d"%totalHours

			#Count all the time until you do a exercise

			activeSeconds+=1

			if activeSeconds>59:
				activeMinutes+=1
				activeSeconds=0
				if activeMinutes>59:
					activeHours+=1
					activeMinutes=0

			#strActiveSeconds="%02d"%activeSeconds
			strActiveMinutes="%02d"%activeMinutes
			strActiveHour="%02d"%activeHours

			if activeMinutes==makeSound and activeSeconds==0:
				threading.Thread(target=playSound).start()
				print("You must move")

			global exitFlag
			if not exitFlag:
				lbTiempoTotal.config(text="{}:{}".format(strTotalHour,strTotalMinutes))
				lbTiempoActivo.config(text="{}:{}".format(strActiveHour,strActiveMinutes))

def resetTime():
	global activeSeconds,activeMinutes,activeHours
	activeHours=0
	activeMinutes=0
	activeSeconds=0
def playSound():
	winsound.PlaySound("*", winsound.SND_ALIAS)


timerTime=threading.Thread(target=tiempo).start()

##Time counting

lbTime=ttk.Label(frameTopRight,text="Total time",style='T.TLabel')
lbTime.grid(row=0,column=0)
lbTiempoTotal=ttk.Label(frameTopRight,text="00:00",style='Time.TLabel')
lbTiempoTotal.grid(row=1,column=0,padx=30)

lbTime=ttk.Label(frameTopRight,text="Sedentary time",style='T.TLabel')
lbTime.grid(row=0,column=1)
lbTiempoActivo=ttk.Label(frameTopRight,text="00:00",style='Time.TLabel')
lbTiempoActivo.grid(row=1,column=1,padx=30)




##Treeview
my_tree=ttk.Treeview(frameBottom,selectmode="browse")

tree_scroll=Scrollbar(frameBottom,command=my_tree.yview)
tree_scroll.grid(row=1,column=1,sticky="nsew")
my_tree.config(yscrollcommand=tree_scroll.set)

my_tree['columns']=("Time","Repetitions","Exercise")

#Formate our columns
my_tree.column("#0",width=0,stretch=NO)
my_tree.column("Time",anchor=W)
my_tree.column("Repetitions",anchor=CENTER)
my_tree.column("Exercise",anchor=W)

#Create headings

my_tree.heading("#0",text="Label",anchor=W)
my_tree.heading("Time",text="Time",anchor=W)
my_tree.heading("Repetitions",text="Repetitions",anchor=CENTER)
my_tree.heading("Exercise",text="Exercise",anchor=W)

my_tree.grid(row=1,column=0)



def removeOne(*args):
	global actualDate
	global statsFrameShown
	
	selected=my_tree.focus()
	values=my_tree.item(selected,'values')
	selectedDate=str(actualDate)+" "+values[0]

	dateValue=values[0]
	repetitionsValue=values[1]
	nameValue=values[2]

	value=messagebox.askyesnocancel("Delete","Do you want to delete this record?",icon='warning') 

	if value:
		x=my_tree.selection()[0]
		my_tree.delete(x)
		if not statsFrameShown:
			try:
				connection=sqlite3.connect("exercises.db")
		
				cursor=connection.cursor()
				cursor.execute('''DELETE FROM EXERCISE WHERE date==(?)''',(selectedDate,))
			except sqlite3.OperationalError as e:
				print(e)
			finally:
				connection.commit()
				connection.close()
	
			exerciseGraph('home')
		else:
			try:
				connection=sqlite3.connect("exercises.db")
		
				cursor=connection.cursor()
				cursor.execute('''DELETE FROM EXERCISE 
								WHERE date IN(SELECT e.date FROM EXERCISE e
								JOIN EXERCISE_TYPE t ON e.type=t.exercise_id
								WHERE date(e.date) = (?) AND name=(?))''',(dateValue,nameValue))
			except sqlite3.OperationalError as e:
				print(e)
			finally:
				connection.commit()
				connection.close()
			exerciseGraph('stats')
		btDeleteTree["state"]="disabled"

	
my_tree.bind("<Delete>",removeOne)

btDeleteTree=ttk.Button(frameBottom,text="Delete selected",command=removeOne)
btDeleteTree.grid(row=0,column=0)
btDeleteTree["state"] = "disabled"

def treeSelected(*args):
	selected=my_tree.focus()
	values=my_tree.item(selected,'values')
	if values!="":
		btDeleteTree["state"] = "enable"
	else:
		btDeleteTree["state"]="disabled"


my_tree.bind("<Button-1>",treeSelected)





def readRegistry():
	global statsFrameShown
	if not statsFrameShown:
		for record in my_tree.get_children():
			my_tree.delete(record)
		connection=sqlite3.connect("exercises.db")
		cursor=connection.cursor()
		try:
			cursor.execute('''SELECT time(date),repetitions,name FROM EXERCISE e
						  	  JOIN EXERCISE_TYPE t ON e.type=t.exercise_id
						 	  WHERE date(date)==(?) and active=1''',(actualDate,))
			tasks=cursor.fetchall()
		except sqlite3.OperationalError as e:
			print(e)
		finally:
			connection.commit()
			connection.close()
		count=0
		for record in tasks:
			my_tree.insert(parent='', index='end',iid=count,values=record)
			count+=1
	else:
		for record in my_tree.get_children():
			my_tree.delete(record)
		connection=sqlite3.connect("exercises.db")
		cursor=connection.cursor()
		try:
			cursor.execute('''SELECT date(date),sum(repetitions),name FROM EXERCISE e
						  	  JOIN EXERCISE_TYPE t ON e.type=t.exercise_id
						 	  WHERE date(date) BETWEEN (?) AND (?) and active=1
						 	  GROUP BY date(e.date),name''',(fromDate,toDate))
			tasks=cursor.fetchall()
		except sqlite3.OperationalError as e:
			print(e)
		finally:
			connection.commit()
			connection.close()
		count=0
		for record in tasks:
			my_tree.insert(parent='', index='end',iid=count,values=record)
			count+=1



		
####################ExerciseGRAPH 

fig=plt.figure(figsize=(7,5),dpi=75)
plt.ion()
canvas=FigureCanvasTkAgg(fig,frameMiddleLeft)
canvas.get_tk_widget().grid(row=0,column=0)
def exerciseGraph(option):
	if option=='home':
		readRegistry()



		data=pd.read_sql_query('''SELECT sum(repetitions) as total,name 
								  FROM EXERCISE e 
								  JOIN EXERCISE_TYPE t ON e.type=t.exercise_id
								  WHERE date(e.date)==(?) and active=1
								  GROUP BY name''', sqlite3.connect("exercises.db"),params=(actualDate,))
	elif option=='stats':
		readRegistry()
		data=pd.read_sql_query('''SELECT sum(repetitions) as total,name 
								  FROM EXERCISE e 
								  JOIN EXERCISE_TYPE t ON e.type=t.exercise_id
								  WHERE date(e.date) BETWEEN (?) AND (?) and active=1
								  GROUP BY name''', sqlite3.connect("exercises.db"),params=(fromDate,toDate))

	names=[]
	repetitions=[]
	
	for name in data.name:
		names.append(name)
	
	for repetition in data.total:
		repetitions.append(repetition)

	plt.clf()
	plt.bar(names,repetitions)


selectedToday()


def getAllExercises():
	connection=sqlite3.connect("exercises.db")
	cursor=connection.cursor()

	try:
		cursor.execute("SELECT name FROM EXERCISE_TYPE WHERE active=1")
		varios=cursor.fetchall()
		return varios
	except sqlite3.OperationalError as e:
		print(e)
	finally:
		connection.commit()
		connection.close()



comboBox=ttk.Combobox(frameMiddleRight,values=getAllExercises(),state="readonly")
comboBox.set("Pick an exercise")
comboBox.grid(row=0,column=0,padx=30)

spNumberExerciseRoot = ttk.Spinbox(frameMiddleRight, from_= 1,to=300,state="readonly")
spNumberExerciseRoot.set(5)
spNumberExerciseRoot.grid(row=0,column=1,padx=30)

btAddExercise=ttk.Button(frameMiddleRight,text="Add",command=lambda:numberDetect(spNumberExerciseRoot,comboBox.get(),root))
btAddExercise.grid(row=0,column=2,padx=30)

def numberDetect(spNumber,typeExercise,window):
	number=spNumber.get()
	if number.isdigit() and int(number)>0 and typeExercise!='Pick an exercise':

		connection=sqlite3.connect("exercises.db")
		cursor=connection.cursor()
	
		try:
			cursor.execute("SELECT exercise_id FROM EXERCISE_TYPE WHERE name=(?) ",(typeExercise,))
			tipo=cursor.fetchone()
			tipo=int(tipo[0])
	
			tupla=(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),number,tipo)
	
			cursor.execute("INSERT INTO EXERCISE VALUES(NULL,?,?,?)",tupla)
		except sqlite3.OperationalError as e:
				print(e)
		finally:
			connection.commit()
			connection.close()
	
		if str(type(window))=="<class 'tkinter.Toplevel'>":
			window.destroy()
		else:
			global statsFrameShown
			if not statsFrameShown:
				exerciseGraph('home')
			else:
				exerciseGraph('stats')
		resetTime()

	else:
		if not number.isdigit() and not int(number)>0:
			messagebox.showwarning("Warning","Enter a number greater than zero")
			spNumber.set(5)
		else:
			messagebox.showwarning("Warning","Select a exercise")

##Systray options

def randomExercise(systray):
	top=Toplevel(root)
	top.iconbitmap('icon.ico')

	allExercises=getAllExercises()
	rand=random.randint(0, len(allExercises)-1)

	lbExercise=ttk.Label(top,text=allExercises[rand],style='T.TLabel')
	lbExercise.grid(row=0,column=0,pady=10,padx=20)

	spNumberExercise = ttk.Spinbox(top, from_= 1,to=300,state="readonly")
	spNumberExercise.set(random.randint(1, 20))
	spNumberExercise.grid(row=1,column=0,pady=5,padx=20)
	
	btAddRandExercise=ttk.Button(top,text="Add repetitions",command=lambda:numberDetect(spNumberExercise,lbExercise.cget("text"),top))
	btAddRandExercise.grid(row=2,column=0,pady=5,padx=20)

	top.resizable(False, False)


def addExercise(systray):
	top=Toplevel(root)
	top.iconbitmap('icon.ico')

	cbExercises=ttk.Combobox(top,values=getAllExercises(),state="readonly")
	cbExercises.set("Pick an exercise")
	cbExercises.grid(row=0,column=0,pady=5,padx=20)

	spNumberExercise = ttk.Spinbox(top, from_= 1,to=300,state="readonly")
	spNumberExercise.set(random.randint(1, 20))
	spNumberExercise.grid(row=1,column=0,pady=5,padx=20)

	btAddExerciseSystray=ttk.Button(top,text="Add repetitions",command=lambda:numberDetect(spNumberExercise,cbExercises.get(),top))
	btAddExerciseSystray.grid(row=2,column=0,pady=10,padx=20)

	top.resizable(False, False)

	
def openWindow(systray):
	global exitFlag
	root.deiconify()
	exitFlag=False
	if not statsFrameShown:
		exerciseGraph('home')
	else:
		exerciseGraph('stats')


minimizedWindow=True

def on_closing():
	global exitFlag
	global minimizedWindow
	exitFlag=True
	root.withdraw()

	def exitProgram(systray):
		root.destroy()
		os._exit(0)

	if minimizedWindow:
		minimizedWindow=False
		menu_options = (("Open",None,openWindow),("Random Exercise",None,randomExercise),("Add Exercise", None, addExercise),)
		systray = SysTrayIcon("icon.ico", "ManicExercise", menu_options,default_menu_index=0,on_quit=exitProgram)
		systray.start()


def checkRootProtocol():
	if getMinimizeTray():
		root.protocol("WM_DELETE_WINDOW", on_closing)
	else:
		root.protocol("WM_DELETE_WINDOW", confirmExit)

checkRootProtocol()


root.resizable(False, False)
root.mainloop()