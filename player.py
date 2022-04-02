'''

A Music Player built with Python, Tkinter, and pygame.
Built with the intent of discovering/rediscovering music within my own library.
Plays random songs from within whatever parent directory the user chooses.
Allows the user to compile a list of favorites which are stored via .txt and can be accessed later.
Currently only allows for playing .mp3 files due to pygame limitations

Built by Christopher Davis 2020

'''
from tkinter import *
from tkinter import filedialog
import pygame
import random
import os
import threading
from PIL import ImageTk,Image
from ctypes import windll

# Some WindowsOS styles, required for task bar integration
GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080

def get_default_folder():
	#we need to get the path of the folder where the music files are contained
	#look for the default_folder.txt, if it doesnt exist ask for the default folder 
	#then create the txt file containing it and return the given value
	#if it does exist read the value and return it
	default_path = ''
	if os.path.exists('default_folder.txt'):
		#read in the value 
		with open('default_folder.txt','r') as file:
			default_path = file.readline()
	else:
		#ask user to select their music folder
		default_path =  filedialog.askdirectory(title="Please Choose a Default Music Folder")
		with open('default_folder.txt','w') as file:
			file.write(default_path)
	return default_path

def select_default_folder():
	#ask user to select their music folder
	default_path =  filedialog.askdirectory(title="Please Choose a Default Music Folder")
	#make sure the file path is not empty
	if default_path == '':
		default_path = 'C:/'
	#update txt and set the file_path
	with open('default_folder.txt','w') as file:
		file.write(default_path)
	global file_path
	file_path = default_path
	init_folders()
	
def play_pressed():
	#depending of the current text of the play button either
	#play a song of pause/unpause the current one
	text = play_text.get()
	if now_playing_text.get() == '':
		play_text.set('Pause')
		next_song()
	else:
		if text == 'Play':
			mixer.unpause()
			play_text.set("Pause")

		if text == 'Pause':
			mixer.pause()
			play_text.set('Play')

def next_song():
	global current_path
	global fav_list
	global played_list

	if play_mode.get() == 'random':
		#select random folder
		folder_select = random.randrange(0,len(folders))
		#if there are folders within that folder make a list and select a 
		#random one of those until you are in a folder with no folders
		artist = folders[folder_select]
		artist_text.set(artist)
		path = file_path + '/' + artist
		avail_files = os.listdir(path)
		no_dirs = False

		while no_dirs == False:
			folder_list = []
			for i in avail_files:
				if os.path.isdir(path + '/' + i):
					folder_list.append(i)

			if len(folder_list) == 0:
				no_dirs = True
			else:
				new_path = random.randrange(0,len(folder_list))
				path = path + '/' + folder_list[new_path]
				avail_files = os.listdir(path)
			
		#select random .mp3, if none exist call next_song
		album = path.split('/').pop()
		album_text.set(album)
		songs = []
		imgs = []
		for i in os.listdir(path):
			if i[-4:] == '.mp3':
				songs.append(i)
			elif i[-4:] == '.jpg':
				imgs.append(i)

		#select random song
		try:
			rand_song = random.randrange(0,len(songs))
			mixer.stop()
			now_playing_text.set(songs[rand_song])
			current_path = path + '/' + songs[rand_song]
			mixer.load(current_path)
			mixer.play()
			mixer.set_endevent(42)#set event for when the song ends		
			pygame.event.clear()#clear the event cue to avoid infinite next songing
			#update visual stuff
			like_button.config(bg = black_2,fg = text_1)
			update_played_songs(artist,songs[rand_song])	
			select_album_art(imgs,path)
		except:
			#if something goes wrong output to the terminal then try again
			print('ERROR OF SOME SORT:')
			print(folders[folder_select])
			print('')
			next_song()

	#FAVORITE MODE
	if play_mode.get() == 'fav':
		#check if the fav list has len zero if so, shuffle played, copy into favs, clear played
		if len(fav_list) == 0:
			fav_list = played_list.copy()
			played_list = []
			random.shuffle(fav_list)

		#pop off fav list, play, put that in played list
		rand_song = fav_list.pop()
		#split up the shit by 'P**n'  path,artist,song,album
		components = rand_song.split('P**n')
		path,artist,song,album,art = components

		mixer.stop()
		now_playing_text.set(song)
		artist_text.set(artist)
		album_text.set(album)
		current_path = path
		mixer.load(current_path)
		mixer.play()
		mixer.set_endevent(42)#set evernt for when the song ends		
		pygame.event.clear()#clear the event cue to avoid infinite next songing
		#update visual stuff
		like_button.config(bg = black_2,fg = text_1)
		update_played_songs(artist,song)
		played_list.append(rand_song)
		#album art
		img = Image.open(art)	
		img = ImageTk.PhotoImage(img.resize((75,75),Image.ANTIALIAS))
		album_art.config(image = img)
		album_art.image  = img
	info_shrink()

