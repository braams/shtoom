Shtoom is a pure-python VoIP client and other applications, using SIP.

At the moment it's functionality is somewhat limited, but is 
growing quickly:

  - Qt, Tk, Gnome, wxWidgets or text user interface (MFC on Windows and 
  Cocoa on OSX coming soon)

  - Can make and receive calls - tested with kphone, linphone, xten and
  cisco AS5x00 running 12.3, as well as with Asterisk and Quotient.

  - Can register with SIP proxies/location services. Tested with
  divmod.com's Quotient, Asterisk, and FWD (http://www.fwd.pulver.com/)

  - Uses the G711 ULAW codec by default, or GSM 06.10 (with additional
  pygsm module installed).

  - It should work on any system with ossaudiodev, or on most other
  systems (with the fastaudio/portaudio module installed, see the
  dependencies section, below)

  - Doug, the shtoom application server, makes it very easy to write
  simple voice applications. 

It's been tested (by me) on Linux (Fedora Core 1) using ossaudio, and 
Windows XP (using portaudio/fastaudio). It _should_ work Mac OS X - but
this is untested so far.

Note that only shtoom itself needs the user interface or audio interfaces.
Doug should work on almost anything.

In addition, there are a number of other programs, including shtam 
(an answering machine/voicemail), shmessage (a simple announcement 
server) and shtoomcu (a conferencing server) XXX shtoomcu not checked
in yet, check back soon.

Dependencies
------------

Note that the Windows installer (offline for now) has all dependencies
included in the installer. You only need these if you're not using the 
windows installer.

Required:

    Python 2.3. It might work on 2.2, but I have no real interest in 
    maintaining that.

    http://www.python.org/2.3.3

    Twisted 1.1.1. Note that Twisted 1.1.1 or later is REQUIRED.

    http://www.twistedmatrix.com/

Optional:

    Portaudio/fastaudio (see below)

    pygsm (see below)

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
shtoom.sf.net website. If someone wants to package up a Mac OSX 
installer, that would be great.

Note that, for me, portaudio doesn't work - I'm using ALSA on Linux.
The python standard ossaudiodev module works fine with ALSA. ALSA is
an optional add-on for Linux kernel version 2.4, but is standard in 
kernel version 2.6.

Note that you don't need to worry about the audio layer if you're
only running doug.

Codecs
======

At the moment G711 ULAW (aka PCMU) is supported with the standard
Python audioop module. If you install Itamar Shtull-Trauring's 
pygsm module (available from shtoom CVS as module 'pygsm', or from the
'Files' section of the shtoom website), it will also handle GSM 06.10. 
Additional codecs will be added later.


Shtoom is (C) Copyright 2004 Anthony Baxter and is licensed under
the GNU Lesser General Public License - see the file LICENSE for
details.

Thanks to folks who've contributed:
   Itamar Shtull-Trauring,
   Jp Calderone,
   Andy Hird,
   Jamey Hicks,
   Amir Bakhtiar,
   Allan Short for much testing and advice

and thanks to everyone on the Twisted project for producing such a 
high quality framework.

Thanks also to Mike Barnes for providing Mac OSX hardware, and Amir
Bakhtiar of Divmod for a UPnP-capable router.

License
-------

This collective work is Copyright (C)2004 by Anthony Baxter.
Individual portions may be copyright by individual contributors, and
are included in this collective work with permission of the copyright 
owners.

The license for this work can be found in the file LICENSE.

