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
import baseaudio

class FastAudioDevice(baseaudio.AudioDevice):

    def openDev(self):
        if self.dev is None:
            # Thanks to dotz for putting me on the track of the magic
            # options 160, 2
            fdev = FastAudioWrapper(fastaudio.stream(8000, 1, 'int16', 160, 2))
            fdev.open()
            self.dev = fdev
            self.close = fdev.close
            self.start = fdev.start
            self.stop = fdev.stop
            self.buffer = ''

    def write(self, bytes):
        if bytes:
            self.dev.write(bytes)

    def open(self):
        self.dev.open()
        self.dev.start()

    def close(self):
        self.dev.stop()
        self.dev.close()

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

Device = FastAudioDevice