def select_album_art(img_array,path):
	#takes in an array of availible jpgs, looks for one with a prefered name
	#sets album art. gets called in next song(when random) and play_song
	prefer = ['folder.jpg','cover.jpg']
	album_art_text.set(path + '/' + img_array[0])#initialize to default

	if len(img_array) > 0:

		for i in img_array:
			if i.lower() in prefer:
				album_art_text.set(path + '/' + i.lower())
		
	else:
		album_art_text.set("default.png")

	img = Image.open(album_art_text.get())	
	img = ImageTk.PhotoImage(img.resize((75,75),Image.ANTIALIAS))
	album_art.config(image = img)
	album_art.image  = img

def update_played_songs(artist,song):
	#updates the played songs area
	#takes 2 strings:artist and song title
	played_songs.config(state=NORMAL)

	if len(played_songs.get("1.0",END)) > 1:#if the thing is empty don't add a new line
		played_songs.insert(END,'\n')
	stop = played_songs.index(END)
	played_songs.insert(END,artist + '---' + song)
	played_songs.yview(END)#scroll text box all the way down
	start = float(stop) -1 
	#not 100% sure why this works, but you move the end to the end of the last line, not the next paragrah
	stop = stop + ' - 1 chars'

	if float(start)%2 == 0:
		played_songs.tag_add("tag_1",start,stop)#purple
	else:
		played_songs.tag_add("tag_2",start,stop)#green

	#disable editing once song has been added
	played_songs.config(state=DISABLED)

	#if the song that's just been played is in the liked list
	#highlight it
	for i in fav_list:
		if current_path in i:
			like_button.config(bg = text_1,fg = black_1)

def like_pressed():
		#write to likes.txt, only once though
		fav_val = current_path + 'P**n' + artist_text.get() + 'P**n' + now_playing_text.get() + 'P**n' + album_text.get() + 'P**n' + album_art_text.get()
		if like_button.cget('fg') != black_1:			
			likes = open('likes.txt',"a")
			#when reading back we need the artist,album,song,album art
			likes.write( fav_val+'\n')
			likes.close()
			like_button.config(bg = text_1,fg = black_1)
		#in this situation it is already in likes so we should remove it
		else:
			fav_list.remove(fav_val)
			#rewrite list to file, overwriting
			likes = open('likes.txt',"w")
			for i in fav_list:
				likes.write(i+'\n')
			likes.close()
			like_button.config(bg = black_2,fg = text_1)
		
def is_playing():
	#this is used so that when a song ends a new one begins
	global timer
	for i in pygame.event.get():
		if i.type == 42:
			next_song()

	timer = threading.Timer(1.0,is_playing)
	timer.start()

def select_folder():
	#lets the user change the current directory from which songs are selected
	global file_path
	try:
		tmp_path = filedialog.askdirectory()
		if tmp_path != '':
			file_path = tmp_path
			init_folders()
	except:
		pass
		
def init_folders():
	#gets a list of all the availible folders that can be looked in for songs to play
	global folders
	avail_files = os.listdir(file_path)
	folders = []
	for i in avail_files:
		if os.path.isdir(file_path+'/'+i):
			folders.append(i)

