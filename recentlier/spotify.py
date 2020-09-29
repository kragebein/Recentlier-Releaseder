#!/usr/bin/python3
''' Spotify API file '''
import json, re, requests, spotipy.util, os, sys, datetime, traceback, time, sqlite3
import spotipy.util as util
from recentlier.config import conf as _conf
from recentlier.div import _dump, track_name, Spinner
spin = Spinner('dna', 0, static=1)

class spot():
    ''' Spot class handles all API queries towards spotify. '''
    def __init__(self):
        conf = _conf()
        self.debug = False                  # Set to true if --debug (TODO)
        self.tracklist = {}                 # Unsorted tracklist
        self.popped = []                    # Duplicate tracks
        self.plname = conf.playlist_name    # Playlist name
        self.plsize = conf.playlist_size    # Playlist siuze
        self.follow = []                    # Follow list
        self.albums = {}                    # Albums list from all follow artists
        self.get_artists_total = ''         # how many artists in total
        self.get_artist_album_total = ''    # How many albums does this artist have
        self.get_artist_single_total = ''   # how many singles does this artist have
        self.get_artist_tracks_total = ''   # How many tracks does this artist have in totalt
        self.track_details_total = ''       # How many tracks will we request for detailed analysis
        self.get_album_tracks_total = 0     # Total tracks counter (temp var)
        self.artist_albums = {}             # Artist albums for generator
        self.artist_singles = {}            # artist singles for generator
        self.artist_collection = {}         # artist collections for generator
        self.artist_appears_on = {}         # artist appears_on for generator          
        self.sp = ''                        # Spotify session 
        self.username = self.getusername()  # username
        self.cid = conf.cid                 # Client Key
        self.cic = conf.cic                 # Client Secret
        self.callback = conf.callback       # Callback URL.

        self.x = sqlite3.connect('cache.db')
        self.sql = self.x.cursor()
        self.scope = 'playlist-read-private, user-follow-read, playlist-modify-private'
        self.login()
        mydata = self.sp.me()               # User profile
        self.myid = mydata['id']            # User ID
        # Enable or disable local cache through config.
        if conf.cache.lower() == 'yes':
            self.sp._get = self._get
            self.sql.execute('CREATE TABLE IF NOT EXISTS cache (url TEXT, value BLOB);')
            self.x.commit()

    def login(self):
        try: 
            token = util.prompt_for_user_token(self.username, \
                self.scope, client_id=self.cid, client_secret=self.cic, \
                redirect_uri=self.callback)
        except Exception as r: 
            print('Unable to log you in. \n\nTraceback: {}'.format(r))
            exit()
        try:
            if token:
                self.sp = spotipy.Spotify(auth=token)
            return True
        except:
            print('Error: Couldnt validate token! Try deleting .cache-{}'.format(self.username))
            exit()

    # rewrite spotipy internals to support local caching.
    def _get(self, url, args=None, payload=None, **kwargs):   
        if args:
            kwargs.update(args)
        _db = self.db(url, 'get')
        if _db:
            return json.loads(_db)
        returndata = self.sp._internal_call("GET", url, payload, kwargs)
        self.db(url, 'put', value=returndata) 
        return returndata

    def db(self, url, method, value=None):
        prefix = "https://api.spotify.com/v1/"
        if not url.startswith('http'):
            url = prefix + url
        if method == 'get':
            query = 'SELECT value FROM cache WHERE url = "{}"'.format(url)
            data = self.sql.execute(query).fetchone()
