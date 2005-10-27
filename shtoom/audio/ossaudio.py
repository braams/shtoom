# Copyright (C) 2004 Anthony Baxter

import baseaudio, ossaudiodev

# from Twisted
from twisted.python import log
from twisted.internet.task import LoopingCall

opened = None

class OSSAudioDevice(baseaudio.AudioDevice):
    dev = None

    def openDev(self):
        try:
            from __main__ import app
        except:
            app = None
        if app is not None:
            device = app.getPref('audio_device')
        else:
            device = None
        if device is not None:
            log.msg("ossaudiodev opening device %s")
            dev = ossaudiodev.open(device, 'rw')
        else:
            log.msg("ossaudiodev opening default device")
            dev = ossaudiodev.open('rw')
        dev.speed(8000)
        dev.nonblock()
        ch = dev.channels(1)
        if ch not in (1, 2):
            raise ValueError("insane channel count %r"%(ch))
        self._channels = ch
        formats = listFormats(dev)
        if 'AFMT_S16_LE' in formats:
            dev.setfmt(ossaudiodev.AFMT_S16_LE)
            self.dev = dev
        else:
            raise ValueError("Couldn't find signed 16 bit PCM, got %s"%(
                                                    ", ".join(formats)))

        self.LC = LoopingCall(self._push_up_some_data)
        self.LC.start(0.010)

    def _push_up_some_data(self):
        from audioop import tomono
        try:
            data = self.dev.read(320*self._channels)
        except IOError:
            return None
        if self._channels == 2:
            data = tomono(data, 2, 1, 1)
        if self.encoder and data:
            self.encoder.handle_audio(data)

    def write(self, data):
        from audioop import tostereo
        if self._channels == 2:
            data = tostereo(data, 2, 1, 1)
        self.dev.write(data)

    def _close(self):
        if self.isOpen():
            log.msg("ossaudiodev closing")
            try:
                self.LC.stop()
            except AttributeError:
                # workaround a twisted bug
                pass
            del self.LC
            self.dev = None

def listFormats(dev):
    import ossaudiodev as O
    supported = dev.getfmts()
    l = [ x for x in dir(O) if x.startswith('AFMT') ]
    l = [ fmt for fmt in l if getattr(O, fmt) & supported ]
    return l

Device = OSSAudioDevice