def play_mode_switch():
	global fav_list
	mode = play_mode.get()

	#put in FAVORITES mode
	if mode == 'random':
		file.menu.entryconfigure(1,label = "Play Random")
		play_mode.set('fav')
		#populate fav_list from favorites file
		likes = open('likes.txt')
		line = likes.readline().strip('\n')
		fav_list = []#clear fav_list
		while line != '':
			fav_list.append(line)
			line = likes.readline().strip('\n')
		#shuffle list
		random.shuffle(fav_list)
		likes.close()
	#put in RANDOM mode
	if mode == 'fav':
		file.menu.entryconfigure(1,label = "Play Favorites")
		play_mode.set('random')

def button_hover_on(button):
	#change the like/play/next song buttons when hovered
	if button != like_button:
		button.config(bg = black_3,activebackground = text_1)
	else:
		if button.cget('fg') == text_1:
			button.config(bg = black_3,activebackground = text_1)
		else:
			button.config(bg = 'darkorange',activebackground = text_1)

def button_hover_off(button):
	#change the like/play/next song buttons when hovered
	if button != like_button:
		button.config(bg = black_2)
	else:
		if button.cget('fg') == text_1:
			button.config(bg = black_2)
		else:
			button.config(bg = text_1,activebackground = text_1)

def info_shrink():
	#decreases the length of song/artist/album names so they fit nicely on screen
	#cuts off some of the data and we could add some sort of scroll functionality
	#but you can see the full thing sans the album name in the played songs window
	#so it's not so much of a big deal
	artist = artist_text.get()
	song = now_playing_text.get()
	album = album_text.get()
	max_len = 34
	
	if len(artist) > max_len:
		artist = artist[:max_len]
	if len(song) > max_len:
		song = song[:max_len]
	if len(album) > max_len:
		album = album[:max_len]

	artist_text.set(artist)
	now_playing_text.set(song)
	album_text.set(album)

def play_song(input_song):
	#allows the user to play a specific song, this is only really useful if you are wanting
	#to put something into your favorites list
	global current_path
	try:
		if input_song == '':
			current_path = filedialog.askopenfilename(filetypes = [("MP3","*mp3")])
		else:
			current_path = input_song
		#
		tmp_path = current_path.split('/')
		#remove the song name from the path
		path = current_path[:-1*(len(tmp_path[-1])+1)]
		path_array = current_path.split('/')

		song = path_array[-1]
		artist = path_array[-3]
		album = path_array[-2]

		imgs = []
		for i in os.listdir(path):
			if i[-4:] == '.jpg':
				imgs.append(i)

		select_album_art(imgs,path)

		mixer.stop()
		now_playing_text.set(song)
		artist_text.set(artist)
		album_text.set(album)
		mixer.load(current_path)
		mixer.play()
		mixer.set_endevent(42)#set event for when the song ends		
		pygame.event.clear()#clear the event cue to avoid infinite next songing
		#update visual stuff
		like_button.config(bg = black_2,fg = text_1)
		update_played_songs(artist,song)
	except:
		pass

