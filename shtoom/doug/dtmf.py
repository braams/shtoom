"""
    Extraordinarily brutal DTMF detection code. This is just
    "something that works". Anyone who's got a better grasp
    of signal processing than me (which wouldn't be hard - I
    last studied it 12 years ago, and haven't touched it since
    then) is encouraged to suggest a better approach. I'm not
    that happy with the getpeaks() code, to be honest the 8 times
    greater than average level seems somehow hacky. If you are
    interested, let me know and I can provide you with some sample
    files to experiment on.
"""

# DTMF tones (aka "the beeps when you hit a keypad consist of a pair
# of sine waves. The table of the sine waves is:

#             1209   1336   1477   1633    scaled
#         697   1      2      3      A     27.88
#         770   4      5      6      B     30.8
#         852   7      8      9      C     34.08
#         941   *      0      #      D     37.64
# scaled      48.36  53.44  59.08  65.32

# 'scaled' is the number divided by 25 - since we're examining
# 40ms of audio at a time (1/25th of a second).

HZ = 8000.0

freq2dtmf = {
        (697,1209):'1', (697,1336):'2',(697,1477):'3',(697,1633):'A',
        (770,1209):'4', (770,1336):'5',(770,1477):'6',(770,1633):'B',
        (852,1209):'7', (852,1336):'8',(852,1477):'9',(852,1633):'C',
        (941,1209):'*', (941,1336):'0',(941,1477):'#',(941,1633):'D',
             }

dtmf2freq = {}
for f, d in freq2dtmf.items():
    dtmf2freq[d] = f
del f, d
    
import sets
frequencies = freq2dtmf.keys()
frequencies = sets.Set([ x[0] for x in frequencies ] + 
                       [ x[1] for x in frequencies ])

def getSineWave(freq, samplecount=320):
    """ Generate a sine wave of frequency 'freq'. The samples are
        generated at 8khz. The first 'samplecount' samples will be
        returned.
    """
    from numarray import sin, arange
    from math import pi
    sine = sin(arange(HZ)/(HZ/freq) * 2.0 * pi)
    sine = sine[:samplecount]
    return sine


class DtmfDetector:
    "This class detects DTMF tones from an audio stream."
    def __init__(self):
        # Store away pre-calculated FFTs for each of the eight frequencies.
        self.freqmatch = {}
        self.dtmf = freq2dtmf
        for val in frequencies:
            sine = getSineWave(val)
            peaks = self.getpeaks(sine)
            for peak in peaks:
                self.freqmatch[peak] = val

    def detect(self, sample):
        """ Test for DTMF in a sample. Returns either a string with the
            DTMF digit, or the empty string if none is present. Accepts
            a string of length 640, representing 320 16 bit signed PCM
            samples (host endianness). This is _two_ samples at normal
            shtoom sampling rates.
        """
        import numarray
        from sets import Set
        a = numarray.fromstring(sample, numarray.Int16)
        if len(a) != 320:
            raise ValueError("samples length %d != 320 (40ms)"%len(a))
        peaks = self.getpeaks(a)
        matched = Set()
        for p in peaks:
            m = self.freqmatch.get(p)
            if m is None:
                if p-1 in peaks:
                    m = self.freqmatch.get(p-1)
                elif p+1 in peaks:
                    m = self.freqmatch.get(p+1)
            matched.add(m)
        # If we got a None, that means there was a significant component
        # that wasn't a DTMF frequency.
        if None in matched:
            return ''
        else:
            m = list(matched)
            m.sort()
            return self.dtmf.get(tuple(m), '')

    def getpeaks(self, a):
        # This could be better.
        from numarray.fft import real_fft
        from numarray import add, abs, greater, nonzero
        from sets import Set
        res = real_fft(a)
        res1 = abs(res)
        mres = add.reduce(res1)/len(res1)
        if not mres:
            return []
        # Here's the bit I'm uncomfortable with. The 'eight times average'
        # seems a hack. On the other hand, it works for me.
        res2 = res1/mres
        peaks = Set(nonzero(greater(res2, 8))[0])
        return peaks

def dtmfGenerator(key, duration=160):
    import struct
    f = dtmf2freq.get(key)
    if not f:
        raise ValueError('dtmf key %s not recognised!'%(key))
    f1, f2 = f
    s1 = getSineWave(f1, duration)
    s2 = getSineWave(f2, duration)
    # combine them and make louder
    s = [ (2**13)*(s1[x]+s2[x]) for x in range(duration) ] 
    # turn into a string
    s = struct.pack('%dh'%duration, *s)
    return s





def test():
    import sys
    if len(sys.argv) != 2:
        print "usage: dtmfdetect.py <file>"
        print "file should be 8KHz raw 16 bit signed samples"
        print "use sox infile.au -s -w testfile.raw to make this"
        sys.exit(1)
    audio = open(sys.argv[1], 'r')
    D = DtmfDetector()
    old = ''
    offs = 0.0
    prev = None
    while True:
        # To better replicate how shtoom uses this code, we read in 20ms
        # samples, then analyse a sliding window of size 2.
        samp = audio.read(320)
        if len(samp) < 320:
            break
        if not prev:
            prev = samp
            continue
        digit = D.detect(prev+samp)
        prev = samp
        if digit != old:
            if old == '':
                print "%.3fs: %s ON"%(offs, digit)
            elif digit == '':
                print "%.3fs: %s OFF"%(offs, old)
            else:
                print "%.3fs: %s OFF"%(offs, old)
                print "%.3fs: %s ON"%(offs, digit)
            old = digit
        offs = offs + (320.0/HZ)

if __name__ == "__main__":
    test()
