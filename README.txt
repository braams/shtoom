Shtoom is a pure-python VoIP client, using SIP.

At the moment it's functionality is pretty limited, but is growing
quickly:

  - Qt or Tk user interface (others coming soon)
  - Can make simple calls and hang them up - tested with kphone, linphone and
    cisco AS5x00 running 12.3(3a).
  - Uses the G711 ULAW codec by default 
  - It should work on any system with ossaudiodev, or on most other
    systems (with the fastaudio/portaudio module installed, see the
    dependencies section, below)

Dependencies
------------

Audio
-----

At the moment, it uses either ossaudiodev, which should work on
Linux and FreeBSD, or fastaudio, which should work on 
'Windows, Macintosh (8,9,X), Unix (OSS), SGI, and BeOS'

It requires the PortAudio library, from 
http://www.portaudio.com/
and the fastaudio wrapper for PortAudio, available from 
http://www.freenet.org.nz/python/pyPortAudio/

Windows installer for Python2.3 fastaudio is available from the 
shtoom.sf.net website.

Note that, for me, portaudio doesn't work - I'm using ALSA on linux.
The audio produced by portaudio/fastaudio looks like 16 bit linear 
PCM - need to convert (using audioop.lin2ulaw? Does this get distributed
with Mac and Windows installers of Python?)

Other dependencies
------------------

If available, it will make use of the itimer module.
http://polykoira.megabaud.fi/~torppa/py-itimer/
It's currently unclear if this is still necessary, after Jp Calderone's
new LoopingCall construct seems to be getting just as good a result.


Shtoom is (C) Copyright 2003 Anthony Baxter and is licensed under
the GNU Lesser General Public License - see the file LICENSE for
details.

Thanks to folks who've contributed:
   Itamar Shtull-Trauring
   Jp Calderone
and thanks to everyone on the Twisted project for producing such a 
high quality framework.

Thanks also to Mike Barnes for providing Mac OSX hardware, and Amir
Bakhtiar of Divmod for a UPnP-capable router.

