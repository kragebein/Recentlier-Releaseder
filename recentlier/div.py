#!/usr/bin/python3
''' Some other classes '''
import os, re, json, requests
from recentlier.config import conf

def _dump():
    '''tries to load already parsed data'''
    if os.path.exists('dump.json'):
        with open('dump.json', 'r') as dumpfile:
            dump = json.loads(dumpfile.read())
            return dump
    else:
        return False

def checkforupdate():
    config = conf()
    with open('version', 'r') as version:
        version = json.loads(version.read())
    version = version['version']
    plname = config.playlist_name

    def update(update):
        newversion = update['version']
        if newversion > version:
            print('{} v{}\nNew version available: v{}\nGet it here: https://github.com/kragebein/Recentlier-Releaseder'.format(plname, version, newversion))
        else:
            print(plname + ' v' + version)
    try:
        f = requests.get('https://raw.githubusercontent.com/kragebein/Recentlier-Releaseder/master/version')
        upt = f.json()
    except:
        pass
    try:
        update(upt)
    except:
        print(plname + ' v' + version)

def track_name(list, i):
    ''' Print the the track data from the list'''
    #track_data.update({track_id: [album['id'], album_name, artist_name, track_name, artist_id, release_date, album['album_type']]})
    try:
        artist = list['tracks'][i][2]
        track = list['tracks'][i][3]
        rel_date = list['tracks'][i][5]
    except:
        artist = 'Unkown artist'
        track = 'unknown track'
        rel_date = '?'
        pass
    return('({}) {} - {}'.format(rel_date, artist, track))