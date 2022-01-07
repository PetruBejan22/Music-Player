from tkinter import *
from PIL import ImageTk, Image
import os
import sys
from pygame import mixer
from tkinter import filedialog, messagebox
from mutagen.mp3 import MP3
import random
from datetime import datetime, timedelta
from getpass import getuser
import json
from webbrowser import open as webbrowser_open
import pyperclip
from threading import Thread
from tkinterdnd2 import *

from Packages.Info import About, Features, Patch_History, Shortcuts, Info
from Packages.Delete import Delete, Restore

# Sometimes gives an error with the files from program(icon etc) so this function help to get the file
def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception as e:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)

username = str(getuser())  # get users PC name

path_saved_playlist = f"C:/Users/{username}/Documents/Music Player/playlist.txt"  	# path to store songs paths
path_saved_config = f"C:/Users/{username}/Documents/Music Player/config.txt"   		# path to store config

if not os.path.exists(f"C:/Users/{username}/Documents/Music Player"):    			# create folder where to store info
	os.mkdir(f"C:/Users/{username}/Documents/Music Player")	

# Background names
background_images = ['Default', 'Wall', 'Nature', 'Space', 'Apocalypse', 'Star Wars', 'Rain', 'Desert']
images = []
images_path = './Images/'     # path where images are stored

def load_image(file):
	image = resource_path(images_path + file)
	image = ImageTk.PhotoImage(Image.open(image))
	images.append(image)
	return images[-1]


