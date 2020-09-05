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
    except Exception:
        artist = 'Unkown artist'
        track = 'unknown track'
        rel_date = '????-??-??'
        pass
    return('({}) {} - {}'.format(rel_date, artist, track).encode('utf-8'))


class Spinner():
    def __init__(self, typ, pp, static=0):
        ''' Possible types:
        notes, penor, arrows, spinner, quarter, box, dna'''
        if static == 1:
            self.s = '\n'
        else:
            self.s = ''
        self.pp = pp # pre text, post text.
        self.type = typ
        self.ticks = 1
        self.text = ''
        self.prevtext = ''
        self.spinner = { 'notes':
            {
        'tick': 8,
        2: '♫        ♪',
        1: ' ♫      ♪ ',
        3: '   ♫  ♪   ',
        4: '    ♫♪    ',
        5: '    ♪♫    ',
        6: '   ♪  ♫   ',
        7: '  ♪    ♫  ',
        8: ' ♪      ♫ ',
            },
        'penor': {
        'tick': 16,
        1: 'D         D',
        2: '=D       Ɑ=',
        3: '==D     Ɑ==',
        4: '===D~  Ɑ===',
        5: '===D ~ Ɑ===',
        6: '===D  ~Ɑ===',
        7: '8===D Ɑ===8',
        8: '===D  ~Ɑ===',
        9: '===D ~ Ɑ===',
        10: '===D~  Ɑ===',
        11: '===D   Ɑ===',
        12: '===D   Ɑ===',
        13: '==D     Ɑ==',
        14: '=D       Ɑ=',
        15: 'D         Ɑ',
        16: '           '
            },
        'dna': {
            'tick': 9,
        1: '|-----------------|',
        2: ' \---------------/ ',
        3: '  ~-_---------_-~  ',
        4: '     ~-_---_-~     ',
        5: '        ~-_        ',
        6: '     _-~---~-_     ',
        7: '  _-~---------~-_  ',
        8: ' /---------------\ ',
        9: '|-----------------|'
            },
        'spinner': {
        'tick': 4,
        1: '|',
        2: '/',
        3: '—',
        4: '\\'
            },
        'arrows': {
            'tick': 8,
            1: '←',
            2: '↖',
            3: '↑',
            4: '↗',
            5: '→',
            6: '↘',
            7: '↓',
            8: '↙'
            },
        'quarter': {
            'tick': 4,
            1: "◜",
            2: "◝",
            3: "◞",
            4: "◟"
            },
        'box': { 'tick': 4,
            1: '◰',
            2: '◳',
            3: '◲',
            4: '◱'
            }
        }

    def tick(self, text):
        self.text = text
        if self.ticks >= self.spinner[self.type]['tick']:
            self.ticks = 1
        space = []
        for x in range(0, len(self.prevtext)):
            space.append(' ')
        print('\r{} {}{}{}'.format(
            self.spinner[self.type][self.ticks] if self.pp is 0 else self.text, 
            self.text if self.pp is 0 else self.spinner[self.type][self.ticks],
            ''.join(space),
            self.s), end='', flush=True
            )
        self.prevtext = text
        self.ticks += 1

    def end(self):
        ''' clear old text, allow for new print to overwrite the spinner once done.'''
        length = len(self.text) + len(self.spinner[self.type][1])
        space = []
        for x in range(0, length):
            space.append(' ')
        print('\r{}'.format(''.join(space)),end='', flush=True)