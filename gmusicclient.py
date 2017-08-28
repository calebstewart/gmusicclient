#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: caleb
# @Date:   2016-02-27 09:30:50
# @Last modified by:   caleb
# @Last modified time: 2017-08-27T21:18:25-07:00
from gmusicapi import Mobileclient
from colorama import Fore,Back,Style
import colorama
import getpass
import sys
import os
import log
import mediaplayer
import texttable as tt
import readline
import cmdln
import string
import keyring

class GMusicClient(cmdln.Cmdln):
	"""${name}: Google Play Music Command Line Client

	${command_list}
	"""

	# Member Variables denoting application name and prompt
	name='gmusicplayer'
	prompt="gmusic$ "
	# The MediaPlayer object
	player=None
	window=None

	# Initialize the object
	def __init__(self, email, password):
		cmdln.Cmdln.__init__(self)
		self.login(email, password)

	# Login to Google Play Music and setup the media player object
	def login(self, email, password):
		try:
			self.player = mediaplayer.MediaPlayer(email, password)
		except:
			log.error('authentication failed!')
			sys.exit(-1)
		log.info('authenticated as %s' % email)

	@cmdln.alias('stat', 'st')
	@cmdln.option('-p', '--playlist', action='store_const', const='playlist', dest='type', help='stream a playlist')
	@cmdln.option('-t', '--track', action='store_const', const='track', dest='type', default='track', help='stream a track')
	@cmdln.option('-a', '--artist', action='store_const', const='artist', dest='type', help='stream an artists top tracks')
	@cmdln.option('-b', '--album', action='store_const', const='album', dest='type', help='stream an album')
	@cmdln.option('-r', '--radio', action='store_const', const='radio', dest='type', help='stream a radio station')
	@cmdln.option('-n', '--next', action='store_const', const='insert', dest='how', default='replace', help='insert after the current track')
	@cmdln.option('--append', action='store_const', const='append', dest='how', help='append to the current play queue')
	@cmdln.option('--replace', action='store_const', const='replace', dest='how', help='replace the current play queue (default)')
	def do_stream(self, subcmd, opts, ID):
		"""${cmd_name}: stream a track, playlist or radio station

		${cmd_usage}
		${cmd_option_list}
		"""
		try:
			self.player.stream(ID, type=opts.type, how=opts.how)
			self.do_status(None, None)
		except Exception as e:
			log.error('failed to begin stream: {0}'.format(e))

	def do_shuffle(self, subcmd, opts):
		"""${cmd_name}: shuffle the current queue

		${cmd_usage}
		"""
		self.player.shuffle()
		self.do_status(None, None)

	def printable(self, s):
		return ''.join(filter(lambda x: x in string.printable, s))

	def do_playlist(self, subcmd, opts):
		"""${cmd_name}: list all playlists

		${cmd_usage}
		"""
		playlists = self.player.playlists()
		(height,width) = [ int(x) for x in os.popen('stty size').read().split() ]
		column_width = (width-40-15)
		table = tt.Texttable()
		table.header(['Name', 'Owner', 'Playlist ID'])
		table.set_cols_width([column_width/2, column_width/2, 40])
		for p in playlists:
			table.add_row([self.printable(p['name']), self.printable(p['ownerName']), self.printable(p['id'])])
		log.info('Search Results:')
		print table.draw()

	def build_table(self, header, last_width):
		(height,width) = [ int(x) for x in os.popen('stty size').read().split() ]
		table = tt.Texttable()
		table.header(header)
		column_width = []
		for i in range(len(header)-1):
			column_width.append((width-last_width-15)/len(header))
		column_width.append(last_width)
		table.set_cols_width(column_width)
		return table

	@cmdln.alias('s')
	@cmdln.option('-p', '--playlist', action='store_true', help='search for playlist')
	@cmdln.option('-t', '--track', action='store_true', help='search for track')
	def do_search(self, subcmd, opts, *query):
		"""${cmd_name}: Search the All-Access Database for tracks or Search personal playlists

		${cmd_usage}
		${cmd_option_list}
		"""
		result = self.player.search(''.join(query), max=15)

		pl_tab = self.build_table(['Name', 'Playlist ID'], 40)
		for p in [r['playlist'] for r in result['playlist_hits']]:
			pl_tab.add_row([self.printable(p['name']), self.printable(p['shareToken'])])
		log.info('Playlist Hits')
		print pl_tab.draw()

		artist_tab = self.build_table(['Artist', 'Artist ID'], 30)
		for a in [r['artist'] for r in result['artist_hits']]:
			artist_tab.add_row([self.printable(a['name']), a['artistId']])
		log.info('Artist Hits')
		print artist_tab.draw()

		album_tab = self.build_table(['Album', 'Artist', 'Album ID'], 30)
		for a in [r['album'] for r in result['album_hits']]:
			album_tab.add_row([self.printable(a['name']), self.printable(a['artist']), a['albumId']])
		log.info('Album Hits')
		print album_tab.draw()

		song_tab = self.build_table(['Title', 'Album', 'Artist', 'Track ID'], 28)
		for t in [r['track'] for r in result['song_hits']]:
			song_tab.add_row([self.printable(t['title']),self.printable(t['album']),self.printable(t['albumArtist']),self.printable(t['nid'])])
		log.info('Song Hits:')
		print song_tab.draw()

	@cmdln.option('-p', '--playlist', action='store_const', const='playlist', dest='type', help='playlist seed')
	@cmdln.option('-t', '--track', action='store_const', const='track', dest='type', default='track', help='track seed')
	@cmdln.option('-a', '--artist', action='store_const', const='artist', dest='type', help='artist seed')
	@cmdln.option('-b', '--album', action='store_const', const='album', dest='type', help='album seed')
	@cmdln.option('-r', '--radio', action='store_const', const='radio', dest='type', help='search for radio station')
	def do_radio(self, subcmd, opts, ID):
		"""${cmd_name}: lookup radio stations based on a track, album, artist or genre ID seed values

		If the given radio station does not exist and something other than a radio ID was
		specified, then the radio station will be created and returned.

		${cmd_usage}
		${cmd_option_list}
		"""
		try:
			stations = self.player.radio(ID, type=opts.type)
			table = self.build_table(['Station Name', 'Station ID'], 40)
			for s in stations:
				table.add_row([self.printable(s['name']) + ' Radio', s['id']])
			log.info('Radio Station Results:')
			print table.draw()
		except Exception as e:
			log.error('failed to lookup radio station: {0}'.format(e))

	def do_seek(self, subcmd, opts, position):
		"""${cmd_name}: go to a position in the song. Format should be decimal minutes and seconds (e.g. 1:25.3 for 1 minutes 25.3 seconds)

		${cmd_usage}
		${cmd_option_list}
		"""
		parts = position.split(':')
		try:
			minutes = float(parts[0])
			if len(parts) == 2:
				seconds = float(parts[1])
			elif len(parts) > 2:
				log.error('expected format of MM:SS!')
				return
		except:
			log.error('minutes and seconds must be numbers between 0 and 60.')
			return
		self.player.seek(minutes*60 + seconds)
		self.do_status(None, None)

	@cmdln.alias('>')
	def do_next(self, subcmd, opts):
		"""${cmd_name}: skip this song and move to the next in the queue

		${cmd_usage}
		"""
		self.player.next()
		self.do_status(None, None)

	@cmdln.alias('<')
	def do_prev(self, subcmd, opts):
		"""${cmd_name}: go to the previous song

		${cmd_usage}
		"""
		self.player.prev()
		self.do_status(None, None)

	@cmdln.alias('v')
	def do_volume(self, subcmd, opts, level):
		"""${cmd_name}: set the volume between 0 and 1

		${cmd_usage}
		"""
		try:
			self.player.volume(float(level))
		except:
			log.error('invalid level value (should be float between 0 and 1)')

	@cmdln.alias('l')
	@cmdln.option('-t', '--track', action='store', help='specify a track to rate')
	def do_like(self, subcmd, opts):
		"""${cmd_name}: set the rating of a track to 5

		${cmd_usage}
		${cmd_option_list}
		"""
		self.do_rate(subcmd, opts, '5')

	@cmdln.alias('d')
	@cmdln.option('-t', '--track', action='store', help='specify a track to rate')
	def do_dislike(self, subcmd, opts):
		"""${cmd_name}: set the rating of a track to 1

		${cmd_usage}
		${cmd_option_list}
		"""
		self.do_rate(subcmd, opts, '1')

	@cmdln.option('-t', '--track', action='store', help='specify a track to rate')
	def do_rate(self, subcmd, opts, rating):
		"""${cmd_name}: rate a track from 1 to 5 (1=Dislike/Thumbs Down, 5=Like/Thumbs Up)

		By default, this command will rate the current track.

		${cmd_usage}
		${cmd_option_list}
		"""
		value = 0
		try:
			value = int(rating)
			if value < 1 or value > 5:
				raise Exception()
		except:
			log.error('rating must be between 1 and 5!')
			return
		self.player.rate(value, track=opts.track)

	def do_quality(self, subcmd, opts, quality):
		"""${cmd_name}: set quality to one of low,med,hi

		${cmd_usage}
		"""
		if quality != 'hi' and quality != 'med' and quality != 'low':
			log.error('expected one of \'hi\', \'med\', or \'low\'')
			return
		self.player.set_quality(quality)

	def do_pause(self, subcmd, opts):
		"""${cmd_name}: pause the current track

		${cmd_usage}
		"""
		self.player.pause()

	@cmdln.alias('p')
	def do_toggle(self, subcmd, opts):
		"""${cmd_name}: toggle play vs pause for the current track.

		${cmd_usage}
		"""
		if self.player.current_state == "PLAY":
			self.player.pause()
		elif self.player.current_state == "PAUSE":
			self.player.play()

	def do_queue(self, subcmd, opts):
		"""${cmd_name}: print the current play queue

		${cmd_usage}
		"""
		queue = self.player.queue
		for i in range(len(queue)):
			if queue[i][0] == 'T':
				track = self.player.get_info(queue[i])
				if i == self.player.current['index']:
					log.info('[current] queue[{0}]: track: {1}, album: {2}, artist: {3}'.format(i, self.printable(track['title']), self.printable(track['album']), self.printable(track['albumArtist'])))
				else:
					log.info('queue[{0}]: track: {1}, album: {2}, artist: {3}'.format(i, self.printable(track['title']), self.printable(track['album']), self.printable(track['albumArtist'])))

	def do_play(self, line):
		self.player.play()

	def do_status(self, subcmd, opts):
		"""${cmd_name}: retrieve the status of the streaming service

		${cmd_usage}
		"""
		current = self.player.current
		if current['index'] == -1:
			log.info('Queue empty.')
			return
		log.info('Title: {0}, Album: {1}, Artist: {2}'.format(current['title'], current['album'], current['albumArtist']))
		(duration_min, duration_secs) = divmod(int(current['durationMillis'])/1000, 60)
		(position_min, position_secs) = divmod(self.player.position(), 60)
		log.info('Stream: {pmin:02d}:{psec:02d}/{dmin:02d}:{dsec:02d}'.format(pmin=int(position_min), psec=int(position_secs), dmin=int(duration_min), dsec=int(duration_secs)))

	def do_exit(self, line):
		sys.exit(0)

	def postcmd(self, argv):
		current = self.player.current
		if current != None and current['index'] != -1:
			(duration_min, duration_secs) = divmod(int(current['durationMillis'])/1000, 60)
			(position_min, position_secs) = divmod(self.player.position(), 60)
			self.prompt = '({pmin:02d}:{psec:02d}/{dmin:02d}:{dsec:02d}) gmusic$ '.format(pmin=int(position_min),psec=int(position_secs),
				dmin=int(duration_min),dsec=int(duration_secs))
		else:
			self.prompt = 'gmusic$ '
		cmdln.Cmdln.postcmd(self, argv)

	def emptyline(self):
		return ''

if __name__ == '__main__':

	# Initialize Colorama
	#colorama.init(autoreset=True) # Colorama breaks readline!

	# Grab the E-Mail
	email = raw_input('E-Mail: ')
	# Unlock the keyring
	keyring.get_keyring()
	# Try and grab the password from the login keyring
	password = keyring.get_password('login', email)

	# If we didn't find an entry, ask for the password
	if password == None:
		password = getpass.getpass('Password: ')
		log.warn('Credentials not in Keyring!')
		yn = raw_input('Save credentials in Gnome Keyring? (y/n) ')
		if len(yn) and (yn[0] == 'y' or yn[0] == 'Y'):
			keyring.set_password('login', email, password)

	client = GMusicClient(email, password)
	sys.exit(client.main(loop=cmdln.LOOP_ALWAYS))

	sys.exit(0)
