"""Use fastaudio, a python wrapper for PortAudio.

Apparently this means it'll work on 'Windows, Macintosh (8,9,X),
Unix (OSS), SGI, and BeOS'. It doesn't work for me using ALSA's
OSS emulation.

Requires fastaudio.tar.gz and PortAudio available from
http://www.freenet.org.nz/python/pyPortAudio/
"""

# system imports
import fastaudio

# sibling imports
import interfaces

from converters import MediaLayer
import baseaudio

class FastAudioDevice(baseaudio.AudioDevice):

    __implements__ = (interfaces.IAudio,)

    _rdev = None
    dev = None

    def openDev(self):
        if self._rdev is None:
            # Thanks to dotz for putting me on the track of the magic
            # options 160, 2
            self._rdev = FastAudioWrapper(fastaudio.stream(8000, 1,
                                                           'int16', 160, 2))
        self._rdev.open()
        if self.dev is None:
            self.dev = MediaLayer(self._rdev)
        else:
            self.dev.setDevice(self._rdev)


class FastAudioWrapper(object):
    def __init__(self, f):
        self._f = f
        #self.write = f.write
        self.close = f.close
        self.start = f.start
        self.stop = f.stop
        self.buffer = ''

    def write(self, bytes):
        if bytes:
            self._f.write(bytes)

    def open(self):
        self._f.open()
        self._f.start()

    def close(self):
        self._f.stop()
        self._f.close()

    def read(self, length=320):
        fc = 0
        while len(self.buffer) < length:
            nb = self._f.read()
            if nb:
                self.buffer += nb
            else:
                fc += 1
                if fc > 4:
                    # just give up, for now
                    print "audio is not ready. wah"
                    return ''
        result, self.buffer = self.buffer[:length], self.buffer[length:]
        return result

opened = None

def getAudioDevice(mode):
    global opened
    if opened is None:
        opened = FastAudioDevice(mode)
    if opened.isClosed():
        opened.reopen()
    return opened
