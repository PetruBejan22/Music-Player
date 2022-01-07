import os
from tkinter import messagebox
import time

class About:
	creator = 'Petru Bejan'
	version = '4.7'
	version_date = '03-12-2021'
	initial_release_date = '22-05-2020'

	about = f'''
Created by: {creator}
Version: {version}
Date: {version_date}
Initial release: {initial_release_date}'''       


class Features:
	features = '''
The program only supports "mp3" format
*** Options for playback:
	-repeat the current song
	-repeat all songs
	-random songs from the list
*** Progress bar when playing a song
*** Buttons for:
	-add files
	-add a folder
	-delete a song
	-clear the entire list
	-undo the previous deleted song/list
*** Search bar
*** Mute button and a bar to change the volume
*** Can shift up/down a song in list
*** Time elapse when playing a song
*** Shortcuts for most functions
*** Themes (background image)
*** Option to sort by:
	-name
	-length
	-shuffle
*** Show song info(size, path, date created etc)
*** Show playlist info
*** Auto save/load when exit/start program:
	-music list
	-window height
	-volume level
	-repeat song/all and shuffle checkbox'''


class Patch_History:
	patch_history = '''
Patch 4.7 (03-12-2021)
***New:
	- Drag songs from outside to playlist in Music Player

Patch 4.6 (16-11-2021)
***New:
	- UI Design
***Removed:
	- Stop Button
	- Option to check for updates	

Patch 4.5 (01-10-2021)	
***New:
	- Option to check for updates
	- Display time(tooltip) when you move mouse over progress bar
	- Background images (Nature, Apocalypse, Space, Star Wars etc...)
	- New style for volume level and progress bar
	- Change icon (play/stop/pause) when is active/inactive

Patch 4.4 (08-09-2021)
***Adjust:
	- Can restore the deleted songs after you clear de list
***Fixed:
	- Not showing About page

Patch 4.3 (15-07-2021)
***New:
	   -right click commands:-copy, paste, info song, delete song, move song to top

Patch 4.2 (01-12-2020)
***New:
	   -webpage
	   -search bar
	   -new commands in menu tab
	   -icons in menu tab and for buttons
	   -theme select'''


class Shortcuts:
	shortcuts = '''
<Enter> - play
<S> - stop
<P> - pause
<M> - mute
<B> - previous song
<N> - next song
<Right> - forward song 5 sec
<Left> - back song 5 sec
<Delete> - delete song
<C> - clear list
<Ctrl+Z> - undo delete
<Ctrl+O> - add file(s)
<Ctrl+F> - add folder
<I> - song info
<L> - playlist info'''


class Info:
	def song_info(index, listbox_music, playlist, length):
		file_name = listbox_music.get(index)  								# get file name
		full_file_path = playlist[index]  									# get the file full path
		file_type = os.path.splitext(full_file_path)[1][1:].upper()  		# get file extension type
		file_path = os.path.dirname(full_file_path)  						# get the path without the basename
		file_size = os.path.getsize(full_file_path)  						# get the size in bytes
		file_size = (file_size / 1024) / 1024  								# convert bytes to MB
		file_size = "{:.2f}".format(file_size)
		file_length = length.get(index)

		# get the created date
		date_created = time.strftime('%d-%b-%Y  %H:%M:%S', time.localtime(os.path.getctime(full_file_path)))
		# get the modified date
		date_modified = time.strftime('%d-%b-%Y  %H:%M:%S', time.localtime(os.path.getmtime(full_file_path)))
		# get the accessed date
		date_accessed = time.strftime('%d-%b-%Y  %H:%M:%S', time.localtime(os.path.getatime(full_file_path)))

		file_info = f"""
Name                : {file_name}\n
File type            :   {file_type}\n
Folder path      :   {file_path}\n
Size                   :   {file_size} MB\n
Length              :   {file_length}\n
Date created     :   {date_created}\n
Date modified  :   {date_modified}\n
Date accessed   :   {date_accessed}\n\n
Do you want to open the folder location ?"""

		# show message with the location and ask to open the folder
		show_message = messagebox.askyesno("Song info", file_info)

		# open folder location
		if show_message == True:  
			os.startfile(file_path)

		return show_message	 

	def playlist_info(playlist, length_song):
		total_length_in_sec = 0  									# store total length in seconds
		total_size = 0  											# store total size
		for file in playlist:
			song_length = length_song(file)  						# get the length of every song from playlist
			total_length_in_sec += song_length

			file_size = os.path.getsize(file)  						# get the size in bytes
			file_size = (file_size / 1024) / 1024  					# convert bytes to MB
			total_size += file_size

		total_size = "{:.2f}".format(total_size)
		hours = round(total_length_in_sec // 3600)  				# get hours
		mins = round((total_length_in_sec - hours * 3600) // 60)  	# get minutes
		secs = round(total_length_in_sec - hours * 3600 - mins * 60)# get seconds

		# convert 60 mins/secs
		if mins == 60:
			hours += 1
			mins = 0
		elif secs == 60:
			mins += 1
			secs = 0
		total_length = "{:02d}:{:02d}:{:02d}".format(hours, mins, secs)
		info = messagebox.showinfo("Playlist info", f"Total length:   {total_length}\n"
									   f"Total size:     {total_size} MB")
		return info  