#!/usr/bin/python3
''' Configuration handling '''
import configparser, os
class conf():
    file = 'config.ini'
    config = configparser.ConfigParser()
    def __init__(self):
        if not os.path.exists(self.file):
            print('{} not found, creating default config..'.format(self.file))
            self.config['PLAYLIST'] = {'name' : 'Recentlier Releaseder','size' :30}
            self.config['APPLICATION'] = {'update_interval': 0}
            with open(self.file, 'w') as configfile:
                self.config.write(configfile)
        self.config.read(self.file)
        application = self.config['APPLICATION']
        playlist = self.config['PLAYLIST']
        self.playlist_name = playlist['name']
        self.playlist_size = playlist['size']
        self.loop = application['update_interval']
