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

from converters import MultipleConv
import baseaudio

class FastAudioDevice(baseaudio.AudioDevice):

    __implements__ = (interfaces.IAudio,)

    _rdev = None

    def openDev(self):
        if self._rdev is None:
            # Thanks to dotz for putting me on the track of the magic
            # options 160, 2
            self._rdev = FastAudioWrapper(fastaudio.stream(8000, 1,
                                                           'int16', 160, 2))
        self._rdev.open()
        self.dev = MultipleConv(self._rdev)


class FastAudioWrapper(object):
    def __init__(self, f):
        self._f = f
        self.write = f.write
        self.close = f.close
        self.start = f.start
        self.stop = f.stop
        self.buffer = ''

    def open(self):
        self._f.open()
        self._f.start()

    def close(self):
        self._f.stop()
        self._f.close()

    def read(self, length):
        while len(self.buffer) < length:
            self.buffer += self._f.read()
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
