#!/usr/bin/python3
''' Spotify API file '''
import json, spotipy.util,sys, datetime, traceback, sqlite3
import spotipy.util as util
from recentlier.config import conf as _conf
from recentlier.div import track_name, Spinner
conf = _conf()
spin = Spinner(conf.st, 0, static=1)

class spot():
    ''' Spot class handles all API queries towards spotify. '''
    def __init__(self):
        self.debug = False                  # Set to true if --debug (TODO)
        self.tracklist = {}                 # Unsorted tracklist
        self.popped = {}                    # Duplicat track amount
        self.plname = conf.playlist_name    # Playlist name
        self.plsize = int(conf.playlist_size)# Playlist size
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
            
    # rewrite spotipy internals to allow caching.
    def _get(self, url, args=None, payload=None, **kwargs):   
        if args:
            kwargs.update(args)
        _db = self.db(url, 'get')
        if _db:
            return json.loads(_db)
        else:
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
            #print('SQL:(CACHE) fetching {}'.format(url) if data is not None else 'SQL:(API) fetching {}'.format(url))
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
                print('Something went very wrong! Please delete .cache, cache.db, .user, and dump.json')
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
        ''' 31.10.20: Sort function rewrite'''
        allTracks = {}
        self.unsorted = {}
        track = self.tracklist['tracks']
        
        #Fill the allTracks Dict with all potential duplicates
        for i in track.copy():
            try:
                trackId = i
                artistName = track[i][2].strip()
                trackName = track[i][3].strip()
                releaseDate = track[i][5] 
            except Exception as R:
                traceback.print_exc()
                break # print stack and continue with next iteration
            if len(releaseDate) == 4: 
                if int(releaseDate) <= 2011:
                    releaseDate = str('2011')
                releaseDate = releaseDate + '-01-01'
            if len(releaseDate) != 10: break 
            thisTrack = '{} - {}'.format(artistName, trackName)
            if thisTrack in allTracks:
                allTracks[thisTrack].update({trackId: releaseDate})
            else:
                allTracks[thisTrack] = {trackId: releaseDate}
        for x in allTracks: # adds oldest of all occurences to unsorted list
            tId, tDate = sorted(allTracks[x].items(), \
                 key=lambda x: datetime.datetime.strptime(x[1],'%Y-%m-%d'), reverse=False)[0]
            self.unsorted.update({tId: tDate}) # add the track data to unsorted list
            self.popped[x] = '{}'.format(str(len(allTracks[x]) -1)) # number of duped tracks
        
        # sort the entire unsorted tracklist
        self.sorted = sorted(self.unsorted.items(), \
            key=lambda x: datetime.datetime.strptime(x[1],'%Y-%m-%d'), reverse=True)
        return [i[0] for i in self.sorted[0:self.plsize]] # return the playlist

    def diff(self, first, second):
        ''' Compare list types '''
        return [item for item in first if item not in second]

    def updateplaylist(self):
        ''' 
        Actuallay fill up the playlist.  
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
                spin.tick(text='[+] {}'.format(track_name(self.tracklist, i)))
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
            return True

        # We dont need to do anything, how have the user even reached this code?
        if len(comparison) == self.plsize:
            spin.tick(text='Playlist doesnt need updating, local list and playlist are the same size. ')
            return True
        
        # Gracefully update the playlist. 
        if len(comparison) > 1:
            spin.tick(text='There are {} new tracks'.format(len(comparison)))
            start_pos = int(self.plsize) - len(comparison)
            for i in set(playlist).difference(current_id):
                spin.tick(text='[+] {}'.format(track_name(self.tracklist, i)))
            for i in comparison:
                spin.tick(text='[-] {}'.format(track_name(self.tracklist, i)))
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
        '''returns details of a single track'''
        return json.dumps(self.sp.track(i), indent=2)