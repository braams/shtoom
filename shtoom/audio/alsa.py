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

    def __init__(self):
        baseaudio.AudioDevice.__init__(self)

    def openDev(self):
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

    def _push_up_some_data(self):
        (l, data,) = self.readdev.read()
        if self.readchannels == 2:
            data = audioop.tomono(data, 2, 1, 1)
        if self.sink and data:
            self.sink.handle_data(data)

    def write(self, data):
        if not hasattr(self, 'LC'):
            return
        assert self.isOpen(), "calling write() on closed %s"%(self,)
        if self.writechannels == 2:
            data = audioop.tostereo(data, 2, 1, 1)
        wrote = self.writedev.write(data)
        if not wrote: log.msg("ALSA overrun")

    def isOpen(self):
        return hasattr(self, 'writedev')

    def close(self):
        if self.isOpen():
            log.msg("alsaaudiodev closing")
            try:
                self.LC.stop()
            except AttributeError:
                # ? bug in Twisted?  Not sure.  This catch-and-ignore is a temporary workaround.  --Zooko
                pass
            del self.LC
            del self.writedev
            del self.readdev

Device = ALSAAudioDevice
