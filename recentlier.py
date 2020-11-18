#!/usr/bin/python3
''' Recently Releaseder '''
# -*- coding: utf-8 -*-
# pylint: disable=no-name-in-module
import json, os, sys, time, codecs, traceback
import spotipy.util as util
from spotipy.client import Spotify 
from recentlier.spotify import spot
from recentlier.config import conf as _conf
from recentlier.div import checkforupdate, Spinner, arguments
from spotipy.client import SpotifyException
from datetime import datetime


# this should allow for non-ascii characters to be printed
if sys.stdout.encoding is None or sys.stdout.encoding == 'ANSI_X3.4-1968':
    utf8_writer = codecs.getwriter('UTF-8')
    if sys.version_info.major < 3:
        sys.stdout = utf8_writer(sys.stdout, errors='replace')
    else:
        sys.stdout = utf8_writer(sys.stdout.buffer, errors='replace')

if len(sys.argv) > 1:
    arguments(sys.argv)

conf = _conf()
checkforupdate()
def collect():
    found_item = False
    c = 0
    t = 0
    a = 0
    track_data = {}
    albums = []
    buffer = []  
    # get artists from followlist
    for artist in collector.get_artists():
        a +=1
        # get albums from artist
        spin.tick(text='parsing {}..'.format(artist['name'])) # loading bar text, leave empty for none
        for album in collector.get_albums(artist['id']):
            # if album has been processed earlier, skip this album.
            albums.append(album['id'])
            album_name = album['name']
            #get tracks from album
            for track in collector.get_tracks(album['id']):
                buffer.append(track['id'])
                if len(buffer) == 50 or len(buffer) >= collector.get_album_tracks_total:
                    # get track details about each track (build buffer) ^
                    for details in collector.get_track_details(buffer):
                        release_date = details['album']['release_date']
                        track_name = details['name']
                        track_id = details['id']
                        for artist in details['artists']:
                            artist_name = artist['name']
                            artist_id = artist['id']
                            c +=1
                            # if main artist is in the list of artists you follow, add to list of tracks to be concidered.
                            if artist_id in collector.follow:
                                found_item = True
                                t +=0
                                track_data.update({track_id: [album['id'], album_name, artist_name, track_name, artist_id, release_date, album['album_type']]})
                                del buffer[:]      
            
    spin.end()
    if found_item == True:
        for i in track_data:
            collector.tracklist['tracks'].update({i: track_data[i]})
        collector.updateplaylist()
        return True
    elif found_item == False:
        return False

    return True if found_item == True else False

def checktime():
    ''' Returns true if timer is reached '''
    if not conf.runtime:
        return False
    now = datetime.now()
    return True if str(now.strftime("%H:%M:%S")) == conf.runtime else False

# loopity whoop
if int(conf.loop) != 0:
    minutes = int(conf.loop) * 60
    spin = Spinner(conf.st, 0)
    while True:
        countdown = minutes
        try:
            collector = spot()
            collect()
        except SpotifyException:
            ''' token has expired, initialize spot again. '''
            collector = spot()
            collect()
        except Exception as r:
            traceback.print_exc() 
        # Spinners for everyone!
        for x in range(0, minutes):
            if countdown == 0:
                break
            for y in range(0, 10): 
                if checktime():
                    countdown = 0
                    break
                # Smoother spinner.
                spin.tick(text='waiting for {}'.format(str(int(countdown/60)) + ' minutes..' if int(countdown/60) >= 1 else str(int(countdown)) + ' seconds..'))
                time.sleep(0.1)
            countdown -= 1
        spin.end()
else:
    collector = spot()
    collect()
