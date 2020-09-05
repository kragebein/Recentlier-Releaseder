#!/usr/bin/python3
''' Recently Releaseder '''
# pylint: disable=no-name-in-module
import json, re, requests, spotipy.util, os, sys, time
import spotipy.util as util
from spotipy.client import Spotify 
from recentlier.spotify import spot
from recentlier.config import conf as _conf
from recentlier.div import _dump, checkforupdate, track_name, Spinner
from spotipy.client import SpotifyException
from datetime import datetime
import traceback

conf = _conf()
checkforupdate()
def collect():
    def writedump():
        ''' write the dumpfile '''
        with open('dump.json', 'w') as dumpfile:
            # We Lets sort and set up indent for this
            tracklist = json.dumps(collector.tracklist, indent=2, sort_keys=True)
            dumpfile.write(tracklist)
            dumpfile.close()
    dump = _dump()
    spin = Spinner('dna', 0, static=0)
    found_item = False
    c = 0
    t = 0
    a = 0
    track_data = {}
    albums = []
    buffer = []  
    for artist in collector.get_artists():
        a +=1
        for album in collector.get_albums(artist['id']):
            spin.tick(text='parsing {}..'.format(album['name'])) # loading bar text, leave empty for none
            if dump:
                if album['id'] in dump['albums']:
                    break
            albums.append(album['id'])
            album_name = album['name']
            for track in collector.get_tracks(album['id']):
                buffer.append(track['id'])
                if len(buffer) == 50 or a <= len(collector.follow): #build buffer or wait until last iteration
                    for details in collector.get_track_details(buffer):
                        release_date = details['album']['release_date']
                        track_name = details['name']
                        track_id = details['id']
                        for artist in details['artists']:
                            artist_name = artist['name']
                            artist_id = artist['id']
                            c +=1
                            if artist_id in collector.follow:
                                found_item = True
                                t +=0
                                track_data.update({track_id: [album['id'], album_name, artist_name, track_name, artist_id, release_date, album['album_type']]})
                                del buffer[:]      
            
    spin.end()                    
    if dump and found_item is False:     
        print('\r{}: Nothing new.'.format(
            datetime.now().strftime(
                "%X %x" 
                )
            )
        )
        return False
    elif not dump and not found_item:
        print('Whoah there.. Couldnt find ANYTHING. Are you sure you are following artists?')
        return False
    elif dump and found_item:
        collector.tracklist.update({'username': collector.username, 'tracks': dump['tracks'], 'albums': dump['albums'], 'popped': dump['popped']}) # Include old dump
        for i in albums:
            collector.tracklist['albums'].append(i)
        for i in track_data:
            collector.tracklist['tracks'].update({i: track_data[i]})
        for i in collector.popped:
            collector.tracklist['popped'].append(i)
        collector.updateplaylist()
        writedump()
        return True
    elif not dump and found_item:
        collector.tracklist.update({'username': collector.username, 'tracks': track_data, 'albums': albums, 'popped': collector.popped})
        collector.updateplaylist()
        writedump()
        return True
    else:
        print('We met an unkonwn condition, exiting')
        return False
# loopity whoop
if int(conf.loop) != 0:
    minutes = int(conf.loop) * 60
    spin = Spinner('dna', 0)
    while True:
        countdown = minutes
        try:
            collector = spot()
            collect()
        except SpotifyException:
            ''' token has expired, we think lets do this again '''
            collector = spot()
            collect()
        except Exception as r:
            traceback.print_exc() 
        # Spinners for everyone!
        for x in range(0, minutes): 
            if countdown == 0:
                break
            for y in range(0, 10): 
                # Smoother spinner.
                spin.tick(text='waiting for {}'.format(str(int(countdown/60)) + ' minutes..' if int(countdown/60) >= 1 else str(int(countdown)) + ' seconds..'))
                time.sleep(0.1)
            countdown -= 1
        spin.end()
else:
    collector = spot()
    collect()

if os.name == 'nt':
    input('Press enter to close window.')