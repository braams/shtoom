# Copyright (C) 2004 Anthony Baxter

from converters import MediaLayer
import baseaudio, ossaudiodev

opened = None

class OSSAudioDevice(baseaudio.AudioDevice):
    dev = None

    def openDev(self):
        import ossaudiodev
        dev = ossaudiodev.open(self._mode)
        dev.speed(8000)
        dev.nonblock()
        # Some devices, even using ALSA, will only do stereo! Suckage.
        ch = dev.channels(1)
        formats = listFormats(dev)
        if not self._wrapped:
            self.dev = dev
        if 'AFMT_S16_LE' in formats:
            dev.setfmt(ossaudiodev.AFMT_S16_LE)
            if self.dev is None:
                self.dev = MediaLayer(Wrapper(dev, ch))
            else:
                self.dev.setDevice(Wrapper(dev, ch))
        else:
            raise ValueError, \
                "Couldn't find signed 16 bit PCM, got %s"%(
                ", ".join(formats))

class Wrapper:
    def __init__(self, d, channels=1):
        self._d = d
        if channels not in (1, 2): 
            raise ValueError, channels
        self._channels = channels
        self.write = self._d.write
        self.close = self._d.close

    def read(self):
        from audioop import tomono
        try:
            data = self._d.read(320*self._channels)
        except IOError:
            return None
        if self._channels == 2:
            data = tomono(data, 2, 1, 1)
        return data

    def write(self, data):
        from audioop import tostereo
        if self._channels == 2:
            data = tostereo(data, 2, 1, 1)
        self._d.write(data)

    def __getattr__(self,a):
        return getattr(self._d, a)

def getAudioDevice(mode, wrapped=1):
    global opened
    if opened is None:
        opened = OSSAudioDevice(mode, wrapped)
    else:
        if opened.isClosed():
            opened.reopen()
    return opened


def listFormats(dev):
    import ossaudiodev as O
    supported = dev.getfmts()
    l = [ x for x in dir(O) if x.startswith('AFMT') ]
    l = [ fmt for fmt in l if getattr(O, fmt) & supported ]
    return l

def test():
    dev = getAudioDevice('rw', wrapped=0)
    print "got device", dev
    print "supports", ", ".join(listFormats(dev))

if __name__ == "__main__":
    test()
