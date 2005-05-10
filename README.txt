Shtoom is a pure-python VoIP client and other applications, using SIP.

READ THIS FIRST
===============

If you are reporting a bug, at a minimum, include the output of
the script "shtoominfo.py" (it's in the scripts directory). Any 
bugs reported without this are likely to just get a response saying
"please run this script and include the output". There's also a lot
of information in the file DEBUGGING.txt - particularly on the
subjects of firewalls/NATs and audio. Please make sure you've read
this before reporting a bug.

Highlights
----------

At the moment it's functionality is not complete, but is growing quickly:

  - Qt, Tk, Gnome, wxWidgets, Cocoa or text user interface 

  - Can make and receive calls - tested with kphone, linphone, xten and
  cisco AS5x00 running 12.3, as well as with Asterisk and Quotient.

  - Can register with SIP proxies/location services. Tested with
  divmod.com's Quotient, Asterisk, and FWD (http://www.fwd.pulver.com/)

  - Uses the G711 ULAW codec by default, GSM 06.10 or Speex
  (GSM and Speex require an additional python module, see below)

  - It should work on any system with ossaudiodev, CoreAudio (OSX),
  ALSA (many systems), or on most other systems (with the 
  fastaudio/portaudio module installed, see the dependencies section, 
  below)

  - Doug, the shtoom application server, makes it very easy to write
  simple voice applications. 

It's known to work on the following platforms:

  Linux (Fedora Core, Ubuntu)
  Windows XP
  Mac OS X 10.3
  Solaris (server side only so far)

Note that only shtoom itself needs the user interface or audio interfaces.
Doug should work on almost anything.

In addition, there are a number of other programs, including shtam 
(an answering machine/voicemail), shmessage (a simple announcement 
server) and shtoomcu (a conferencing server).

Further Reading
---------------

The paper "Scripting Language My Arse" was presented at PyCon 2004, and 
again in an expanded and updated form as a keynote for OSDC 2005. The latter
paper and slides are available from 

      http://www.interlink.com.au/anthony/tech/talks/OSDC/

Dependencies
------------

Note that the Windows installer (offline for now) has all dependencies
included in the installer. You only need these if you're not using the 
windows installer.

Required:

    Python 2.3. It might work on 2.2, but I have no real interest in 
    maintaining that. 2.4 is better, of course.

    http://www.python.org/2.3.4

    Twisted 1.3. Note that Twisted 1.3 or later is REQUIRED.

    http://www.twistedmatrix.com/

Optional:

    Portaudio/fastaudio (see below)

    pygsm (see below)

    pySpeex. This is needed for the speex codec, but not required otherwise.

    http://www.freenet.org.nz/python/pySpeex/

    python ALSA interface
        The state of audio on Linux is terrible. The ALSA interface is
        much better, use it if you can. See the large amounts of ranting
        in the DEBUGGING.txt file for more.
        svn://divmod.org/svn/Shtoom/trunk/audio/pyalsaaudio

    numarray
        Numarray is required if you want Doug to be able to do inband
        DTMF detection. If you don't know what this means, you probably
        don't care.

    CocoaShtoom

On Ubuntu Hoary, most of the above are already packaged for you - get the
packages python2.4-alsaaudio, python2.4-pygsm, python2.4-numarray, 
python2.4-numarray-ext and python2.4-speex.

Audio
=====

At the moment, it uses either ossaudiodev, which should work on
Linux and FreeBSD, ALSA, which will work on a range of unix-like
systems, CoreAudio (OS X) or fastaudio, which should work on 
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
pygsm module (available from shtoom SVN as module 'pygsm', or from the
'Files' section of the shtoom.sf.net website), it will also handle 
GSM 06.10. 

If you install David McNab's pySpeex package, you can handle speex 
audio.


Debugging, Troubleshooting, &c
------------------------------

See the DEBUGGING.txt file.

Credits
-------

Shtoom is (C) Copyright 2004 Anthony Baxter and is licensed under
the GNU Lesser General Public License - see the file LICENSE for
details.

Thanks to the folks who've contributed - I've broken the contributor
list out into the file doc/ACKS.

Thanks also to everyone on the Twisted project for producing such a 
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