def view_fav():
	#this opens a new topLevel window which displays a card for each song the user has favorited,
	#the user is able to either play the songs or remove them from the favorites list
	global fav_list
	#generate the fav list
	likes = open('likes.txt')
	line = likes.readline().strip('\n')
	fav_list = []#clear fav_list
	while line != '':
		fav_list.append(line)
		line = likes.readline().strip('\n')
	likes.close()

	#create a class for each fav
	class Fav:
		def __init__(self,components,black,fav_val):
			self.path,self.artist,self.song,self.album,self.art = components
			if len(self.album) > 45:
				self.album = self.album[:45]
			self.black = black
			self.fav_val = fav_val
			self.frame = Frame(top_frame,bg = self.black,width = 400,height = 75)
			self.frame.grid_propagate(0)
			img = Image.open(self.art)
			img = ImageTk.PhotoImage(img.resize((60,60),Image.ANTIALIAS))
			self.aa = Label(self.frame,image = img,bg = self.black)
			self.aa.grid(row = 0,column = 0,rowspan = 3,pady = 5,padx = 5)
			self.aa.image = img

			self.l1 = Label(self.frame, text = self.artist,bg = self.black,fg = text_1)
			self.l1.grid(row = 0,column = 1,sticky = W)
			self.l2 = Label(self.frame, text = self.song,bg = self.black,fg = text_1)
			self.l2.grid(row = 1,column = 1,sticky = W)
			self.l3 = Label(self.frame, text = self.album,bg = self.black,fg = text_1)
			self.l3.grid(row = 2,column = 1,sticky = W)

			self.play = Button(self.frame,text = 'Play',bg = self.black,fg = text_1,activebackground = text_1,activeforeground = black_1,command = self.play_push)
			self.play.grid(row = 0,column = 2,sticky = N+S+E+W,rowspan = 2)
			self.play.bind("<Enter>",lambda e: self.on_enter(self,self.play))
			self.play.bind("<Leave>",lambda e: self.on_leave(self,self.play))
			self.unlike = Button(self.frame,text = 'Unlike',bg = self.black,fg = text_1,activebackground = text_1,activeforeground = black_1,command = self.unlike_push)
			self.unlike.grid(row = 2,column = 2,sticky = E)
			self.unlike.bind("<Enter>",lambda e: self.on_enter(self,self.unlike))
			self.unlike.bind("<Leave>",lambda e: self.on_leave(self,self.unlike))

			self.frame.grid_columnconfigure(1,minsize = 280)
			self.frame.pack(fill = Y)

		#functions for hovering over the buttons
		def on_enter(event,self,button):
			if self.black == black_1:
				button.config(bg = black_2,activebackground = text_1)
			else:
				button.config(bg = black_1,activebackground = text_1)
		
		def on_leave(event,self,button):
			button.config(bg = self.black)


		def play_push(self):
			#we set the now playing text to "dummy song" because otherwise it will play something random at first
			#if this is the first thing we play
			now_playing_text.set('dummy song')
			play_pressed()
			play_song(self.path)

		def unlike_push(self):
			#change the background color of the like button
			like_button.config(bg = black_2,fg = text_1)
			#remove self.fav_val from fav list
			fav_list.remove(self.fav_val)
			#rewrite list to file, overwriting
			likes = open('likes.txt',"w")
			for i in fav_list:
				likes.write(i+'\n')
			#likes.write(current_path + 'P**n' + artist_text.get() + 'P**n' + now_playing_text.get() + 'P**n' + album_text.get() + 'P**n' + album_art_text.get() +'\n')
			likes.close()
			#destroy self
			self.frame.destroy()


	#create new window/populate with favs
	top = Toplevel()
	top.iconphoto(False,PhotoImage(file = "icon.png"))
	top.config(background = black_1)	
	top.geometry("420x400")
	top.title('Favorites')
	top_canvas = Canvas(top, height = 700,bg='black')
	top.bind("<MouseWheel>",lambda event:scroll_top(event, top_canvas))
	scroll_bar = Scrollbar(top,orient = 'vertical',command = top_canvas.yview)
	top_frame = Frame(top_canvas,bg = black_1)
	top_canvas.create_window((0,0),window = top_frame,anchor = N)
	top_canvas.configure(yscrollcommand = scroll_bar.set)
	scroll_bar.pack(side = RIGHT, fill = Y)
	top_canvas.pack(fill = BOTH)
	top.focus()
	top.update()
	top_frame.bind("<Configure>", lambda e: top_canvas.configure(scrollregion = top_canvas.bbox("all")))


	black = black_1
	for i in fav_list:
		Fav(i.split('P**n'),black,i)

		if black == black_1:
			black = black_2
		else: 
			black = black_1

		top.update()


	top.update_idletasks()
	top_canvas.yview_moveto(0.0)
	top_canvas.xview_moveto(0.0)

def scroll_top(event,top):
	top.yview_scroll(-int(event.delta/100),'units')

