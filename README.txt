Shtoom is a pure-python VoIP client, using SIP.

At the moment it's functionality is pretty limited, but is growing
quickly:

  - Qt or Tk user interface (others coming soon)
  - Can make simple calls and hang them up
  - Uses the G711 ULAW codec by default 

If available, it will make use of the itimer module.
http://polykoira.megabaud.fi/~torppa/py-itimer/

At the moment, it uses either ossaudiodev, which should work on
Linux and FreeBSD, or fastaudio, which should work on 
'Windows, Macintosh (8,9,X), Unix (OSS), SGI, and BeOS'
It requires the PortAudio library, from 
http://www.portaudio.com/
and the fastaudio wrapper for PortAudio, available from 
http://www.freenet.org.nz/python/pyPortAudio/

Shtoom is (C) Copyright 2003 Anthony Baxter and is licensed under
the GNU Lesser General Public License - see the file LICENSE for
details.

Thanks to folks who've contributed:
   Itamar Shtull-Trauring
   Jp Calderone
and thanks to everyone on the Twisted project for producing such a 
high quality framework.
