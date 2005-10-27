# Copyright (C) 2004 Anthony Baxter

# from pyalsa
import alsaaudio

# from Shtoom
import baseaudio

# from Twisted
from twisted.python import log
from twisted.internet.task import LoopingCall

import time
import audioop

opened = None
DEFAULT_ALSA_DEVICE = 'default'

class ALSAAudioDevice(baseaudio.AudioDevice):
    writedev = None
    readdev = None

    def __repr__(self):
        return "ALSAAudioDevice %s" % (self.isOpen() and "open" or "closed")

    def openDev(self):
        print "alsa OPEN", self._closed
        try:
            from __main__ import app
        except:
            app = None
        if app is None:
            device = DEFAULT_ALSA_DEVICE
        else:
            device = app.getPref('audio_device', DEFAULT_ALSA_DEVICE)
        log.msg("alsaaudiodev opening device %s" % (device))
        writedev = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK,
                                 alsaaudio.PCM_NONBLOCK, device)
        self.writechannels = writedev.setchannels(1)
        writedev.setrate(8000)
        writedev.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        writedev.setperiodsize(160)
        self.writedev = writedev

        readdev = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,
                                alsaaudio.PCM_NONBLOCK, device)
        self.readchannels = readdev.setchannels(1)
        readdev.setrate(8000)
        readdev.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        readdev.setperiodsize(160)
        self.readdev = readdev

        self.LC = LoopingCall(self._push_up_some_data)
        self.LC.start(0.010)
        print "alsa OPENED", self._closed

    def _push_up_some_data(self):
        if self.readdev is None:
            return
        (l, data,) = self.readdev.read()
        if self.readchannels == 2:
            data = audioop.tomono(data, 2, 1, 1)
        if self.encoder and data:
            self.encoder.handle_audio(data)

    def write(self, data):
        if not hasattr(self, 'LC'):
            return
        assert self.isOpen(), "calling write() on closed %s"%(self,)
        if self.writechannels == 2:
            data = audioop.tostereo(data, 2, 1, 1)
        wrote = self.writedev.write(data)
        if not wrote: log.msg("ALSA overrun")

    def _close(self):
        print "alsa CLOSE", self._closed
        if self.isOpen():
            log.msg("alsaaudiodev closing")
            try:
                self.LC.stop()
            except AttributeError:
                # ? bug in Twisted?  Not sure.  This catch-and-ignore is a temporary workaround.  --Zooko
                pass
            del self.LC
            self.writedev = None
            self.readdev = None
        print "alsa CLOSED", self._closed

Device = ALSAAudioDevice
