"""
    Extraordinarily badly written DTMF detection code. This is just 
    "something that works". 
"""


# DTMF frequencies.
#      1209   1336   1477   1633
#  697   1      2      3      A     27.88
#  770   4      5      6      B     30.8
#  852   7      8      9      C     34.08
#  941   *      0      #      D     37.64
#      48.36  53.44  59.08  65.32

def getSineWave(freq):
    from numarray import sin, arange
    from math import pi
    sine = sin(arange(8000.0)/(8000.0/freq) * 2.0 * pi)
    sine = sine[:320]
    return sine


class DtmfDetector:

    def __init__(self):
        from numarray import add, fabs, abs, log, greater, nonzero
        from sets import Set 
        self.freqmatch = {}
        self.dtmf = { 
            (697,1209):'1', (697,1336):'2',(697,1477):'3',(697,1633):'A',
            (770,1209):'4', (770,1336):'5',(770,1477):'6',(770,1633):'B',
            (852,1209):'7', (852,1336):'8',(852,1477):'9',(852,1633):'C',
            (941,1209):'*', (941,1336):'0',(941,1477):'#',(941,1633):'D',
            }
        for val in 1209, 1336, 1477, 1633, 697, 770, 852, 941:
            sine = getSineWave(val)
            peaks = self.getpeaks(sine)
            for peak in peaks:
                self.freqmatch[peak] = val

    def detect(self, sample):
        import numarray
        from sets import Set

        a = numarray.fromstring(sample, numarray.Int16)
        peaks = self.getpeaks(a)
        matched = Set()
        for p in peaks:
            matched.add(self.freqmatch.get(p))
        if None in matched:
            return ''
        else:
            m = list(matched)
            m.sort()
            return self.dtmf.get(tuple(m), '')

    def getpeaks(self, a):
        from numarray.fft import real_fft
        from numarray import add, fabs, abs, log, greater, nonzero
        res = real_fft(a)
        res1 = abs(res)
        mres = add.reduce(res1)/len(res1)
        if not mres:
            return []
        res2 = res1/mres
        peaks = list(nonzero(greater(res2, 8))[0])
        return peaks

def test():
    import sys
    audio = open(sys.argv[1], 'r')
    # sunau converts for us.
    D = DtmfDetector()
    old = ''
    offs = 0.0
    prev = None
    while True: 
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
        offs = offs + (320.0/8000)

if __name__ == "__main__":
    test()
