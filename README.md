# gmusicclient: a command line interface for streaming Google Play Music

gmusicclient provides a shell like interface into the Google Play Music API and provides the basic media player controls associated with the service.

The client is built using the [cmdln](https://github.com/trentm/cmdln) module in Python to build the shell like prompt. The commands are documented through [cmdln](https://github.com/trentm/cmdln)'s builtin help functionality.

Available commands and their usage may change at any time regardless of this README, but here is a snapshot of the help output of the client.

```
gmusic$ help
gmusicplayer: Google Play Music Command Line Client

Commands:
    dislike (d)        set the rating of a track to 1
    exit
    help (?)           give detailed help on a specific sub-command
    like (l)           set the rating of a track to 5
    next (>)           skip this song and move to the next in the queue
    pause              pause the current track
    play
    playlist           list all playlists
    prev (<)           go to the previous song
    quality            set quality to one of low,med,hi
    queue              print the current play queue
    radio              lookup radio stations based on a track, album, artis...
    rate               rate a track from 1 to 5 (1=Dislike/Thumbs Down, 5=L...
    search (s)         Search the All-Access Database for tracks or Search ...
    seek               go to a position in the song. Format should be decim...
    shuffle            shuffle the current queue
    status             retrieve the status of the streaming service
    stream (st, stat)  stream a track, playlist or radio station
    toggle (p)         toggle play vs pause for the current track.
    volume (v)         set the volume between 0 and 1
```

Dependencies
------------

You can use the provided `requirements.txt` file to setup a working environment. `pip` will not install pygobject directly. You have to manually install pygobject either from a system package manager or through the git repository like so:

```
pip install git+https://git.gnome.org/browse/pygobject
```