#            print('SQL:(CACHE) fetching {}'.format(url) if data is not None else 'SQL:(API) fetching {}'.format(url))
            return data[0] if data is not None else False
        elif method == 'put':
            _list = ('https://api.spotify.com/v1/tracks/','https://api.spotify.com/v1/albums/')
            if url.startswith(_list):
                #print('SQL: putting {}'.format(url))
                query = 'REPLACE INTO cache VALUES(?, ?)'
                self.sql.execute(query, [url, json.dumps(value)])
                self.x.commit()

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
            result = self.sp.next(result['artists'])
            for i in result['artists']['items']:
                follow_data['artists']['items'].append(i)
            if result['artists']['next'] is None:
                break
        for i in follow_data['artists']['items']:
            self.follow.append(i['id'])

        for i in follow_data['artists']['items']:
            yield i

    def get_collection(self, artist):
        result = self.sp.artist_albums(artist, limit=50, album_type='collection')
        self.artist_collection.update(result)
        while 'next' in result and result['next'] is not None:
            result = self.sp.next(result)
            for i in result['items']:
                self.artist_collection['items'].append(i)
            if result['next'] is None:
                break
    def get_appears_on(self, artist):
        result = self.sp.artist_albums(artist, limit=50, album_type='single')
        self.artist_appears_on.update(result)
        while 'next' in result and result['next'] is not None:
            result = self.sp.next(result)
            for i in result['items']:
                self.artist_appears_on['items'].append(i)
            if result['next'] is None:
                break
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
        ''' albums and singles generator '''
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
        #for i in self.artist_collection['items']:
        #    yield i
        #for i in self.artist_appears_on['items']:
        #    yield i

    def get_tracks(self, album):
        ''' album tracks generator '''
        self.get_album_tracks_total = 0
        album_tracks = {}
        result = self.sp.album_tracks(album, limit=50)
        album_tracks.update(result)
        while 'next' in result and result['next'] is not None:
            result = self.sp.next(result)
            for i in result['items']:
                album_tracks['items'].append(i)
            if result['next'] is None:
                break
        self.get_album_tracks_total = len(album_tracks['items'])
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
        self.unsorted = {}
        
        # needed for debugging
        #dump = _dump()
        #if dump:
            #self.tracklist.update({'tracks': dump['tracks']})

        track = self.tracklist['tracks']
        # Find and remove new instances of older tracks
        dupe_count = 0
        for i in track.copy():
            #print('\r{} duplicates removed..'.format(dupe_count), end='', flush=True)
            dupes = {}
            try: 
                artist_id = track[i][4]
                track_name = track[i][3]
                release_date = track[i][5]
            except:
                break
            for dupe in track.copy():                       # == for exact match - use 'is' for aproximate match                     
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
            #print('done.')
            return self.playlist_new
        except Exception:
            traceback.print_exc()
            # - stop exceution if this important part fails

    def diff(self, first, second):
        ''' Compare list types '''
        return [item for item in first if item not in second]

    def updateplaylist(self):
        ''' 
        Actuallay fill up the playlist. If playlist has data, 
        '''
        # Collect the datasets
        try:
            playlist = self.sort()
        except:
            with open('DEBUGDUMP.TXT', 'w') as brrt:
                brrt.write(json.dumps(locals(), indent=2))
                brrt.close()
            print('DEBUGDUMP.TXT created! Please upload!')
            pass
        playlist_id = self.genplaylist()
        playlist_tracks = self.sp.user_playlist_tracks(self.myid,playlist_id=playlist_id)
        length = len(playlist_tracks['items'])
        
        
        # if empty, add everything to playlist
        if length == 0:
            self.addtoplaylist(playlist_id, playlist)
            for i in playlist:
                spin.tick(text='[+] {}'.format(track_name(self.tracklist, i)))
                #print('[+] {}'.format(track_name(self.tracklist, i)))
            return True

        # Add, remove, compare and adjust. 
        current_id = []
        for track in playlist_tracks['items']:
            current_id.append(track['track']['id'])
        comparison = []
        in_tracks = []
        comparison = self.diff(current_id, playlist)
        in_tracks = self.diff(playlist, current_id)

        # sorted data is identical to online playlist
        if current_id == playlist:
            spin.tick(text='Online playlist and local sorted list are the same.')
            return True

        # If we need to update everything, might as well just swap out everything.
        if len(comparison) > int(self.plsize): # self.plsize
            spin.tick(text='Flushing playlist.')
            self.sp.user_playlist_replace_tracks(self.myid, playlist_id, playlist)
            for i in playlist:
                spin.tick(text='[+] {}'.format(track_name(self.tracklist, i)))
                #print('[+] {}'.format(track_name(self.tracklist, i)))
            return True

        # We dont need to do anything, how have the user even reached this code?
        if len(comparison) == self.plsize:
            spin.tick(text='Playlist doesnt need updating, local list and playlist are the same size.')
            return True
        
        # Gracefully update the playlist. 
        if len(comparison) > 1:
            spin.tick(text='There are {} new tracks'.format(len(comparison)))
            start_pos = int(self.plsize) - len(comparison)
            for i in set(playlist).difference(current_id):
                spin.tick(text='[+] {}'.format(track_name(self.tracklist, i)))
                #print('[+] {}'.format(track_name(self.tracklist, i)))
            for i in comparison:
                spin.tick(text='[-] {}'.format(track_name(self.tracklist, i)))
                #print('[-] {}'.format(track_name(self.tracklist, i)))
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
            spin.tick('Updated playlist with {} tracks'.format(self.plsize))
        except Exception:
            traceback.print_exc()

    def get_single_track_details(self, i):
        '''Just print the data from this single track'''
        return json.dumps(self.sp.track(i), indent=2)