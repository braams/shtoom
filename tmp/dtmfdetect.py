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

def getarray(f):
    import sunau, audioop
    from numarray import Int16, fromstring
    au = sunau.open(f, 'r')
    # sunau converts for us.
    lin = au.readframes(320)
    a = fromstring(lin, Int16) 
    return a

def main(files):
    from numarray.fft import real_fft
    from numarray import add, fabs, abs, log, greater, nonzero
    from sets import Set 

    freqmatch = {}
    dtmf = { 
        (697,1209):'1', (697,1336):'2',(697,1477):'3',(697,1633):'A',
        (770,1209):'4', (770,1336):'5',(770,1477):'6',(770,1633):'B',
        (852,1209):'7', (852,1336):'8',(852,1477):'9',(852,1633):'C',
        (941,1209):'*', (941,1336):'0',(941,1477):'#',(941,1633):'D',
        }
    for val in 1209, 1336, 1477, 1633, 697, 770, 852, 941:
        sine = getSineWave(val)
        peaks = getpeaks(sine)
        for peak in peaks:
            freqmatch[peak] = val
    for f in files:
        a = getarray(f)
        peaks = getpeaks(a)
        matched = Set()
        for p in peaks:
            matched.add(freqmatch.get(p))
        if None in matched:
            print "no match"
        else:
            m = list(matched)
            m.sort()
            print f, dtmf.get(tuple(m))
            
def getpeaks(a):
    from numarray.fft import real_fft
    from numarray import add, fabs, abs, log, greater, nonzero
    res = real_fft(a)
    res1 = abs(res)
    #print "r1", res1
    mres = add.reduce(res1)/len(res1)
    res2 = res1/mres
    peaks = list(nonzero(greater(res2, 8))[0])
    return peaks

if __name__ == "__main__":
    import sys
    from numarray import floor
    main(sys.argv[1:])
