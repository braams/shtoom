Shtoom is a pure-python VoIP client, using SIP.

At the moment it's functionality is pretty limited, but is growing
quickly:

  - Qt user interface (needs to be re-done)
  - Can make simple calls and hang up
  - Uses the G711 ULAW codec by default 

At the moment, something's Not Quite Right in the full duplex handling 
of /dev/audio. Working on it.

If available, it should make use of the itimer module.
http://polykoira.megabaud.fi/~torppa/py-itimer/

