# Recentlier Releaseder!
A tool that sets up a playlist for you that gives you the latest tracks from the artists you follow on Spotify. 

Unlike spotify's "Recently Released"-list that is dynamically updated based on several algorithms, this tool just gives you the latest tracks from the artists you actually follow. No less, no more. 

> Requirements: Python 3.6 and modules: requests, spotipy

*Installing:*
> pip3 install -f requirements.txt

The tool tries to remove any duplicate tracks from labels that re-upload old songs instead of using the old tracks that already exists.

It works by sifting through every album, every single and every track that your artists have published on spotify, it removes duplicates, sorts it by date and inserts the newest tracks into your list. 

A json dump of the albums and tracks are stored locally and will be used the next time recentlier is beeing run. Delete it to start fresh.

 Files created locally:
> .user, dump.json, .cache-\<username\>

There is also a small configuration file which will be created the first time you run recentlier.
It will stop execution after first time run to let you enter the client secret and client id in the config.

>[PLAYLIST]  
name = Recentlier Releaseder  
size = 30  
[APPLICATION]  
update_interval = 0
client_secret = 
client_id = 

Set update_interval to 0 to stop looping, otherwise set it in minutes. Be wary of spotifys rate limiting and set it to something reasonable, like 15 minutes.