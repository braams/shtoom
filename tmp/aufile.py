import ossaudiodev
import wave, sunau
from audioop import tomono, lin2lin, ulaw2lin, ratecv

import struct
if struct.pack("h", 1) == "\000\001":
    big_endian = 1
else:
    big_endian = 0

class BaseFile:
    _cvt = lambda s, x: x
    _freqCvt = { 8000: 160, 16000: 320, 32000: 640, 64000: 1280 }

    def __init__(self, fp):
        self.fp = self.module.open(fp, 'rb')
        p = self.fp.getparams()
        print p
        if (p[4] not in self.allowedComp):
            raise ValueError("Incorrect file format %r"%(p,))
        self.comptype = p[4]
        if p[0] == 2:
            self._cvt = lambda s, x, c=self._cvt: audiop.tomono(c(x))
        elif p[0] != 1:
            raise ValueError("can only handle mono/stereo, not %d"%p[0])
        if p[1] != 2:
            self._cvt = lambda s,x,ch=p[1],c=self._cvt: lin2lin(c(x),ch,2)
        self.sampwidth = p[1]
        if p[2] % 8000 != 0:
            raise ValueError("sampfreq must be multiple of 8k")
        self.sampfreq = p[2]
        if p[2] != 8000:
            print "rate conversion"
            self._ratecvt = None
            self._cvt = lambda x,c=self._cvt: self.rateCvt(c(x))

    def rateCvt(self, data):
        data, self._ratecvt = ratecv(data,2,1,self.sampfreq,8000,self._ratecvt)
        return data

    def read(self):
        data = self.fp.readframes(160 * (self.sampfreq/8000))
        data = self._cvt(data)
        return data

class WavFile(BaseFile):
    module = wave
    allowedComp = ('NONE','ULAW')

class AuFile(BaseFile):
    module = sunau
    allowedComp = ('ULAW','NONE')

    def endianCvt(self, data):
        import array
        _array_fmts = None, None, 'h', None, 'l'

        if self.comptype == 'ULAW' or big_endian:
            return data

        if _array_fmts[self.sampwidth]:
            arr = array.array(_array_fmts[self.sampwidth]) 
            arr.fromstring(data)
            arr.byteswap()
            data = arr.tostring()

        return data

    _cvt = endianCvt

def getdev():
    dev = ossaudiodev.open('rw')
    dev.speed(8000)
    dev.nonblock()
    ch = dev.channels(1)
    dev.setfmt(ossaudiodev.AFMT_S16_LE)
    return dev


def main(filename):
    dev = getdev()
    if filename.lower().endswith('.wav'):
        audio = WavFile(open(filename, 'rb'))
    elif filename.lower().endswith('.au'):
        audio = AuFile(open(filename, 'rb'))
    while True:
        data = audio.read()
        dev.write(data)
        if len(data) < 320:
            print "stopping because data len == %d"%(len(data))
            break


if __name__ == "__main__":
    import sys
    main(sys.argv[1])

