# Copyright (C) 2004 Anthony Baxter

import baseaudio, ossaudiodev

opened = None

class OSSAudioDevice(baseaudio.AudioDevice):

    def openDev(self):
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

    def read(self):
        from audioop import tomono
        try:
            data = self.dev.read(320*self._channels)
        except IOError:
            return None
        if self._channels == 2:
            data = tomono(data, 2, 1, 1)
        return data

    def write(self, data):
        from audioop import tostereo
        if self._channels == 2:
            data = tostereo(data, 2, 1, 1)
        self.dev.write(data)

def listFormats(dev):
    import ossaudiodev as O
    supported = dev.getfmts()
    l = [ x for x in dir(O) if x.startswith('AFMT') ]
    l = [ fmt for fmt in l if getattr(O, fmt) & supported ]
    return l

Device = OSSAudioDevice
