def power(sample):
    cdef float s
    cdef int x
    import math

    for x in sample:
        s = s + ( x*x )
    ms = s/160
    rms = math.sqrt(ms)
    return rms, sample

