# Copyright (C) 2004 Anthony Baxter

import baseaudio, alsaaudio
import traceback
from twisted.python import log

opened = None

class ALSAAudioDevice(baseaudio.AudioDevice):

    def openDev(self):
        log.msg("alsaaudiodev opening")
        writedev = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK,
                                 alsaaudio.PCM_NONBLOCK)
        writedev.setchannels(1)
        writedev.setrate(8000)
        writedev.setperiodsize(160)
        self.writedev = writedev

        readdev = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,
                                alsaaudio.PCM_NONBLOCK)
        readdev.setchannels(1)
        readdev.setrate(8000)
        readdev.setperiodsize(160)
        self.readdev = readdev

    def read(self):
        l,data = self.readdev.read()
        return data

    def write(self, data):
        wrote = self.writedev.write(data)
        if not wrote: log.msg("ALSA overrun")

    def close(self):
        log.msg("alsaaudiodev closing")
        del self.writedev
        del self.readdev

Device = ALSAAudioDevice
