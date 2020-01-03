#!/usr/bin/python3
''' Spotify API file '''
import json, re, requests, spotipy.util, os, sys, datetime, traceback, time
import spotipy.util as util
from recentlier.config import conf as _conf
from recentlier.div import _dump, track_name


class spot():
    def __init__(self):
        conf = _conf()
        self.tracklist = {}
        self.popped = []
        self.plname = conf.playlist_name
        self.plsize = conf.playlist_size
        self.follow = []
        self.albums = {}
        self.get_artists_total = ''
        self.get_artist_album_total = ''
        self.get_artist_single_total = ''
        self.get_artist_tracks_total = ''
        self.track_details_total = ''
        self.artist_albums = {}
        self.artist_singles = {}
        self.data = []
        self.username = self.getusername()
        self.cid = ''    # Client ID
        self.cic = ''    # Client Secret
        self.scope = 'playlist-read-private, user-follow-read, playlist-modify-private'
        self.callback = 'https://www.lazywack.no'
        try: 
            token = util.prompt_for_user_token(self.username, \
                self.scope, client_id=self.cid, client_secret=self.cic, \
                redirect_uri=self.callback)
        except Exception as r:
            raise('Couldnt retrieve token!\n{}'.format(r))
        if token:
            self.sp = spotipy.Spotify(auth=token)
        mydata = self.sp.me()
        self.myid = mydata['id']

    def getusername(self):
        '''Will fill the username variable'''
        
        try:
            with open('.user','r') as ussr:
                usssr = json.loads(ussr.read())
            return usssr['username']
        except:
            username = input('Enter your spotify username: ')
            if username is None:
                sys.exit()
            with open('.user', 'w') as ussr:
                ussr.write(json.dumps({'username': username}))
            return username
        
    def get_artists(self):
        ''' Artists generator'''
        follow_data = {}
        result = self.sp.current_user_followed_artists(limit=50)
        follow_data.update(result)
        while 'next' in result['artists'] and result['artists']['next'] is not None:
            resulty = self.sp.next(result['artists'])
            for i in resulty['artists']['items']:
                follow_data['artists']['items'].append(i)
            _next = resulty['artists']['next']
            if resulty['artists']['next'] is None:
                break
        for i in follow_data['artists']['items']:
            self.follow.append(i['id'])

        for i in follow_data['artists']['items']:
            yield i

    def get_albums_singles(self, artist):
        result = self.sp.artist_albums(artist, limit=50, album_type='single')
        self.artist_singles.update(result)
        while 'next' in result and result['next'] is not None:
            result = self.sp.next(result)
            for i in result['items']:
                self.artist_singles['items'].append(i)
            if result['next'] is None:
                break
        
    def get_albums(self, artist):
        ''' albums generator '''
        self.get_albums_singles(artist)
        result = self.sp.artist_albums(artist, limit=50, album_type='album')
        self.artist_albums.update(result)
        while 'next' in result and result['next'] is not None:
            result = self.sp.next(result)
            for i in result['items']:
                self.artist_albums['items'].append(i)
            #self.artist_albums.update(result)
            if result['next'] is None:
                break
        for i in self.artist_singles['items']:
            yield i
        for i in self.artist_albums['items']:
            yield i

    def get_tracks(self, album):
        ''' album tracks generator '''
        album_tracks = {}
        result = self.sp.album_tracks(album, limit=50)
        album_tracks.update(result)
        while 'next' in result and result['next'] is not None:
            result = self.sp.next(result)
            for i in result['items']:
                album_tracks['items'].append(i)
            if result['next'] is None:
                break
        for i in album_tracks['items']:
            yield i

    def get_track_details(self, tracklist):
        ''' track detail generator '''
        tracks = {}
        result = self.sp.tracks(tracklist)
        tracks.update(result)
        for i in tracks['tracks']:
            yield i

    def join(self, album, track_data):
        self.tracklist.update({album: track_data})

    def genplaylist(self):
        '''Locate or create the playlist in config '''
        def gp(pl_data):
            for i in pl_data['items']:
                if self.username in i['owner']['id']:
                    playlists.update({i['id']: [i['name'], i['owner']['id']]})
        playlists = {}
        pl = self.sp.user_playlists(self.myid)
        gp(pl)
        while 'next' in pl and pl['next'] is not None:
            pl = self.sp.next(pl)
            gp(pl)
        for i in playlists: 
            if self.plname in playlists[i]:
                playlist_id = i
        try:
            playlist_id
        except NameError:
            playlist_create = self.sp.user_playlist_create(self.myid, self.plname, public=False)
            self.sp.user_playlist
            playlist_id = playlist_create['id']
        self.tracklist.update({'playlist_id': playlist_id})
        return playlist_id
        
    def sort(self):
        ''' sort all the data we have retrieved from spotify '''
        dump = _dump()
        self.unsorted = {}
        
        # needed for debugging
        #if dump:
            #self.tracklist.update({'tracks': dump['tracks']})

        track = self.tracklist['tracks']
        # Find and remove new instances of older tracks
        dupe_count = 0
        for i in track.copy():
            print('\r{} duplicates removed..'.format(dupe_count), end='', flush=True)
            dupes = {}
            try: # we'll try it first, in case we are trying to iterate over a removed duplicate
                artist_id = track[i][4]
                track_name = track[i][3]
                release_date = track[i][5]
            except:
                break
            for dupe in track.copy():
                if artist_id in track[dupe][4] and track_name == track[dupe][3] and release_date != track[dupe][5] and len(track[dupe][5]) != 4:
                    dupes.update({dupe: track[dupe][5]})
                    dupe_count +=1
            if len(dupes) > 2:
                one = {}
                for i in dupes:
                    if len(dupes[i]) > 5:
                        one.update({i: dupes[i]})
                one_sorted = sorted(one.items(), key=lambda x: datetime.datetime.strptime(x[1],'%Y-%m-%d'), reverse=False)
                length = len(one_sorted)
                for i in one_sorted[1:length]:
                    self.tracklist['tracks'].pop(i[0])
                    self.popped.append(i[0])
                    dupe_count +=1
                    
        # populate the unsorted list with a tuple
        pop = []
        for data in track:
            self.unsorted.update({data: track[data][5]})
        for i in self.unsorted:
            if len(self.unsorted[i]) <= 5: 
                pop.append(i)
        for i in pop:
            self.unsorted.pop(i)

        self.sorted = sorted(self.unsorted.items(), key=lambda x: datetime.datetime.strptime(x[1],'%Y-%m-%d'), reverse=True)
        try:
            self.playlist_new = []
            size = int(self.plsize)
            for i in self.sorted[0:size]:
                self.playlist_new.append(i[0])
            print('done.')
            return self.playlist_new
        except Exception:
            traceback.print_exc()
            raise Exception

    def diff(self, first, second):
        return [item for item in first if item not in second]

    def updateplaylist(self):
        ''' 
        Gracefully update the already populated playlist.
        If playlist is empty, all sorted tracks will be dumped into playlist.

        '''
        # Collect the datasets
        playlist = self.sort()
        playlist_id = self.genplaylist()
        playlist_tracks = self.sp.user_playlist_tracks(self.myid,playlist_id=playlist_id)

        length = len(playlist_tracks['items'])
        # if empty, add everything to playlist
        if length == 0:
            self.addtoplaylist(playlist_id, playlist)
            for i in playlist:
                print('[+] {}'.format(track_name(self.tracklist, i).decode('utf-8')))
            return True

        # Add, remove, compare and adjust. 
        current_id = []
        for track in playlist_tracks['items']:
            current_id.append(track['track']['id'])
        comparison = []
        in_tracks = []
        comparison = self.diff(current_id, playlist)
        in_tracks = self.diff(playlist, current_id)

        if current_id == playlist:
            # sorted data is identical to online playlist
            print('Online playlist and local sorted list are the same.')
            return True

        # If we need to update everything, might as well just swap out everything.
        if len(comparison) > int(self.plsize): # self.plsize
            print('Flushing playlist.')
            self.sp.user_playlist_replace_tracks(self.myid, playlist_id, playlist)
            for i in playlist:
                print('[+] {}'.format(track_name(self.tracklist, i).decode('utf-8')))
            return True

        # We dont need to do anything, how have the user even reached this code?
        if len(comparison) == self.plsize:
            print('Playlist doesnt need updating, local list and playlist are the same size.')
            return True
        
        if len(comparison) > 1:
            # Gracefully update the playlist. 
            print('There are {} new tracks'.format(len(comparison)))
            start_pos = int(self.plsize) - len(comparison)
            for i in set(playlist).difference(current_id):
                print('[+] {}'.format(track_name(self.tracklist, i).decode('utf-8')))
            print('')
            for i in comparison:
                print('[-] {}'.format(track_name(self.tracklist, i).decode('utf-8')))
            self.sp.user_playlist_remove_all_occurrences_of_tracks(self.myid, playlist_id, comparison)
            self.sp.user_playlist_add_tracks(self.myid, playlist_id, in_tracks)
            for i in in_tracks: # Adjust the position of the newly added tracks
                for placement, trackid in enumerate(playlist):
                    if i == trackid:
                        self.sp.user_playlist_reorder_tracks(self.myid, playlist_id, start_pos, placement)
                        start_pos +=1
                        break 
                    else:
                        continue
            return True

    def addtoplaylist(self, playlist_id, playlist):
        ''' dump sorted tracks into playlist'''
        try:
            self.sp.user_playlist_add_tracks(self.myid, playlist_id, playlist)
            print('Updated playlist with {} tracks'.format(self.plsize))
        except Exception:
            traceback.print_exc()

    def get_single_track_details(self, i):
        return json.dumps(self.sp.track(i), indent=2)