def exit_program():
	#closes the program only after canceling the time to prevent memory leaks
	global timer
	timer.cancel()
	root.destroy()

def setMouseLocation(e):
	#set the mouse position so the draggin looks nice and not jumpy
	global title_bar_mouse_location
	title_bar_mouse_location = (e.x,e.y)

def drag_app(e):
	#reposition the app when it's dragged, relative to where the mouse is
	#the mouse position will be set the titlebar is clicked on
	new_x = e.x_root-title_bar_mouse_location[0]
	new_y = e.y_root-title_bar_mouse_location[1]
	root.geometry(f'+{new_x}+{new_y}')

def hover(e,button,type):
	#change the exit button in the title bar when hovered
	if type == 'enter':
		button.config(bg=text_1,fg=black_1)
	elif type == 'exit':
		button.config(fg=text_1,bg=black_1)

def set_appwindow(mainWindow):
    # "Honestly forgot what most of this stuff does. I think it's so that you can see
    # the program in the task bar while using overridedirect. Most of it is taken
    # from a post I found on stackoverflow."
	#that in and of itself was taken from a post I found on stack overflow...
    hwnd = windll.user32.GetParent(mainWindow.winfo_id())
    stylew = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    stylew = stylew & ~WS_EX_TOOLWINDOW
    stylew = stylew | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, stylew)
    # re-assert the new window style
    mainWindow.wm_withdraw()
    mainWindow.after(10, lambda: mainWindow.wm_deiconify())

def frameMapped(event=None):
	global z
	root.overrideredirect(True)
	root.iconbitmap("icon.png")
	if z == 1:
		set_appwindow(root)
		z = 0

def minimizeGUI():
	global z
	root.state('withdrawn')
	root.overrideredirect(False)
	root.state('iconic')
	z = 1


#pygame mixer setup
pygame.init()
pygame.mixer.init()
current_song = 0
mixer = pygame.mixer.music
#volume automatically at 1
mixer.set_volume(.99)

#start timer for checking if a song is finished
timer = threading.Timer(1.0,is_playing)
timer.start()

#colors
black_1 = 'grey12'
black_2 = 'grey22'
black_3 = 'grey8'
text_1 = 'orange'
text_2 = 'mediumorchid2'
text_3 = 'lawn green'

#GUI setup
root = Tk()
root.wm_resizable(0,0)
root.title('A Music Player')
root.configure(background = black_1)
x_pos = int(root.winfo_screenwidth()/2 - 150)
y_pos = int(root.winfo_screenheight()/2 - 100)
root.geometry('300x235+{}+{}'.format(x_pos,y_pos))
root.pack_propagate(0)
root.protocol('WM_DELETE_WINDOW',exit_program)#when the X button is hit run the exit_program function to stop the timer and avoid memory issues

#we want to do a custom titlebar so it looks nicer.
#in order to do so we have to remove the one which is there and build our own
root.overrideredirect(True)
root.after(10,lambda: set_appwindow(root))
z = 1

title_bar = Frame(root,bg=black_1,relief='raised')
title_bar.pack(expand=1,fill=X)
title_bar.bind("<B1-Motion>", drag_app)
title_bar_mouse_location = (0,0)
title_bar.bind("<Button-1>",setMouseLocation)
#ICON
title_icon_image = ImageTk.PhotoImage(Image.open("icon.png").resize((16,16)))
title_icon = Label(title_bar,image = title_icon_image,bg=black_1)
title_icon.pack(side = LEFT,ipadx=0)
#TITLE
title_label = Label(title_bar,text = "A Music Player", bg = black_1, fg = text_1)
title_label.pack(padx = 5,pady=2,side=LEFT)
#Exit Buton
quit_button = Button(title_bar,text='X', bg = black_1, fg = text_1, border=0, command=exit_program)
quit_button.pack(ipadx = 5,side=RIGHT)
quit_button.bind("<Enter>",lambda e: hover(e,quit_button,'enter'))
quit_button.bind("<Leave>",lambda e: hover(e,quit_button,'exit'))
#Minimize Button
min_button = Button(title_bar,text='-', bg = black_1, fg = text_1, border=0, command=minimizeGUI)
min_button.pack(ipadx = 5, side=RIGHT)
min_button.bind("<Enter>",lambda e: hover(e,min_button,'enter'))
min_button.bind("<Leave>",lambda e: hover(e,min_button,'exit'))

