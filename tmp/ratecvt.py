"""
    Testbed code for getting audio conversion on the Mac to work
"""
import numarray, ossaudiodev, time, audioop

# This generates a sine wave in the same format as Donovan's 
# coreaudio module's format

HZ = 44100
OUTHZ = 8000

class SineGenerator:
    freq = 440.0
    offset = 0 

    def callback(self, buffer):
        from math import sin
        offset = self.offset
        self.offset += 512
        for frame in xrange(512):
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
        buffer = audioop.stereo(buffer, 2, 1, 1)
        b, self.fromstate = audioop.ratecv(b, 2, 2, OUTHZ, HZ, self.fromstate)
        buffer = fromstring(x, Int16)
        buffer = buffer.astype(Float32)
        buffer = ( buffer + 32768/2 ) / self.SCALE
        return buffer
        


def main():
    buffer = numarray.array([0.0]*1024)
    dev = ossaudiodev.open('w')
    dev.speed(OUTHZ)
    dev.nonblock()
    dev.channels(1)
    dev.setfmt(ossaudiodev.AFMT_S16_LE)
    sine = SineGenerator()
    cvt = MacConverter()
    while True:
        # get more audio
        sine.callback(buffer)
        out = cvt.cvt(buffer)
        dev.write(out)

if __name__ == "__main__":
    main()
