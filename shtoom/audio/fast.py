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

from converters import PCM16toULAWConv
import baseaudio

class FastAudioDevice(baseaudio.AudioDevice):

    __implements__ = (interfaces.IAudio,)

    def read(self, length):
        self.buffer += self.dev.read()
        result, self.buffer = self.buffer[:length], self.buffer[length:]
        return result

    def openDev(self):
        self.dev = PCM16toULAWConv(fastaudio.stream(8000, 1, 'int16'))

opened = None

def getAudioDevice(mode):
    global opened
    if opened is None:
        opened = FastAudioDevice(mode, wrapped)
    else:
        if opened.isClosed():
            opened.reopen()
    return opened

