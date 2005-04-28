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

# from Twisted
from twisted.python import log
from twisted.internet.task import LoopingCall

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

            self.LC = LoopingCall(self._push_up_some_data)
            self.LC.start(0.010)

    def write(self, bytes):
        if bytes:
            self.dev.write(bytes)

    def open(self):
        self.dev.open()
        self.dev.start()

    def close(self):
        if self.isOpen():
            log.msg("fastaudiodev closing")
            try:
                self.LC.stop()
            except AttributeError:
                # ? bug in Twisted?  Not sure.  This catch-and-ignore is a temporary workaround.  --Zooko
                pass
            del self.LC
            baseaudio.AudioDevice.close(self)
            del self.dev

    def _push_up_some_data(self):
        if hasattr(self, 'encoder') and self.encoder:
            data = self._f.read()
            while data:
                self.encoder.handle_audio(data)
                data = self._f.read()

Device = FastAudioDevice
