# Copyright (C) 2004 Anthony Baxter

from converters import MultipleConv
import baseaudio, ossaudiodev

opened = None

class OSSAudioDevice(baseaudio.AudioDevice):
    def openDev(self):
        import ossaudiodev
        dev = ossaudiodev.open(self._mode)
        dev.speed(8000)
        dev.nonblock()
        dev.channels(1)
        formats = listFormats(dev)
        if not self._wrapped:
            self.dev = dev
        if 'AFMT_S16_LE' in formats:
            dev.setfmt(ossaudiodev.AFMT_S16_LE)
            self.dev = MultipleConv(Wrapper(dev))
        else:
            raise ValueError, \
                "Couldn't find signed 16 bit PCM, got %s"%(
                ", ".join(formats))

class Wrapper:
    def __init__(self, d):
        self._d = d
        self.write = self._d.write

    def read(self):
        return self._d.read(320)

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
