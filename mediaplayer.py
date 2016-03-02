# -*- coding: utf-8 -*-
# @Author: caleb
# @Date:   2016-02-27 23:09:54
# @Last Modified by:   Caleb Stewart
# @Last Modified time: 2016-03-02 00:50:29
# import pygst
# pygst.require('0.10')
# import gst
from gi.repository import Gst
import gmusicapi
import log
import string
import threading
import random

class MediaPlayer:
	player = None
	api = None
	device = None
	queue = []
	current = { 'index': -1 }
	timer_thread = None
	current_state = 'STOP'
	seek_position = 0
	quality = 'hi'

	def __init__(self, email, password):
		Gst.init(None)
		self.player = Gst.ElementFactory.make('playbin', 'player')
		self.player.set_state(Gst.State.NULL)
		self.player.set_property('volume', 1.0)
		self.player.connect('about-to-finish', self.signal_song_finished)
		self.api = gmusicapi.Mobileclient()
		if self.api.login(email,password, gmusicapi.Mobileclient.FROM_MAC_ADDRESS) == False:
			raise Exception('auth failed as %s' % email)
		self.device = self.api.get_registered_devices()[0]
		self.current = {'uri': None, 'index': -1}

	def search(self, query, max=25):
		results = self.api.search_all_access(query, max_results=max)
		return results #[ r['track'] for r in results[what] ]

	def get_playlists(self):
		playlists = self.api.get_all_playlists()
		return [{'name':p['name'], 'id': p['name']} for p in playlists]

	def get_playlist(self, ID):
		for p in self.api.get_all_user_playlist_contents():
			if p['id'] == ID:
				return p
		return None

	def get_info(self, ID):
		try:
			track = self.api.get_track_info(ID)
		except:
			return None
		return track

	def playlists(self):
		return self.api.get_all_playlists()

	def radio(self, ID=None, type='track'):
		stations = self.api.get_all_stations()
		print type
		if type == 'track':
			name = self.api.get_track_info(ID)['title']
			stations = [s for s in stations if s['seed'].get('trackId', None) == ID]
		elif type == 'genre':
			name = ID # I don't know...
			stations = [s for s in stations if s['seed'].get('genreId', None) == ID]
		elif type == 'radio':
			stations = [s for s in stations if s['id'] == ID]
		elif type == 'artist':
			name = self.api.get_artist_info(ID)['name']
			stations = [s for s in stations if s['seed'].get('artistId', None) == ID]
		elif type == 'album':
			name = self.api.get_album_info(ID)['name']
			stations = [s for s in stations if s['seed'].get('albumId', None) == ID]
		else:
			raise Exception()
		
		# If we were looking for a radio station based on something, 
		# create it if it doesn't exist
		if len(stations) == 0 and type != 'radio':
			if type == 'track':
				ID = self.api.create_station(name, track_id=ID)
			elif type == 'genre':
				ID = self.api.create_station(name, genre_id=ID)
			elif type == 'artist':
				ID = self.api.create_station(name, artist_id=ID)
			elif type == 'album':
				ID = self.api.create_station(name, album_id=ID)
			return self.radio(ID=ID)
		return stations

	def stream(self, ID,  type='track', how='replace'):
		if type == 'track':
			new_queue = [ID]
		elif type =='playlist':
			playlist = self.get_playlist(ID)
			if playlist == None:
				raise Exception('playlist not found')
			new_queue = [entry['trackId'] for entry in playlist['tracks']]
		elif type == 'radio':
			station = self.api.get_station_tracks(ID, 100)
			if station == None:
				raise Exception('radio station not found')
			new_queue = [ entry['nid'] for entry in station ]
		elif type == 'artist':
			artist = self.api.get_artist_info(ID, max_top_tracks=100)
			if artist == None:
				raise Exception('artist not found')
			new_queue = [ entry['nid'] for entry in artist['topTracks'] ]
		elif type == 'album':
			album = self.api.get_album_info(ID, include_tracks = True)
			if album == None:
				raise Exception('album not found')
			new_queue = [ entry['nid'] for entry in album['tracks'] ]
		else:
			raise Exception('unknown stream type: {0}'.format(type))
		if how =='replace':
			#self.state('STOP')
			self.queue = new_queue
			# The queue was replaced, we should start the correct song
			self.current = { 'index': -1 }
			self.next()
		elif how == 'append':
			self.queue = self.queue + new_queue
		elif how == 'insert':
			self.queue = self.queue[:(self.current['index']+1)] + new_queue + self.queue[(self.current['index']+1):]
		else:
			raise Exception('unknown stream insertion method: {0}'.format(how))

	def play(self):
		self.state('PLAY')

	def pause(self):
		self.state('PAUSE')

	def replay(self):
		self.seek(0)
		self.state('PLAY')

	def seek(self, where):
		old = self.state('PAUSE')
		self.player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, int(where * 1000000000))
		self.state(old)

	def position(self):
		return (self.player.query_position(Gst.Format.TIME)[1] / 1000000000.0)

	def set_quality(self, quality):
		if quality != 'hi' and quality != 'med' and quality != 'low':
			return
		self.quality = quality
		if self.current['index'] != -1:
			self.current['index'] = self.current['index']-1
			self.next()

	def shuffle(self):
		self.state('STOP')
		self.current['index'] = -1
		random.shuffle(self.queue)
		self.next()

	def stop(self):
		self.state('STOP')

	def prev(self):
		self.stop()
		self.current['index'] = self.current['index'] - 2
		self.next()

	def next(self, player=None, statechange=True):
		nextidx = self.current['index'] + 1
		if len(self.queue) <= nextidx:
			return
		ID = self.queue[nextidx]
		while ID[0] != 'T':
			nextidx = nextidx + 1
			ID = self.queue[nextidx]
		self.current = self.get_info(ID)
		self.current['index'] = nextidx;
		self.current['uri'] = self.api.get_stream_url(self.current.get('nid', self.current.get('id', '')), self.device['id'].strip('0x'), quality=self.quality)
		if statechange:
			self.state('STOP')
		self.player.set_property('uri', self.current['uri'])
		if statechange:
			self.state('PLAY')

	def state(self, newstate):
		if newstate == self.current_state:
			return
		if newstate == 'PLAY':
			self.player.set_state(Gst.State.PLAYING)
		elif newstate == 'PAUSE':
			self.player.set_state(Gst.State.PAUSED)
		elif newstate == 'STOP':
			self.player.set_state(Gst.State.NULL)
		old = self.current_state
		self.current_state = newstate
		return old

	def rate(self, rating, track=None):
		if track == None:
			# Check if there is a current song
			if self.current['index'] == -1:
				return
			track = self.current['nid']
		info = self.get_info(track)
		if info == None:
			return
		info['rating'] = max(min(rating, 5), 1)
		self.api.change_song_metadata(info)

	def volume(self, level):
		level = max(min(level, 1), 0) # bound level between 0 and 1
		self.player.set_property('volume', level)


	# Signal from GStreamer that the song is finished playing
	# Time to start the next one!
	def signal_song_finished(self, player):
		self.next(statechange=False)
		return