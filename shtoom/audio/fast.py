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


    def openDev(self):
        self.rdev = FastAudioWrapper(fastaudio.stream(8000, 1, 'int16'))
        self.rdev.open()
        self.rdev.start()
        self.dev = MultipleConv(self.rdev)

    def close(self):
        self.rdev.stop()
        self.dev.close()

class FastAudioWrapper(object):
    def __init__(self, f):
        self._f = f
        self.write = f.write
        self.open = f.open
        self.close = f.close
        self.start = f.start
        self.stop = f.stop
        self.buffer = ''

    def read(self, length):
        if len(self.buffer) < length:
            self.buffer += self.dev.read()
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

