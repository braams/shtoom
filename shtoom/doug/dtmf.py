"""
    DTMF generation and detection code. This replaces the old nasty
    code with something a bit nicer (but a bit slower, too :-(
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
SAMPLETIME = 0.040
SAMPLESIZE = int(1/SAMPLETIME)
SCALING = 1/SAMPLETIME

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
            self.freqmatch[int(val/SCALING)+1] = val

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
                if p-1 in self.freqmatch:
                    m = self.freqmatch.get(p-1)
                elif p+1 in self.freqmatch:
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

    def getpeaks(self, sample):
        from numarray import nonzero
        from numarray.fft import real_fft
        fft = abs(real_fft(sample))
        # We compare each point to the point on either side - we must be
        # greater than both.
        # To do this, we left-shift and right-shift the array by one to
        # compare.
        peaks = nonzero((fft[1:-1] > fft[:-2]) * (fft[1:-1] > fft[2:]))
        if not len(peaks) or not len(peaks[0]):
            return ()
        # Avoiding 'zip; sort; reverse' will give a big speedup.
        try:
            peakvals = zip(fft[1:-1].take(peaks)[0], peaks[0])
        except:
            print "pppp", peaks
            raise
        peakvals.sort(); peakvals.reverse()
        if len(peakvals) > 2:
            (val1,ind1),(val2,ind2),(val3,ind3) = peakvals[:3]
            # Peak 3 should be no more than 2/3 the size of peak 2
            # For GSM/Speex mangled audio, peak3 is about 0.55 * peak2
            # at the worst case.
            if val2 > 1.5*val3:
                # Add one to the index because we took [1:-1] before
                return (ind2+1,ind1+1)
            else:
                return ()
        elif len(peakvals) == 2:
            (val2,ind2),(val1,ind1) = peakvals
            # Add one to the index because we took [1:-1] before
            return (ind2+1,ind1+1)
        else:
            (val1,ind1), = peakvals
            return (ind1,0)

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
