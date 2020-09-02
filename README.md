# Recentlier Releaseder!
A tool that sets up a playlist for you that gives you the latest tracks from the artists you follow on Spotify. 

Unlike spotify's "Recently Released"-list that is dynamically updated based on several algorithms, this tool just gives you the latest tracks from the artists you actually follow. No less, no more. 


**Latest updates**

1.4:
Releaseder now creates a local cache of the spotify API. I recommend to delete dump.json and let recentlier build this cache from scratch. 
For all new transactions with spotify API, releaseder will store a local copy of that transaction, so next time recentlier runs, it will not expend transactions on the API, but instead use the locally stored cache. It will always look for new content though.
Will create a new file: cache.db


**Requirements:**
> Python 3.6 and modules: requests, spotipy

**Installing:**
> pip3 install -f requirements.txt

The tool tries to remove any duplicate tracks from labels that re-upload old songs instead of using the old tracks that already exists.

It works by sifting through every album, every single and every track that your artists have published on spotify, it removes duplicates, sorts it by date and inserts the newest tracks into your list. 

A json dump of the albums and tracks are stored locally and will be used the next time recentlier is beeing run. Delete it to start fresh.

**Files created locally:**
> .user  
dump.json  
.cache-\<username\>  
cache.db

There is also a small configuration file which will be created the first time you run recentlier.
It will stop execution after first time run to let you enter the client secret and client id in the config.

>[PLAYLIST]  
name = Recentlier Releaseder  
size = 30  
[APPLICATION]  
update_interval = 0  
client_secret =   
client_id =   
callback =   

Set update_interval to 0 to stop looping, otherwise set it in minutes. Be wary of spotifys rate limiting and set it to something reasonable, like 15 minutes.