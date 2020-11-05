# Recentlier Releaseder!
A tool that sets up a playlist for you that gives you the latest tracks from the artists you follow on Spotify. 

Unlike spotify's "Recently Released"-list that is dynamically updated based on several algorithms, this tool just gives you the latest tracks from the artists you actually follow. No less, no more. 


**Latest updates**

1.5:
* Rewrote the entire sorting function
* optimized database handling (no more uneccecary database transactions)
* cleaned up unused code 
* changed output charset (utf8)
* Altered output with a spinner. (configurable in config: quarter, dna, penor, arrows, box, notes)
* Fixed a bug where the playlist could only be 50 tracks.
* Added some command line options.



1.4:
Releaseder now creates a local cache of the spotify API. I recommend to delete dump.json and let recentlier build this cache from scratch. 
For all new transactions with spotify API, releaseder will store a local copy of that transaction, so next time recentlier runs, it will not expend transactions on the API, but instead use the locally stored cache. It will always look for new content though.
Will create a new file: cache.db


**Requirements:**
> Python 3.6 and modules: requests, spotipy

**Installing:**
> pip3 install -f requirements.txt

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
cache = yes
spinner = quarter

Set update_interval to 0 to stop looping, otherwise set it in minutes. Be wary of spotifys rate limiting and set it to something reasonable, like 15 minutes or higher.

**note
First time you run the script, it will take a while, because it needs to build the cache database and the dump file, in the next runs it will go conciderably faster. 

**bugs:
If many tracks occupies the same release date, recentlier will sometimes just move tracks around and might append/remove the same tracks over and over again. 
This is only noticable if you rebuild the dumpfile, but shouldnt happen if you just let 
