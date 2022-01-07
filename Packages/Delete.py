from tkinter import *

class Delete:
	def __init__(self, playlist, listbox_playlist, length, numbers, deleted_songs):
		self.playlist = playlist
		self.listbox_playlist = listbox_playlist
		self.listbox_length = length
		self.listbox_numbers = numbers
		self.deleted_songs = deleted_songs

	def delete_song(self):
		song_delete_index = self.listbox_playlist.curselection()
		if song_delete_index:
			song_delete_index = song_delete_index[0]  						# get index
			song_delete_name = self.listbox_playlist.get(song_delete_index) # get name
			song_delete_length = self.listbox_length.get(song_delete_index) # get length
			
			song_delete_fullpath = self.playlist.pop(song_delete_index)		# delete song from playlist
				
			self.listbox_length.delete(song_delete_index)  					# delete the length from listbox
			self.listbox_playlist.delete(song_delete_index)  				# delete the song from listbox
			self.listbox_numbers.delete(END)  								# delete the last number from list

			# get a list with index + name + length + fullpath of the song
			full_info_deleted_song = [[song_delete_index,
											 song_delete_name,
											 song_delete_length,
											 song_delete_fullpath]]

			self.deleted_songs.append(full_info_deleted_song)   # add deleted song to the deleted list

	def clear_list(self):
		index_song = 0
		deleted_list = []
		if self.listbox_playlist.size():
			for file in self.listbox_playlist.get(0, END):
				song_delete_name = self.listbox_playlist.get(0)  # get name of the song from list box
				song_delete_length = self.listbox_length.get(0)  # get length of the song
				song_delete_fullpath = self.playlist.pop(0)

				self.listbox_length.delete(0)  		# delete the length from listbox
				self.listbox_playlist.delete(0)  	# delete the song from listbox
				self.listbox_numbers.delete(0)  	# delete the last number from list

				# get a list with index + name + length + fullpath of the song
				full_info_deleted_song = [index_song,
												 song_delete_name,
												 song_delete_length,
												 song_delete_fullpath]

				deleted_list.append(full_info_deleted_song)
				index_song += 1								 

			self.deleted_songs.append(deleted_list)   # add deleted song to the deleted list								 

class Restore(Delete):
	def __init__(self, playlist, listbox_playlist, length, numbers, deleted_songs):
		super().__init__(playlist, listbox_playlist, length, numbers, deleted_songs)
			
	def restore_delete(self):
		if self.deleted_songs:
			last_song_from_list = self.deleted_songs.pop()  # get the last song/list added in the deleted songs list

			for file in last_song_from_list:
				song_index = file[0]  						# get index
				song_name = file[1]  						# get name 
				song_length = file[2] 	 					# get length
				song_fullpath = file[3]  					# get full path
				song_count = self.listbox_numbers.size()  	# get list size

				self.listbox_numbers.insert(END, int(song_count) + 1)  	# insert song count
				self.listbox_playlist.insert(song_index, song_name)  	# insert song name
				self.listbox_length.insert(song_index, song_length)  	# insert length
				self.playlist.insert(song_index, song_fullpath)  		# insert full path to the playlist

			first_index_in_deleted_list = last_song_from_list[0][0]

			self.listbox_playlist.see(first_index_in_deleted_list)			# jump to the restored song
			self.listbox_numbers.see(first_index_in_deleted_list)
			self.listbox_length.see(first_index_in_deleted_list)

			self.listbox_playlist.select_clear(0, END)  					# deselect all
			self.listbox_playlist.selection_set(first_index_in_deleted_list)# highlight the restored song				

			
			

			