play_mode = StringVar()
play_mode.set('random')

menu = Frame(root,bd = 1,bg = black_2)
menu.pack(fill = X)

file = Menubutton(menu,text = 'File',bg = black_2,fg = text_1,activebackground = text_1,activeforeground = black_1)
file.pack(side = LEFT)

file.menu = Menu(file,tearoff = 0,bg = black_2,fg = text_1,activebackground = text_1,activeforeground = black_1)
file["menu"] = file.menu

file.menu.add_command(label = "Choose Directory..", command = select_folder)
file.menu.add_command(label = "Choose Default Directory..", command = select_default_folder)
file.menu.add_command(label = "Play Favorites", command = play_mode_switch)
file.menu.add_command(label = "View Favorites", command = view_fav)
file.menu.add_command(label = "Play Song", command = lambda:play_song(''))
file.menu.add_command(label = "Exit",command = exit_program)

#-------------------
#info
info_container = Frame(root,height = 80,bg = black_1)
info_container.pack(fill = X)
info_container.grid_propagate(0)

text_container = Frame(info_container,width = 210,height = 80,bg = black_1)
text_container.grid(row = 0,column = 0,pady = (8,0))
text_container.pack_propagate(0)

artist_text = StringVar()
artist_label = Label(text_container,textvariable = artist_text,bg = black_1,fg = text_1)
artist_label.pack(anchor = W)

now_playing_text = StringVar()
now_playing = Label(text_container,textvariable = now_playing_text,bg = black_1,fg = text_1)
now_playing.pack(anchor = W)

album_text = StringVar()
album_label = Label(text_container,textvariable = album_text,bg = black_1,fg = text_1)
album_label.pack(anchor = W)

album_art_text = StringVar()
default_art = ImageTk.PhotoImage(Image.open("default.png"))
album_art = Label(info_container,bd = 2,relief = SUNKEN,image = default_art)
album_art.grid(row = 0, column = 1,sticky = E,padx =5)	
album_art_text.set("default.png")

#buttons---------------------
control_frame = Frame(root)
control_frame.pack()

like_button = Button(control_frame,text = "Like",command = like_pressed,fg = text_1,bg = black_2)
like_button.grid(row = 0, column = 0)
like_button.bind('<Enter>',lambda b:button_hover_on(like_button))
like_button.bind('<Leave>',lambda b:button_hover_off(like_button))

play_text = StringVar()
play = Button(control_frame,textvariable = play_text,command = play_pressed,fg = text_1,bg = black_2)
play.grid(row = 0,column = 2)
play_text.set("Play")
play.bind('<Enter>',lambda b:button_hover_on(play))
play.bind('<Leave>',lambda b:button_hover_off(play))

next_button = Button(control_frame,text = ">>",command = next_song,fg = text_1,bg = black_2)
next_button.grid(row = 0,column = 3)
next_button.bind('<Enter>',lambda b:button_hover_on(next_button))
next_button.bind('<Leave>',lambda b:button_hover_off(next_button))

#--------------------------
#songs we have heard
played_songs = Text(root,wrap=WORD,width = 47,height = 6,font = ('Helvetica',8),bg = black_2,bd = 0)
played_songs.pack(pady = 5)
played_songs.tag_configure("tag_1",foreground = text_2)
played_songs.tag_configure("tag_2",foreground = text_3)
played_songs.config(state=DISABLED)

#initialize a list of directories
file_path = get_default_folder()
current_path = ''#path of current song used for saving likes
init_folders()
fav_list = []
played_list = []#used to prevent repeating songs

root.bind("<Map>",frameMapped)
#start the program
root.mainloop()