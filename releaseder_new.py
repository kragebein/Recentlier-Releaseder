#!/usr/bin/python3
''' Recently Releaseder '''
import json, re, requests, spotipy.util, os, sys, time
import spotipy.util as util
from recentlier.spotify import spot
from recentlier.config import conf as _conf
from recentlier.div import _dump, checkforupdate, track_name
import traceback
conf = _conf()
def collect():
    print('Recentlier Releaseder 0.6')
    print('')
    def writedump():
        ''' write the dumpfile '''
        with open('dump.json', 'w') as dumpfile:
            tracklist = json.dumps(collector.tracklist, indent=2, sort_keys=True)
            dumpfile.write(tracklist)
            dumpfile.close()

    dump = _dump()
    found_item = False
    c = 0
    t = 0
    a = 0
    track_data = {}
    albums = []
    buffer = []  
    print('Working with: ', end='')
    for artist in collector.get_artists():
        follow_name = artist['name']
        print('{}, '.format(follow_name), end='', flush=True)
        a +=1
        for album in collector.get_albums(artist['id']):
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
    
                            
    print('')
    if dump and found_item is False:
        print('No new updates found. Not doing anything.')
        return True
    elif not dump and not found_item:
        print('Whoah there.. Couldnt find ANYTHING. Are you sure you are following artists?')
        return True
    elif dump and found_item:
        collector.tracklist.update({'username': collector.username, 'tracks': dump['tracks'], 'albums': dump['albums'], 'popped': dump['popped']}) # Include old dump
        for i in albums:
            collector.tracklist['albums'].append(i)
        for i in track_data:
            collector.tracklist['tracks'].update({i: track_data[i]})
        for i in collector.popped:
            collector.tracklist['popped'].append(i)
        #collector.tracklist.update({'tracks': track_data, 'albums': albums})
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
        return True

#collector = spot()
#print(collector.get_single_track_details('2LeWpFQO55js4AGJwaGzBR'))
#quit()

if int(conf.loop) is not 0:
    minutes = int(conf.loop) * 60
    while True:
        collector = spot()
        collect() #run 
        print('Retrying in {} minutes.'.format(conf.loop))
        time.sleep(minutes)
else:
    collector = spot()
    collect() #run 

if os.name == 'nt':
    input('<ENTER> to close window.')