class MusicPlayer:
	def __init__(self, root):
		self.root = root
		mixer.init()

		self.window_height = self.root.winfo_height()	# window height
		self.music_playlist: list = []  				# playlist (full path)
		self.deleted_songs_playlist: list = []    		# list for deleted songs
		self.music_paused: bool = False  				# variable for music when is paused
		self.music_muted: bool = False  				# variable for music when is muted
		self.music_playing: bool = False  				# variable to check if the music is playing
		self.current_song_name: str = ''  				# get the current song name that is playing
		self.current_song_played_time: int = 0   		# seconds past when playing a song
		self.total_song_seconds: int = 1 				# song seconds
		self.volume_before_mute: int = 100   			# volume level before mute button was pressed
		self.variable_toggle_playback :str = 'off'		# variable for playback options
		self.focus_search :bool = False  				# variable when search bar has focus

	# import files
	def import_files(self):
		playlist = filedialog.askopenfilenames(filetypes=(("mp3", ".mp3"),))	# only 'mp3' files
		self.add_files(playlist)

	# import folder
	def import_folder(self):
		folder = filedialog.askdirectory()			# folder path

		if folder:
			folder_files = os.listdir(folder)		# folder files
			playlist = [os.path.join(folder, file) for file in folder_files]	# get files path
			self.add_files(playlist)

	# Add files to listboxes
	def add_files(self, playlist):
		first_song_index = self.listbox_playlist_music.size()				# get last song index from list				
		
		# add files to listboxes(number, name, length, playlist_list)
		for file in playlist:
			if os.path.exists(file):
				if os.path.splitext(file)[1] == '.mp3':
					filename = self.get_basename_song(file)  				# get song name without extension
					song_length_time = self.song_time_for_display(file) 	# get song length
					song_count = self.listbox_playlist_music.size()   		# last song number 

					self.listbox_length_music.insert(END, song_length_time) # insert length to the listbox			
					self.listbox_playlist_music.insert(END, " " + filename) # insert song name the listbox     
					self.listbox_number_music.insert(END, song_count + 1)   # insert the count song to the listbox
					self.music_playlist.append(file)						# add full path song to playlist

		# when importing a file(s)/folder, jump to the first item from imported songs
		self.listbox_playlist_music.see(first_song_index)
		self.listbox_number_music.see(first_song_index)
		self.listbox_length_music.see(first_song_index)

		self.listbox_playlist_music.select_clear(0, END)			
		self.listbox_playlist_music.selection_set(first_song_index)		# select first item from imported songs					

	# delete song from list
	def delete_song(self):
		delete_class = Delete(self.music_playlist, self.listbox_playlist_music, self.listbox_length_music, 
				   self.listbox_number_music, self.deleted_songs_playlist)
		delete_class.delete_song()
		
	# clear list
	def clear_list(self):
		delete_class = Delete(self.music_playlist, self.listbox_playlist_music, self.listbox_length_music, 
				   self.listbox_number_music, self.deleted_songs_playlist)
		delete_class.clear_list()	

	# Undo deleted songs
	def restore_deleted_song(self):
		restore_class = Restore(self.music_playlist, self.listbox_playlist_music, self.listbox_length_music, 
					self.listbox_number_music, self.deleted_songs_playlist)
		restore_class.restore_delete()
		self.change_foreground_song()	

	# move item in list
	def get_current_index(self, event):
		self.current_index = self.listbox_playlist_music.nearest(event.y)  # gets the current index of the clicked item in the listbox

	# shifts item up or down in listbox
	def shift_song(self, event):
		index = self.listbox_playlist_music.nearest(event.y)   # get index while you move the mouse

		if index != self.current_index:
			name = self.listbox_playlist_music.get(index)  	   # get listbox playlist name
			length = self.listbox_length_music.get(index)      # get listbox song length
			full_path = self.music_playlist.pop(index)         # remove item from playlist

			self.listbox_playlist_music.delete(index)          # delete previous
			self.listbox_length_music.delete(index)
			
			# Moves up
			if index < self.current_index:	
				self.listbox_playlist_music.insert(index + 1, name)
				self.listbox_length_music.insert(index + 1, length)
				self.music_playlist.insert(index + 1, full_path)

				self.listbox_playlist_music.selection_set(index + 1)
				
			# Moves down
			elif index > self.current_index:
				self.listbox_playlist_music.insert(index - 1, name)
				self.listbox_length_music.insert(index - 1, length)
				self.music_playlist.insert(index - 1, full_path)

				self.listbox_playlist_music.selection_set(index - 1)

			self.current_index = index

			self.change_foreground_song()		# change foreground	of the playing song

	# split text to only show the name of the song
	@staticmethod
	def get_basename_song(song_path):
		name_and_extension = os.path.basename(song_path)		# get only the filename and extension
		name = os.path.splitext(name_and_extension)[0]			# get only filename
		return name

	# change background of the playing current song and change song number on display
	def change_foreground_song(self, index_song=None):
		playlist = self.listbox_playlist_music.get(0, END)

		# if it was not provided a song index
		if not index_song:
			if self.current_song_name in playlist:
				index_song = playlist.index(self.current_song_name)
				
		listbox_size = self.listbox_playlist_music.size()

		# first make all foreground songs with color black
		if listbox_size:
			for nr in range(listbox_size):
				self.listbox_playlist_music.itemconfig(nr, fg="black")

		# check to see if the current playing song is still in playlist 
		if self.current_song_name in playlist:
			self.listbox_playlist_music.itemconfig(index_song, fg="white")

			# cancel move song on display and add new number 
			self.root.after_cancel(self.start_move_song_name_on_display)
			self.check_length_name(self.current_song_name, index_song+1)

	# clear current song from list and select and load song for playback
	def load_song(self, song_name):
		song_index_listbox = self.listbox_playlist_music.get(0, END).index(song_name)  			# get song index from listbox

		# search the song in playlist to get the full path
		for file in self.music_playlist:          
			if self.get_basename_song(file) == song_name.lstrip():    
				current_song_full_path = file     		
				break

		self.current_song_played_time = 0   	# reset timer
		self.current_song_name = song_name  	# song name

		# check if song was deleted from pc
		if os.path.exists(current_song_full_path):
			mixer.music.load(current_song_full_path)  											# load song to mixer.music
			mixer.music.play() 
			song_length = self.song_time_for_display(current_song_full_path) 		   			# get song length to display																					
			self.widgets_with_canvas.itemconfigure(self.display_song_length, text=song_length)	# display song length 
			self.total_song_seconds = self.get_song_length(current_song_full_path)				# get song length in seconds
			
			self.start_stop_functions(start_progressbar=True, start_playback_modes=True)		# restart progressbar and playback modes
			self.check_length_name(song_name, song_index_listbox+1)								# check to see if song name exced 60 characters
			self.change_foreground_song(song_index_listbox)										# change foreground of the playing song

		# delete the file from playlist if song was deleted or moved from initial imported directory
		else:
			messagebox.showerror('File not found', f'File missing: {self.current_song_name}')
			self.get_next_song()
			self.music_playlist.remove(current_song_full_path)
			self.listbox_playlist_music.delete(song_index_listbox)
			self.listbox_length_music.delete(song_index_listbox)
			self.listbox_number_music.delete(END)
			
	# check to see if name song is more than 60 characters
	def check_length_name(self, song_name, song_number):
		song_name = f'{song_number}.  {song_name}'	  # add song number in the beginning

		if len(song_name) > 60:				    
			self.move_song_name_on_display(song_name)
		else:
			self.widgets_with_canvas.itemconfigure(self.display_current_song, text=song_name)

	# move name from left to right and back if is bigger than 60 characters
	def move_song_name_on_display(self, song_name):
		global FIRST_CHAR, LAST_CHAR
		FIRST_CHAR = 0
		LAST_CHAR = 65
		song_display_name = f"      {song_name}      "

		def start_text():
			global FIRST_CHAR, LAST_CHAR
			song_text = song_display_name[FIRST_CHAR:LAST_CHAR]      			 			# add space front/end of the song and get only the first 45 characters
			self.widgets_with_canvas.itemconfigure(self.display_current_song, text=song_text)
			FIRST_CHAR += 1                           						     			# increase the starting and ending point
			LAST_CHAR += 1
			
			# check if the last character is at the end 					
			if LAST_CHAR > len(song_display_name):  	  
				FIRST_CHAR = 0  					  							 			# reset the starting and ending point
				LAST_CHAR = 65 

			self.start_move_song_name_on_display = self.root.after(500, start_text) 	 					  

		start_text()
		
	# start and stop functions (progress bar, playback mode and display name song)				
	def start_stop_functions(self, start_progressbar=False, start_playback_modes=False):
		self.root.after_cancel(self.start_move_progress_bar)	
		self.root.after_cancel(self.start_playback_modes)
		self.root.after_cancel(self.start_move_song_name_on_display)

		if start_progressbar:
			self.move_progress_bar()
		
		if self.variable_toggle_playback != 'off' and start_playback_modes:	
			self.playback_modes()

	# Change Play/Pause/Stop icons when music is on/off
	def change_icon_playback(self, play=False):
		if play:
			self.widgets_with_canvas.itemconfigure(self.play_button, image=load_image('pause.png'))
		else:
			self.widgets_with_canvas.itemconfigure(self.play_button, image=load_image('play.png'))

	def music_status(self, play=False, pause=False):
		self.music_playing = play
		self.music_paused = pause

	# play music
	def play_music(self, play_new_song=False):
		if self.music_playing and not play_new_song:
			self.pause_music()

		# unpause the music if it was paused	
		elif self.music_paused and not play_new_song:
			mixer.music.unpause()
			self.start_stop_functions(start_progressbar=True, start_playback_modes=True)
			self.music_status(play=True)	
			self.change_icon_playback(play=True)

		# play new song
		else:
			mixer.music.stop()
			index = self.listbox_playlist_music.curselection()      # get index from selected song in listbox

			# check if a song is selected
			if index:
				self.current_song_name = self.listbox_playlist_music.get(index[0])
				self.load_song(self.current_song_name)
				self.music_status(play=True)	
				self.change_icon_playback(play=True)

	# check to see if the buttons "repeat song", "repeat all" or "random" is selected
	def playback_modes(self):
		# check to see if exists any song in playlist and if toggle is not 'off'
		if self.music_playlist and self.variable_toggle_playback != 'off':
			# after the song finished playing
			if not mixer.music.get_busy() and self.music_playing:
				# repeat current song
				if self.variable_toggle_playback == 'repeat_song':
					self.load_song(self.current_song_name)

				# if "repeat_playlist" or "random" is selected	
				else:
					self.get_next_song()	

		self.start_playback_modes = self.root.after(1000, self.playback_modes)

	# pause music
	def pause_music(self):
		if mixer.music.get_busy():
			mixer.music.pause()
			self.start_stop_functions()				# stop progress bar and playback modes
			self.music_status(pause=True)
			self.change_icon_playback(play=False)

	# Get the next song
	def get_next_song(self):
		# select next song if exists any music in playlist
		if self.music_playlist:
			playlist = self.listbox_playlist_music.get(0, END)

			# select a random song from the list
			if self.variable_toggle_playback == 'random':
				index_next_song = random.randint(0, self.listbox_playlist_music.size() - 1) 	 # get a random number
				next_song = playlist[index_next_song]

			# play the next song
			if self.music_playing:
				if not self.variable_toggle_playback == 'random':
					# check to see if the current song is in playlist
					if self.current_song_name in playlist:
						index_current_song = playlist.index(self.current_song_name)
						next_song = playlist[(index_current_song + 1) % self.listbox_playlist_music.size()]
					else:
						next_song = playlist[0]	

				self.load_song(next_song)			

			# Just select the next song
			elif (index_current_song := self.listbox_playlist_music.curselection()):
				# if shuffle button is not pressed, select next song from list
				if not self.variable_toggle_playback == 'random':
					index_next_song = (index_current_song[0] + 1) % self.listbox_playlist_music.size()

				self.listbox_playlist_music.select_clear(0, END)  	
				self.listbox_playlist_music.selection_set(index_next_song)  			# select song in playlist	

	# Get the previous song
	def get_previous_song(self):
		# select previous song if exists any music in playlist
		if self.music_playlist:
			# Get the previous song if music is playing even if another song is selected
			if mixer.music.get_busy() and not self.music_paused:
				playlist = self.listbox_playlist_music.get(0, END)

				# check to see if the current song is in playlist
				if self.current_song_name in playlist:
					index_current_song = playlist.index(self.current_song_name)
					previous_song = playlist[(index_current_song - 1) % self.listbox_playlist_music.size()]
				else:
					previous_song = playlist[0]

				self.load_song(previous_song)

			# select previous song	
			elif (index_current_song := self.listbox_playlist_music.curselection()):
				index_previous_song = (index_current_song[0] - 1) % self.listbox_playlist_music.size()

				self.listbox_playlist_music.select_clear(0, END)  	
				self.listbox_playlist_music.selection_set(index_previous_song)  		# select song in playlist	

	# skip song 5 seconds forward
	def skip_forward(self, *args):
		self.listbox_playlist_music.xview_moveto(0)                     # (put name in listbox in the left side when pressing LEFT/RIGHT)
		self.current_song_played_time += 5
		if mixer.music.get_busy():
			mixer.music.set_pos(self.current_song_played_time)			# change mixer.music to new time

	# rewind song 5 seconds
	def skip_backward(self, *args):
		self.listbox_playlist_music.xview_moveto(0)						# (put name in listbox in the left side when pressing LEFT/RIGHT)
		self.current_song_played_time -= 5
		if mixer.music.get_busy():
			mixer.music.set_pos(self.current_song_played_time)			

	# set volume
	def change_volume(self, x=None):
		volume = self.variable_volume_level.get() / 100 	# get the volume level (0-100)
		mixer.music.set_volume(volume)  					# set the volume level (0-1)

		if volume > 0:	
			self.music_muted = False
		else:
			self.music_muted = True
			self.widgets_with_canvas.itemconfigure(self.mute_button, image=load_image('mute.png'))	

		# set different images if the volume level has different value
		if volume >= 0.70:
			self.widgets_with_canvas.itemconfigure(self.mute_button, image=load_image('sound3.png'))
		elif 0.35 <= volume < 0.70:
			self.widgets_with_canvas.itemconfigure(self.mute_button, image=load_image('sound2.png'))
		elif 0.01 <= volume < 0.35:
			self.widgets_with_canvas.itemconfigure(self.mute_button, image=load_image('sound1.png'))		

		# change percent volume level
		self.widgets_with_canvas.itemconfigure(self.volume_percent, text=f"{self.variable_volume_level.get()}%")		# percent text
		self.widgets_with_canvas.coords(self.volume_percent, 50 + self.variable_volume_level.get() * 1.44, 152)		# change display coordonates

		# change fill bar volume level
		self.volume_fill_canvas.place_configure(width=self.variable_volume_level.get() * 1.44)							   	

	# Volume down
	def volume_down(self):
		volume = self.variable_volume_level.get() - 10    
		self.volume_level_widget.set(volume)

	# Volume up
	def volume_up(self):
		volume = self.variable_volume_level.get() + 10
		self.volume_level_widget.set(volume)     
			
	# mute song
	def mute_music(self):
		# if mute is on, resume volume level from last known value (from volume level)
		if self.music_muted:
			mixer.music.set_volume(self.volume_before_mute / 100)
			self.volume_level_widget.set(self.volume_before_mute)
			self.music_muted = False
		else:  
			mixer.music.set_volume(0)
			self.volume_before_mute = self.variable_volume_level.get()     # store volume level 
			self.widgets_with_canvas.itemconfigure(self.mute_button, image=load_image('mute.png'))
			self.volume_level_widget.set(0)
			self.music_muted = True

	# get the length of the songs
	def get_song_length(self, song):	
		audio = MP3(song)
		song_seconds = audio.info.length

		return song_seconds	

	# convert seconds to hours/minutes/seconds
	def convert_seconds_to_h_m_s(self, song_seconds):
		song_seconds = round(song_seconds)		
		hours = song_seconds // 3600
		mins, secs = divmod(song_seconds - hours * 3600, 60)
		hours = str(song_seconds // 3600).zfill(2)
		mins, secs = str(mins).zfill(2), str(secs).zfill(2)

		return hours, mins, secs

	# time display format (ex.: 03:43)
	def song_time_for_display(self, song):
		song_seconds = self.get_song_length(song)
		hours, mins, secs = self.convert_seconds_to_h_m_s(song_seconds)

		# change view format of song length if it has more than 1 hour
		if int(hours) > 0:
			display_length_song = f'{hours}:{mins}:{secs}'
		else:
			display_length_song = f'{mins}:{secs}'

		return display_length_song

	# display current song time when music is playing
	def display_current_song_time(self, song_seconds):
		hours, mins, secs = self.convert_seconds_to_h_m_s(song_seconds)

		if self.total_song_seconds > 3600:  					# change the format view if the song has more than 1 hour
			time_format_label = f"{hours}:{mins}:{secs}"
		else:
			time_format_label = f"{mins}:{secs}"

		self.widgets_with_canvas.itemconfigure(self.display_played_song_time, text=f'{time_format_label}')

	# progress bar to show the current state of the playback
	def move_progress_bar(self):
		if mixer.music.get_busy() and self.music_playing:  						# if music is playing, the progress bar is moving
			self.current_song_played_time += 0.2
			self.display_current_song_time(self.current_song_played_time)  		# display seconds pasted
			
			progressbar_dot_coords = self.current_song_played_time * (450/self.total_song_seconds)
			if progressbar_dot_coords > 450:
				progressbar_dot_coords = 450    	# don't exced 450 pixels		
													
			self.widgets_with_canvas.coords(self.progress_bar_fill, 25, 50, progressbar_dot_coords+25, 58)
			self.widgets_with_canvas.coords(self.progress_bar_song_position, progressbar_dot_coords+25, 54)

		self.start_move_progress_bar = self.root.after(200, self.move_progress_bar)

		# cancel everything if the music stop playing
		if not mixer.music.get_busy() and self.variable_toggle_playback == 'off' and self.music_playing:
			self.start_stop_functions()
			self.music_status()
			self.change_icon_playback(play=False)				 
	
	# move progress bar to left click
	def move_progress_bar_to_click(self, event):
		new_coords = (event.x - 25) / (450 / self.total_song_seconds)	# get mouse coordonates and transfrom in seconds
		self.current_song_played_time = new_coords   					# update the timer

		max_length_fill = event.x if event.x < 450 else 450
		self.widgets_with_canvas.coords(self.progress_bar_fill, 25, 50, max_length_fill, 58)  	# change fill progress bar
		self.widgets_with_canvas.coords(self.progress_bar_song_position, max_length_fill, 54)	# change dot position

		if mixer.music.get_busy():
			mixer.music.rewind()  									# restart song and then set the new position in progress bar
			mixer.music.set_pos(new_coords) 						# set new position
													  
	# Change
	def toggle_repeat_playback(self, toggle_menu=False):
		self.root.after_cancel(self.start_playback_modes)

		# reset text info toggle to default
		self.text_info_toggle_playback.tag_config(f'{self.variable_toggle_playback}', font=('Halvetica', 9))

		# change toggle playback if it was changed in menu
		if toggle_menu:
			self.widgets_with_canvas.itemconfigure(self.toggle_button_playback, image=load_image(f'toggle_{toggle_menu}.png'))
			self.variable_toggle_playback = toggle_menu
		else:	
			toggle_options = ['off', 'repeat_song', 'repeat_playlist', 'random']				# all variables for toggle
			index_current_toggle = toggle_options.index(self.variable_toggle_playback)			# get index of the current toggle
			next_toggle = toggle_options[(index_current_toggle + 1) % 4]						# get index of the next toggle

			self.widgets_with_canvas.itemconfigure(self.toggle_button_playback, image=load_image(f'toggle_{next_toggle}.png'))
			self.variable_toggle_playback = next_toggle
			self.variable_menu_toggle_playback.set(next_toggle)

		if self.variable_toggle_playback != 'off' and self.music_playing:
			self.playback_modes()

		# set the current toggle option to bold
		self.text_info_toggle_playback.tag_config(f'{self.variable_toggle_playback}', font=('Halvetica', 9, 'bold', 'italic'))	

	def display_help_toggle_playback(self, event):
		self.text_info_toggle_playback.place(x=30+event.x, y=event.y-20)		
				
	# scroll together all 3 boxes by dragging the scrollbar with mouse
	def scroll_together_mouse_drag(self, *args):
		self.listbox_length_music.yview(*args)
		self.listbox_playlist_music.yview(*args)
		self.listbox_number_music.yview(*args)

	# scroll together all 3 list boxes with mouse wheel
	def scroll_together_mousewheel(self, event):
		self.listbox_length_music.yview("scroll", int(-1 * (event.delta / 120)), "units")
		self.listbox_playlist_music.yview("scroll", int(-1 * (event.delta / 120)), "units")
		self.listbox_number_music.yview("scroll", int(-1 * (event.delta / 120)), "units")
		return "break"
	
	# update widgets position when change the height of the program
	def update_widgets_position(self, event):
		self.window_height = self.root.winfo_height()
		self.frame_edit_listbox.place_configure(y=self.window_height - 26)
		self.frame_listbox.place_configure(height=self.window_height - 226)

		self.line_root_bottom.place_configure(y=self.window_height - 3)
		self.line_root_left.place_configure(height=self.window_height)
		self.line_root_right.place_configure(height=self.window_height)

	# move volume scale to left click
	def move_volume_scale_to_click(self, event):
		new_coord = (event.x -3) * 0.675
		self.volume_level_widget.set(new_coord)

	# display the time when click over progress bar
	def display_time_progress_bar_widget(self, event):
		seconds = (event.x - 25) / (450 / self.total_song_seconds)			# transform mouse position to seconds

		if seconds < 0:
			hours, mins, secs = ['00'] * 3
		else:
			hours, mins, secs = self.convert_seconds_to_h_m_s(seconds)
			
		# change the view format of length if it has more than 1 hour
		if float(hours) > 0:
			time_format = f'{hours}:{mins}:{secs}'
		else:
			time_format = f'{mins}:{secs}'

		self.widgets_with_canvas.itemconfigure(self.progress_bar_show_time, text=f'{time_format}', state='normal',)
		self.widgets_with_canvas.coords(self.progress_bar_show_time, event.x, 42)

	# Shortcuts key event
	def shortcut_key_event(self, event):
		if event.keysym == 'Delete':  						# Delete key (delete)
			self.delete_song()
		elif event.keysym == 'm' or event.keysym == 'M':  	# M key (mute)
			self.mute_music()
		elif event.keysym == 'Return':  					# Enter key (play)
			self.play_music(play_new_song=True)
		elif event.keysym == 'p' or event.keysym == 'P':  	# P key (pause)
			self.pause_music()
		elif event.keysym == 'Left':  						# Left arrow key (skip backward song)
			self.skip_backward()
		elif event.keysym == 'c' or event.keysym == 'C':  	# C key (clear)
			self.clear_list()
		elif event.keysym == 'b' or event.keysym == 'B':   	# B key (previous song)
			self.get_previous_song()
		elif event.keysym == 'n' or event.keycode == 'N':   # N key (next song) 
			self.get_next_song()       
		elif event.keysym == 'i' or event.keysym == 'I':   	# I key (show song info)
			self.song_info()
		elif event.keysym == 'l' or event.keysym == 'L':  	# L key (show playlist info)
			self.playlist_info()  

	# keyboard and mouse events
	def key_events(self):
		self.listbox_playlist_music.bind("<Key>", self.shortcut_key_event)
				
		# make pressed button effect (play/previous/next)
		self.widgets_with_canvas.tag_bind(self.play_button, '<Button-1>', lambda _:(self.play_music(), self.widgets_with_canvas.move('tag_play_button', 0, 3)))
		self.widgets_with_canvas.tag_bind(self.play_button, '<ButtonRelease-1>', lambda _:self.widgets_with_canvas.move('tag_play_button', 0, -3))

		self.widgets_with_canvas.tag_bind(self.previous_button, '<Button-1>', lambda _:(self.get_previous_song(), self.widgets_with_canvas.move('tag_previous_button', 0, 2)))
		self.widgets_with_canvas.tag_bind(self.previous_button, '<ButtonRelease-1>', lambda _:self.widgets_with_canvas.move('tag_previous_button', 0, -2))

		self.widgets_with_canvas.tag_bind(self.next_button, '<Button-1>', lambda _:(self.get_next_song(), self.widgets_with_canvas.move('tag_next_button', 0, 2)))
		self.widgets_with_canvas.tag_bind(self.next_button, '<ButtonRelease-1>', lambda _:self.widgets_with_canvas.move('tag_next_button', 0, -2))
		

		# Change image when cursor is over button (play, next, previous)
		self.widgets_with_canvas.tag_bind(self.play_button, '<Enter>', lambda _:self.change_image_on_focus(button=self.focus_button_play, state='normal'))
		self.widgets_with_canvas.tag_bind(self.play_button, '<Leave>', lambda _:self.change_image_on_focus(button=self.focus_button_play))

		self.widgets_with_canvas.tag_bind(self.previous_button, '<Enter>', lambda _:self.change_image_on_focus(button=self.focus_button_previous, state='normal'))
		self.widgets_with_canvas.tag_bind(self.previous_button, '<Leave>', lambda _:self.change_image_on_focus(button=self.focus_button_previous))

		self.widgets_with_canvas.tag_bind(self.next_button, '<Enter>', lambda _:self.change_image_on_focus(button=self.focus_button_next, state='normal'))
		self.widgets_with_canvas.tag_bind(self.next_button, '<Leave>', lambda _:self.change_image_on_focus(button=self.focus_button_next))

		# double click to play the music
		self.listbox_playlist_music.bind("<Double-Button-1>", lambda _:self.play_music(play_new_song=True))

		# Toggle playback display help
		self.widgets_with_canvas.tag_bind(self.toggle_button_playback, '<Motion>', self.display_help_toggle_playback)

		# Toggle playback
		self.widgets_with_canvas.tag_bind(self.toggle_button_playback, '<Button-1>', lambda x:self.widgets_with_canvas.move('tag_toggle_button', 0, 2))
		self.widgets_with_canvas.tag_bind(self.toggle_button_playback, '<ButtonRelease-1>', lambda _:(self.toggle_repeat_playback(), self.widgets_with_canvas.move('tag_toggle_button', 0, -2)))
		self.widgets_with_canvas.tag_bind(self.toggle_button_playback, '<Enter>', lambda _:self.change_image_on_focus(button=self.focus_button_toggle, state='normal'))
		self.widgets_with_canvas.tag_bind(self.toggle_button_playback, '<Leave>', lambda _:(self.change_image_on_focus(button=self.focus_button_toggle), self.text_info_toggle_playback.place_forget()))

		# Mute button
		self.widgets_with_canvas.tag_bind(self.mute_button, '<Button-1>', lambda x:self.widgets_with_canvas.move('tag_mute_button', 0, 2))
		self.widgets_with_canvas.tag_bind(self.mute_button, '<ButtonRelease-1>', lambda x:(self.mute_music(), self.widgets_with_canvas.move('tag_mute_button', 0, -2)))
		self.widgets_with_canvas.tag_bind(self.mute_button, '<Enter>', lambda _:self.change_image_on_focus(button=self.focus_button_mute, state='normal'))
		self.widgets_with_canvas.tag_bind(self.mute_button, '<Leave>', lambda _:self.change_image_on_focus(button=self.focus_button_mute))

		def change_search_variable_on_focus(focus='out'):
			if focus == 'in':
				if self.variable_search_playlist.get() == 'Search...':
					self.variable_search_playlist.set('')
					self.focus_search = True
			else:
				 if self.variable_search_playlist.get() == '':
				 	self.variable_search_playlist.set('Search...')	
				 	self.focus_search = False	

		# Entry placeholder 'Search...' in search bar		
		self.search_bar.bind('<FocusIn>', lambda _:change_search_variable_on_focus(focus='in'))
		self.search_bar.bind('<FocusOut>', lambda _:change_search_variable_on_focus())

		# Right click menu search bar
		self.search_bar.bind("<Button-3>", self.search_listbox_right_click_menu)

		# add/delete button pressed button effect
		self.add_button.bind("<Button-1>", lambda _: self.add_button.place_configure(y=2))
		self.add_button.bind("<ButtonRelease-1>", lambda  _: self.add_button.place_configure(y=1))
		self.delete_button.bind("<Button-1>", lambda _: self.delete_button.place_configure(y=2))
		self.delete_button.bind("<ButtonRelease-1>", lambda  _: self.delete_button.place_configure(y=1))

		# change image on focus for add/delete button
		self.add_button.bind('<Enter>', lambda _:self.add_button.config(image=load_image('plus_focus.png')))
		self.add_button.bind('<Leave>', lambda _:self.add_button.config(image=load_image('plus.png')))
		self.delete_button.bind('<Enter>', lambda _:self.delete_button.config(image=load_image('minus_focus.png')))
		self.delete_button.bind('<Leave>', lambda _:self.delete_button.config(image=load_image('minus.png')))

		# Right arrow to skip song forward
		self.root.bind('<Right>', self.skip_forward)     

		# listbox right click menu
		self.listbox_playlist_music.bind("<Button-3>", self.listbox_right_click_menu)

		# drag items from outside
		self.listbox_playlist_music.drop_target_register(DND_FILES)
		self.listbox_playlist_music.dnd_bind('<<Drop>>', self.drag_items_from_outside)

		# bind scroll of all three listboxes together to move at the same time with mouse wheel
		self.listbox_playlist_music.bind("<MouseWheel>", self.scroll_together_mousewheel)
		self.listbox_length_music.bind("<MouseWheel>", self.scroll_together_mousewheel)
		self.listbox_number_music.bind("<MouseWheel>", self.scroll_together_mousewheel)

		# Select a song if number of length was pressed
		self.listbox_number_music.bind("<ButtonRelease-1>", self.reselect_song_listbox)
		self.listbox_length_music.bind("<ButtonRelease-1>", self.reselect_song_listbox)

		# move items in list
		self.listbox_playlist_music.bind("<Button-1>", self.get_current_index)
		self.listbox_playlist_music.bind("<B1-Motion>", self.shift_song)

		# Ctrl-z to undo delete
		self.root.bind("<Control-z>", lambda _:self.restore_deleted_song())
		self.root.bind("<Control-Z>", lambda _:self.restore_deleted_song())

		# Ctrl+O to add files
		self.root.bind("<Control-o>", lambda _:self.import_files())
		self.root.bind("<Control-O>", lambda _:self.import_files())

		# Ctrl+F to add folder
		self.root.bind('<Control-f>', lambda _:self.import_folder())
		self.root.bind("<Control-F>", lambda _:self.import_folder())

		# move widgets when resize the main windows
		self.root.bind("<Configure>", self.update_widgets_position)

		# Move progress_bar_widget to left click
		self.widgets_with_canvas.tag_bind(self.progress_bar_song_position, '<Button-1>', self.move_progress_bar_to_click)
		self.widgets_with_canvas.tag_bind(self.progress_bar_song_position, '<B1-Motion>', self.move_progress_bar_to_click)
		self.widgets_with_canvas.tag_bind(self.progress_bar_fill, '<Button-1>', self.move_progress_bar_to_click)
		self.widgets_with_canvas.tag_bind(self.progress_bar_fill, '<B1-Motion>', self.move_progress_bar_to_click)
		self.widgets_with_canvas.tag_bind(self.progress_bar_line, '<Button-1>', self.move_progress_bar_to_click)
		self.widgets_with_canvas.tag_bind(self.progress_bar_line, '<B1-Motion>', self.move_progress_bar_to_click)


		# Display time song where mouse is above progress_bar_widget
		self.widgets_with_canvas.tag_bind(self.progress_bar_song_position, "<Motion>", self.display_time_progress_bar_widget)
		self.widgets_with_canvas.tag_bind(self.progress_bar_song_position, "<Leave>", lambda _:self.widgets_with_canvas.itemconfigure(self.progress_bar_show_time, state='hidden'))
		self.widgets_with_canvas.tag_bind(self.progress_bar_fill, "<Motion>", self.display_time_progress_bar_widget)
		self.widgets_with_canvas.tag_bind(self.progress_bar_fill, "<Leave>", lambda _:self.widgets_with_canvas.itemconfigure(self.progress_bar_show_time, state='hidden'))
		self.widgets_with_canvas.tag_bind(self.progress_bar_line, "<Motion>", self.display_time_progress_bar_widget)
		self.widgets_with_canvas.tag_bind(self.progress_bar_line, "<Leave>", lambda _:self.widgets_with_canvas.itemconfigure(self.progress_bar_show_time, state='hidden'))

		# move volume to left click
		self.volume_level_widget.bind("<Button-1>", self.move_volume_scale_to_click)
		self.volume_level_widget.bind("<B1-Motion>", self.move_volume_scale_to_click)
		self.volume_fill_canvas.bind("<Button-1>", self.move_volume_scale_to_click)
		self.volume_fill_canvas.bind("<B1-Motion>", self.move_volume_scale_to_click)		

	# Auto reselect song if number or song time is selected from listboxes
	def reselect_song_listbox(self, event):
		try:
			index = self.listbox_number_music.curselection()[0]  
		except:
			index = self.listbox_length_music.curselection()[0]
		finally:
			self.listbox_playlist_music.selection_set(index)    			 
		
	# sort list
	def sort_playlist(self, sort):
		# sort by name A-Z
		if sort == "sort_name_AZ":
			self.music_playlist.sort(key=lambda file:os.path.basename(file))

		# sort by name Z-A
		elif sort == "sort_name_ZA":
			self.music_playlist.sort(reverse=True, key=lambda file:os.path.basename(file))
		
		# sort by length A-Z
		if sort == "sort_length_AZ":
			self.music_playlist.sort(key=self.get_song_length)

		# sort by length Z-A
		elif sort == "sort_length_ZA":
			self.music_playlist.sort(reverse=True, key=self.get_song_length)

		# shuffle list        
		elif sort == 'shuffle':
			random.shuffle(self.music_playlist)        

		self.listbox_playlist_music.delete(0, END)  	# delete the listbox
		self.listbox_length_music.delete(0, END)  		
		self.listbox_number_music.delete(0, END)

		# add song name and length to playlists
		for number, file in enumerate(self.music_playlist, 1):  				
			self.listbox_playlist_music.insert(END, " " + self.get_basename_song(file))
			self.listbox_length_music.insert(END, self.song_time_for_display(file))
			self.listbox_number_music.insert(END, number)

		self.change_foreground_song()		# change foreground	of the playing song	

	# Show info song
	def song_info(self):
		index = self.listbox_playlist_music.curselection()

		# check to see if a song was selected
		if index:
			Info.song_info(index[0], self.listbox_playlist_music, self.music_playlist, self.listbox_length_music)	

	# show playlist total time and size
	def playlist_info(self):
		Info.playlist_info(self.music_playlist, self.get_song_length)

	# change background image
	def change_background_image(self, bg_image):
		if bg_image in background_images:		
			self.background_image_variable.set(bg_image)
			self.widgets_with_canvas.itemconfigure(self.background_image, image=load_image(f'background_image_{bg_image.lower()}.jpg'))

	# search songs in list
	def search_songs(self):
		search_input = self.variable_search_playlist.get()   		# get input from search

		# Do nothing if search input is empty or placeholder is there "Search..."
		if self.focus_search and not search_input == 'Search...':
			self.listbox_playlist_music.delete(0, END)
			self.listbox_number_music.delete(0, END)
			self.listbox_length_music.delete(0, END)

			song_number = 1
			for file in self.music_playlist:           
				if search_input.lower() in self.get_basename_song(file).lower():   
					self.listbox_number_music.insert(END, song_number)
					self.listbox_playlist_music.insert(END, " " + self.get_basename_song(file))
					self.listbox_length_music.insert(END, self.song_time_for_display(file))
					song_number += 1

			self.change_foreground_song()			# change foreground	of the playing song			        
	
	# right click menu for listbox       
	def listbox_right_click_menu(self, event):
		if self.listbox_playlist_music.size() > 0:
			index = self.listbox_playlist_music.nearest(event.y)
			self.listbox_playlist_music.select_clear(0, END)
			self.listbox_playlist_music.selection_set(index)

			richt_click_menu = Menu(self.root, tearoff = 0)
			richt_click_menu.add_command(label ="Move top", command=self.move_song_top)
			richt_click_menu.add_command(label ="Delete        Del", command=self.delete_song)
			richt_click_menu.add_command(label ="Info            I", command=self.song_info)
			
			# get cursor position
			try:
				richt_click_menu.tk_popup(event.x_root, event.y_root)
			finally:
				richt_click_menu.grab_release()

	# move selected song in first position
	def move_song_top(self):
		selected_song = self.listbox_playlist_music.curselection()[0]  		# get the index from the list of the current song
		song_delete_name = self.listbox_playlist_music.get(selected_song)   # get name of the song from list box
		song_delete_length = self.listbox_length_music.get(selected_song)   # get length of the song

		song = self.music_playlist.pop(selected_song)
		self.music_playlist.insert(0, song)

		self.listbox_length_music.delete(selected_song) 				 	# delete the length from the list box
		self.listbox_playlist_music.delete(selected_song)  					# delete the song from the list box
		
		self.listbox_playlist_music.insert(0, song_delete_name)
		self.listbox_length_music.insert(0, song_delete_length)

		self.listbox_playlist_music.selection_set(0)      

	# copy text from search bar 
	def copy_text(self):
		text = self.search_bar.selection_get()
		pyperclip.copy(text)

	# paste text into search bar
	def paste_text(self):								
		self.search_bar.select_to(0)				# get the cursor index position and paste text 
		text = self.search_bar.selection_get()		# get the text from begining to cursor
		text_length = len(text)

		self.search_bar.select_clear() 
		self.search_bar.insert(text_length, pyperclip.paste())   # paste text from the cursor position     

	# search box right click menu (Copy/Paste)
	def search_listbox_right_click_menu(self, event):
		search_menu = Menu(self.root, tearoff = 0)
		search_menu.add_command(label ="Copy             Ctrl+C", command=self.copy_text)
		search_menu.add_command(label ="Paste             Ctrl+V", command=self.paste_text)

		# get cursor position
		try:
			search_menu.tk_popup(event.x_root, event.y_root)
		finally:
			search_menu.grab_release()

	# change image if mouse is over button
	def change_image_on_focus(self, button=None, state='hidden'):
		self.widgets_with_canvas.itemconfigure(button, state=state)

	# drag items from outsite
	def drag_items_from_outside(self, event):
		'''
		If file has space beetwen characters, tkinterdnd2 will add '{' at beggining and '}' at the end
		If file has '{' or '}' and space in name , tkinterdnd2 will add '\' after every word
		If multiple items ar dragged in, the whole thing is a string
		'''
		dragged_files = event.data.replace('\\', '')			# delete special character from name '\'		 
		dragged_files = dragged_files.split()					# split string
		files_list = []
		index = 1
		for item in range(len(dragged_files)):
			file = ' '.join(dragged_files[:index]).strip('{}')	# remove '{' and '}' and group items from list until is a valid path
			if os.path.exists(file):
				files_list.append(file)
				dragged_files = dragged_files[index:]			# remove the valid path from dragged items and continue with next
				index = 1
			else:
				index += 1

		if files_list:
			self.add_files(files_list)							# check if files are 'mp3' format and add to playlist
		
	# widgets
	def music_player_widgets(self):
		self.widgets_with_canvas = Canvas(self.root)
		self.widgets_with_canvas.place(x=0, y=0, width=500, height=250)

		# background image
		self.background_image = self.widgets_with_canvas.create_image(250, 100, image=load_image('background_image_default.jpg'))

		#self.line = self.widgets_with_canvas.create_image(250, 148, image=load_image('line.png'))
		
		# Text display song name
		self.display_current_song = self.widgets_with_canvas.create_text(250, 27, text='Welcome', fill="#D6D6D6", font=("", 11, "bold"))

		# Text time song
		self.display_played_song_time = self.widgets_with_canvas.create_text(50, 91, text="--:--", fill="#D6D6D6", font=("", 15, "bold"))
		self.display_song_length = self.widgets_with_canvas.create_text(450, 91, text="--:--", fill="#D6D6D6", font=("", 15, "bold"))
		
		self.progress_bar_items()
		self.listboxes_widgets()
		self.volume_widgets()  
		self.toggle_playback_widget()
		self.display_info_toggle_playback()
		self.restore_config()	
		self.edit_listbox_widgets()
		self.search_widgets()
		self.playback_widgets()	
		self.key_events()
		self.create_contour_program()
		self.restore_playlist() 

	# Text to display info for toggle playback
	def display_info_toggle_playback(self):
		self.text_info_toggle_playback = Text(self.root, font=('Halvetica', 9), height=3, width=13)

		self.text_info_toggle_playback.insert(END, '-repeat song')
		self.text_info_toggle_playback.insert(END, '\n-repeat playlist')
		self.text_info_toggle_playback.insert(END, '\n-play random')

		self.text_info_toggle_playback.tag_add('repeat_song', '1.0', '1.30')
		self.text_info_toggle_playback.tag_add('repeat_playlist', '2.0', '2.30')
		self.text_info_toggle_playback.tag_add('random', '3.0', '3.30')	

	# progress bar when playing a song	
	def progress_bar_items(self):
		# Text to display time when above progress bar
		self.progress_bar_show_time = self.widgets_with_canvas.create_text(137, 42, text='', state='hidden', fill="#D6D6D6", font=("", 10, 'bold'))

		self.progress_bar_line = self.widgets_with_canvas.create_rectangle(25, 50, 475, 58, fill="#CACACA")
		self.progress_bar_fill = self.widgets_with_canvas.create_rectangle(25, 50, 25, 58, fill="#898989")
		self.progress_bar_song_position = self.widgets_with_canvas.create_image(25, 54, image=load_image('progress_bar_dot.png'))

		# variable to initiate: progress bar, playback modes and move text on display
		self.start_move_progress_bar = self.root.after(0, lambda:False)
		self.start_playback_modes = self.root.after(0, lambda:False)
		self.start_move_song_name_on_display = self.root.after(0, lambda:False)		 

	# Control listbox widgets
	def edit_listbox_widgets(self):    
		# frame for listboxes
		self.frame_edit_listbox = Frame(self.root, width=494, height=25, bg="#929292")
		self.frame_edit_listbox.place(x=3, y=700)

		self.add_button = Menubutton(self.frame_edit_listbox, direction='above', bd=0, bg="#929292", activebackground='#929292', image=load_image('plus.png'))
		self.add_button.place(x=4, y=1)

		self.add_button.menu = Menu(self.add_button, tearoff=0, activebackground='#929292')
		self.add_button['menu'] = self.add_button.menu
		self.add_button.menu.add_command(label='Add Files            Ctrl+O', command=lambda:self.import_files(), font=("", 10))
		self.add_button.menu.add_command(label='Add Folder          Ctrl+F', command=lambda:self.import_files(), font=("", 10))


		self.delete_button = Menubutton(self.frame_edit_listbox, direction='above', bd=0, bg="#929292", activebackground='#929292', image=load_image('minus.png'))
		self.delete_button.place(x=30, y=1)

		self.delete_button.menu = Menu(self.delete_button, tearoff=0, activebackground='#929292')
		self.delete_button['menu'] = self.delete_button.menu
		self.delete_button.menu.add_command(label='Delete song            Delete', command=self.delete_song, font=("", 10))
		self.delete_button.menu.add_command(label='Delete playlist         C', command=self.clear_list, font=("", 10))
		self.delete_button.menu.add_command(label='Undo delete            Ctrl+Z', command=self.restore_deleted_song, font=("", 10))

	# Search widgets
	def search_widgets(self):
		search_image = Label(self.frame_edit_listbox, bg="#D1D1D1", relief=FLAT, image=load_image('search.png'))
		search_image.place(x=121, y=1, width=22,height=21)

		# execute command every time something is changed in search bar
		self.variable_search_playlist = StringVar()
		self.variable_search_playlist.trace_add('write', lambda *args: self.search_songs())

		# search bar
		self.search_bar = Entry(self.frame_edit_listbox, font=("", 11,), relief=FLAT, bg="#D1D1D1", textvariable=self.variable_search_playlist)
		self.search_bar.place(x=143, y=1, width=350, height=21)	
		self.search_bar.insert(0, 'Search...')

	# Toggle Playback options
	def toggle_playback_widget(self):
		self.variable_toggle_playback = 'off'
		self.focus_button_toggle = self.widgets_with_canvas.create_image(23, 132, tag='tag_toggle_button', state='hidden', image=load_image('26x26_focus.png'))
		self.toggle_button_playback = self.widgets_with_canvas.create_image(23, 135, tag='tag_toggle_button', image=load_image('toggle_off.png'))

	# Playback widgets
	def playback_widgets(self):
		self.focus_button_play = self.widgets_with_canvas.create_image(360, 153, tag='tag_play_button', state='hidden', image=load_image('play_focus.png'))
		self.play_button = self.widgets_with_canvas.create_image(360, 158, tag='tag_play_button', image=load_image('play.png'))
		
		self.focus_button_previous = self.widgets_with_canvas.create_image(300, 155, tag='tag_previous_button', state='hidden', image=load_image('26x26_focus.png'))
		self.previous_button = self.widgets_with_canvas.create_image(300, 158, tag='tag_previous_button', image=load_image('previous.png'))

		self.focus_button_next = self.widgets_with_canvas.create_image(420, 155, tag='tag_next_button', state='hidden', image=load_image('26x26_focus.png'))
		self.next_button = self.widgets_with_canvas.create_image(420, 158, tag='tag_next_button', image=load_image('next.png'))	

	# Volume widget and images
	def volume_widgets(self):
		self.focus_button_mute = self.widgets_with_canvas.create_image(23, 166, tag='tag_mute_button', state='hidden', image=load_image('26x26_focus.png'))
		self.mute_button = self.widgets_with_canvas.create_image(23, 169, tag='tag_mute_button', image=load_image('sound3.png'))

		# volume level button
		self.variable_volume_level = IntVar()
		self.volume_level_widget = Scale(self.root, orient=HORIZONTAL, from_=0.0, to=100.0, length=150, command=self.change_volume, showvalue=0, repeatdelay=0,
								   activebackground="#929292", bg="#ADADAD", width=6, sliderlength=4,  variable=self.variable_volume_level, relief=FLAT, highlightthickness=0)
		self.volume_level_widget.place(x=43, y=162)
		self.volume_level_widget.set(100)

		self.volume_percent = self.widgets_with_canvas.create_text(43, 154, text=f'{self.variable_volume_level.get()}%', font=('', 10, 'bold'), fill="#C1E8FA")

		self.volume_fill_canvas = Canvas(self.root, bg="#929292", bd=0, relief=FLAT, highlightbackground="#929292")
		self.volume_fill_canvas.place(x=45, y=164, width=self.variable_volume_level.get() * 1.44, height=6)
		
	# Listboxes for playlist, length, number
	def listboxes_widgets(self):
		self.frame_listbox = Frame(self.root)
		self.frame_listbox.place(x=3, y=200, width=494, height=467)

		# scrollbar
		self.listbox_scrollbar_music = Scrollbar(self.frame_listbox, command=self.scroll_together_mouse_drag, width=21)
		self.listbox_scrollbar_music.pack(side=RIGHT, fill=Y)

		# listbox for counting songs
		self.listbox_number_music = Listbox(self.frame_listbox, bd=2, yscrollcommand=self.listbox_scrollbar_music.set, relief=SUNKEN, selectbackground="#878787",
									   selectforeground='black', font=("", 11), activestyle='none', justify=CENTER, bg="#929292", highlightthickness=0, width=4)
		self.listbox_number_music.pack(side=LEFT, fill=Y)

		# listbox for songs name
		self.listbox_playlist_music = Listbox(self.frame_listbox, bd=2, yscrollcommand=self.listbox_scrollbar_music.set, relief=SUNKEN, width=46,
									 font=("", 11), activestyle='none', selectforeground='black', bg="#ADADAD", selectbackground="#878787", highlightthickness=0)
		self.listbox_playlist_music.pack(side=LEFT, fill=Y)

		# listbox for songs length
		self.listbox_length_music = Listbox(self.frame_listbox, bd=2, justify=CENTER, relief=SUNKEN, font=("", 11), width=8, selectbackground="#878787",
										   selectforeground='black', yscrollcommand=self.listbox_scrollbar_music.set, activestyle="none", bg="#929292", highlightthickness=0)
		self.listbox_length_music.pack(side=RIGHT, fill=Y)	

	# Lines for program contour
	def create_contour_program(self):
		# Lines between widgets
		Label(self.root, relief=RAISED).place(x=2, y=110, width=496, height=2)  

		self.line_root_right = Label(self.root, relief=RAISED, bd=5)   # right line
		self.line_root_right.place(x=497, y=0, width=3, height=700)

		self.line_root_left = Label(self.root, relief=RAISED, bd=5)    # left line
		self.line_root_left.place(x=0, y=2, width=3, height=700)	

		self.line_root_bottom = Label(self.root, relief=RAISED, bd=5)  # bottom line
		self.line_root_bottom.place(x=0, y=697, width=500, height=3) 						

	# restore config after program started
	def restore_config(self):
		if os.path.exists(path_saved_config):
			with open(path_saved_config, "r") as config:
				try:
					last_config = json.load(config)
					self.root.geometry("500x{}".format(last_config.get("height", 700) + 20))  				# set the program height
					
					self.volume_level_widget.set(last_config.get("volume_level", 100))  					# set the volume level
					self.change_volume()																	# change volume image after getting new volume value
					
					self.toggle_repeat_playback(last_config['toggle_playback']) 
					self.variable_menu_toggle_playback.set(last_config['toggle_playback'])   				# restore saved playback option
					
					self.change_background_image(last_config.get('background', 'Default')) 					# set background image
					
				except Exception as error:
					print('Invalid config file: ', error)

	# restore playlist
	def restore_playlist(self):
		try:
			with open(path_saved_playlist, "r", encoding='utf8') as file:
				playlist = file.read()
				playlist = playlist.split('\n')
				self.add_files(playlist)
		except Exception as e:
			print('restore playlist: ', e)
					
	# save the playlist and config to a txt file
	def save_info(self):
		config = {}
		config["height"] = self.window_height  											# get window height
		config["volume_level"] = self.variable_volume_level.get()  						# get volume level
		config['toggle_playback'] = self.variable_toggle_playback						# get playback options
		config['background'] = self.background_image_variable.get()						# get background name image
		try:
			with open(path_saved_playlist, "w", encoding='utf8') as file:
				playlist = '\n'.join(self.music_playlist)
				file.writelines(playlist)

			with open(path_saved_config, "w") as file:
				json.dump(config, file)
		except Exception as e:
			print('Save_info error: ', e)
	
	# About page from menu	   
	def about_page(self):
		self.root_about = Toplevel(self.root)
		self.root_about.title('About')
		self.root_about.maxsize(250, 120)
		self.root_about.minsize(250, 120)
		self.root_about.iconphoto(False, load_image('musicplayer_image.png'))
		label_site = Label(self.root_about, text='petrubejan.epizy.com', justify=LEFT, cursor='hand2', font=("", 13, "bold", "italic", "underline"))
		label_site.pack(side=TOP)
		label_site.bind("<Button-1>", lambda _: webbrowser_open('petrubejan.epizy.com'))
					
		label_about = Label(self.root_about, text=About.about, anchor='w', justify=LEFT, pady=5, padx=25, font=('', 10))
		label_about.pack(fill='both', side=LEFT, expand=TRUE)

	# Menu
	def menu_music_player(self):
		menubar = Menu(self.root)
		menu_file = Menu(menubar, tearoff=0)

		# File
		menubar.add_cascade(label="File", menu=menu_file)
		menu_file.add_command(label='Add File(s)              Ctrl+O', command=lambda:self.import_files(), image=load_image('add_file.png'), compound=LEFT)
		menu_file.add_command(label='Add Folder             Ctrl+F', command=lambda:self.import_files(), image=load_image('add_folder.png'), compound=LEFT)
		menu_file.add_separator()
		menu_file.add_command(label='Exit                          Alt+F4', command=lambda:(self.save_info(), self.root.destroy()))

		# Edit
		menu_edit = Menu(menubar, tearoff=0)
		menu_edit.add_command(label='Delete song             Delete', image=load_image('delete_file.png'), command=self.delete_song, compound=LEFT)
		menu_edit.add_command(label='Delete playlist          C', image=load_image('delete_list.png'), command=self.clear_list, compound=LEFT)
		menu_edit.add_command(label='Undo delete            Ctrl+Z', image=load_image('undo.png'), command=self.restore_deleted_song, compound=LEFT)

		menubar.add_cascade(label='Edit', menu=menu_edit)

		# Edit-> Sort with 3 options: by name, length and shuffle
		menu_sort = Menu(menubar, tearoff=0)
		menu_sort_name = Menu(menubar, tearoff=0)
		menu_sort_length = Menu(menubar, tearoff=0)

		menu_edit.add_cascade(label="Sort", menu=menu_sort, image=load_image('sort.png'), compound=LEFT)
		menu_sort.add_cascade(label="by name:", menu=menu_sort_name, image=load_image('sort_AZ.png'), compound=LEFT)
		menu_sort.add_cascade(label="by length:", menu=menu_sort_length, image=load_image('sort_length1.png'), compound=LEFT)
		menu_sort.add_command(label="Shuffle", command=lambda:self.sort_playlist('shuffle'), image=load_image('shuffle.png'), compound=LEFT)

		# Edit-> Sort-> by name with 2 options: A-Z/Z-A
		menu_sort_name.add_command(label="A-Z", command=lambda:self.sort_playlist('sort_name_AZ'))
		menu_sort_name.add_separator()
		menu_sort_name.add_command(label="Z-A", command=lambda:self.sort_playlist('sort_name_ZA'))

		# Edit-> Sort-> by length with 2 options: ↓/↑
		menu_sort_length.add_command(command=lambda:self.sort_playlist('sort_length_ZA'), image=load_image('sort_length2.png'), compound=LEFT)
		menu_sort_length.add_separator()
		menu_sort_length.add_command(command=lambda:self.sort_playlist('sort_length_AZ'), image=load_image('sort_length1.png'), compound=LEFT)

		# Edit->Show file location
		menu_edit.add_separator()
		menu_edit.add_command(label="Song info                 I", command=self.song_info, image=load_image('info.png'), compound=LEFT)

		# Edit->Show playlist length and size
		menu_edit.add_command(label="Playlist info              L", command=self.playlist_info, image=load_image('info.png'), compound=LEFT)
		menu_edit.add_separator()

		# Edit->Background images
		menu_bg_images = Menu(menubar, tearoff=0)
		menu_edit.add_cascade(label="Background Images", menu=menu_bg_images)

		self.background_image_variable = StringVar()
		self.background_image_variable.set('Default')

		for image in background_images:
			menu_bg_images.add_checkbutton(label=f'{image}', command=lambda:self.change_background_image(self.background_image_variable.get()), variable=self.background_image_variable, onvalue=image, offvalue=image)

		# Play
		menu_play = Menu(menubar, tearoff=0)
		menu_play.add_command(label='Play                  Enter', command=lambda :self.play_music(play_new_song=True), image=load_image('play_menu.png'), compound=LEFT)
		menu_play.add_command(label='Pause               P', command=self.pause_music, image=load_image('pause_menu.png'), compound=LEFT)
		menu_play.add_command(label='Previous          B', command=self.get_previous_song, image=load_image('previous_menu.png'), compound=LEFT)
		menu_play.add_command(label='Next                 N', command=self.get_next_song, image=load_image('next_menu.png'), compound=LEFT)
		menu_play.add_separator()
		menu_play.add_command(label='Mute/Unmute              M', command=self.mute_music, image=load_image('mute_menu.png'), compound=LEFT)
		menu_play.add_command(label='Volume up', command=self.volume_up, image=load_image('increase_volume.png'), compound=LEFT)
		menu_play.add_command(label='Volume down', command=self.volume_down, image=load_image('decrease_volume.png'), compound=LEFT)
		menu_play.add_separator()
		menu_play.add_command(label='Back 5 sec             Left', command=self.skip_backward, image=load_image('skip_backward.png'), compound=LEFT)
		menu_play.add_command(label='Fwd 5 sec              Right', command=self.skip_forward, image=load_image('skip_forward.png'), compound=LEFT)
		menu_play.add_separator()

		self.variable_menu_toggle_playback = StringVar()
		menu_play.add_checkbutton(label='Repeat song', command=lambda:self.toggle_repeat_playback(self.variable_menu_toggle_playback.get()), variable=self.variable_menu_toggle_playback, onvalue="repeat_song", offvalue='off')
		menu_play.add_checkbutton(label='Repeat playlist', command=lambda:self.toggle_repeat_playback(self.variable_menu_toggle_playback.get()), variable=self.variable_menu_toggle_playback, onvalue="repeat_playlist", offvalue='off')
		menu_play.add_checkbutton(label='Play random', command=lambda:self.toggle_repeat_playback(self.variable_menu_toggle_playback.get()), variable=self.variable_menu_toggle_playback, onvalue="random", offvalue='off')

		menubar.add_cascade(label='Play', menu=menu_play)

		# Help
		menu_help = Menu(menubar, tearoff=0)

		menu_help.add_command(label="Shortcuts", command=lambda *_:messagebox.showinfo("Shortcuts", Shortcuts.shortcuts))
		menu_help.add_command(label="Features", command=lambda *_:messagebox.showinfo("Features", Features.features))
		menu_help.add_command(label="Patch History", command=lambda *_:messagebox.showinfo("Patch History", Patch_History.patch_history))
		menu_help.add_separator()
		menu_help.add_command(label="About", command=self.about_page, image=load_image('info.png'), compound=LEFT)

		menubar.add_cascade(label="Help", menu=menu_help)

		self.root.config(menu=menubar)

	# initiate tkinter 
	def main(self):
		self.root.title("Music Player")

		screen_width = root.winfo_screenwidth()		# get pc screen width

		self.root.geometry(f'500x700+{(screen_width-500)//2}+100')
		self.root.resizable(height=True, width=False)
		self.root.minsize(500, 500)
			
		self.root.iconphoto(False, load_image('musicplayer_image.png'))

		self.menu_music_player()
		self.music_player_widgets()	
		

# initialize Music Player
if __name__ == '__main__':
	root = Tk()
	music_player = MusicPlayer(root)
	music_player.main()
	root.mainloop()
	music_player.save_info()