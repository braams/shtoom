Shtoom is a pure-python VoIP client, using SIP.

At the moment it's functionality is pretty limited, but is growing
quickly:

  - Qt, Tk, Gnome or text user interface (others coming soon)
  - Can make simple calls and hang them up - tested with kphone, linphone and
    cisco AS5x00 running 12.3(3a), as well as with Asterisk and Quotient
  - Can receive calls
  - Uses the G711 ULAW codec by default, or GSM 06.10 (with additional
    pygsm module installed).
  - It should work on any system with ossaudiodev, or on most other
    systems (with the fastaudio/portaudio module installed, see the
    dependencies section, below)

Dependencies
------------

Audio
=====

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

Codecs
======

At the moment G711 ULAW (aka PCMU) is supported with the standard
Python audioop module. If you install Itamar Shtull-Trauring's 
pygsm module (available from shtoom CVS as module 'pygsm', it will
also handle GSM 06.10. Additional codecs will be added later.




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

