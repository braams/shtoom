"""
    Testbed code for getting audio conversion on the Mac to work
"""
import numarray, ossaudiodev, time, audioop

# This generates a sine wave in the same format as Donovan's 
# coreaudio module's format

HZ = 44100
OUTHZ = 8000
SAMPLESIZE = 1024

class SineGenerator:
    freq = 440.0
    offset = 0 

    def callback(self, buffer):
        from math import sin
        offset = self.offset
        self.offset += SAMPLESIZE
        for frame in xrange(SAMPLESIZE):
            v = 0.5 * sin(3.1415*self.freq/HZ*(frame+offset))
            # Stereo
            buffer[2*frame] = v
            buffer[2*frame+1] = v

class CoreAudioConverter:
    """ converts from mac format (an array of 32-bit stereo float values(!)) 
        to signed little endian 16 bit mono 
    """
    tostate = None
    fromstate = None
    SCALE = 32768/2
    def toStdFmt(self, buffer):
        b = buffer * self.SCALE - self.SCALE/2
        b = b.astype(numarray.Int16)
        # Damn. Endianness?  
        b = b.tostring() 
        b, self.tostate = audioop.ratecv(b, 2, 2, HZ, OUTHZ, self.tostate)
        b = audioop.tomono(b, 2, 1, 1)
        return b

    def fromStdFmt(self, buffer):
        from numarray import fromstring, Int16, Float32
        b = audioop.tostereo(buffer, 2, 1, 1)
        b, self.fromstate = audioop.ratecv(b, 2, 2, OUTHZ, HZ, self.fromstate)
        b = fromstring(b, Int16)
        b = b.astype(Float32)
        b = ( b + 32768/2 ) / self.SCALE
        return b
        


def main():
    buffer = numarray.array([0.0]*SAMPLESIZE*2)
    dev = ossaudiodev.open('w')
    dev.speed(OUTHZ)
    dev.nonblock()
    dev.channels(1)
    dev.setfmt(ossaudiodev.AFMT_S16_LE)
    sine = SineGenerator()
    cvt = CoreAudioConverter()
    while True:
        # get more audio
        sine.callback(buffer)
        out = cvt.toStdFmt(cvt.fromStdFmt(cvt.toStdFmt(buffer)))
        dev.write(out)

if __name__ == "__main__":
    main()
