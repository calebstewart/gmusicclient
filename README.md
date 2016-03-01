# gmusicclient: a command line interface for streaming Google Play Music

gmusicclient provides a shell like interface into the Google Play Music API and provides the basic media player controls associated with the service.

The client is built using the [cmdln](https://github.com/trentm/cmdln) module in Python to build the shell like prompt. The commands are documented through [cmdln](https://github.com/trentm/cmdln)'s builtin help functionality.

Putting any available commands or their usage here seems silly, considering they could change easily at any point without regard to this README. As such, you may see the command listing and usage information by simply running the client.

All dependencies should be available through either [pip] or [easy_install]. The dependencies are listed below.

Dependencies
------------
  * [gmusicapi](https://github.com/simon-weber/gmusicapi)
  * [cmdln](https://github.com/trentm/cmdln)
  * [texttable](https://github.com/foutaise/texttable)
  * [getpass](https://docs.python.org/2/library/getpass.html)
  * [colorama](https://github.com/tartley/colorama)