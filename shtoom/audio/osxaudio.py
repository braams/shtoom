# Copyright (C) 2004 Anthony Baxter

import thread
## Have to initialize the threading mechanisms in order for PyGIL_Ensure to work
thread.start_new_thread(lambda: None, ())

import coreaudio
from numarray import zeros, Float32
from numarray import multiply, add, Int16, Int32
from math import sin, sqrt
import time, sys, traceback, audioop

from converters import MultipleConv
from rateformat import CoreAudioConverter

opened = None

def RMS(b):
    a = b.astype(Int32)
    multiply(a, a, a)
    ms = add.reduce(a)/len(a)
    rms = sqrt(ms)
    return rms

class OSXAudio(object):
    fromstate = None
    tostate = None
    SCALE = 32768/2

    def __init__(self):
        self.outbuffer = '' # Buffer from mac sound out to the network
        self.inbuffer = '' # Buffer from the network back to the mac
        self.running = False
        self.reopen()

    def read(self, bytes=320):
        if len(self.outbuffer) < bytes:
            return ''
        else:
            sound, self.outbuffer = self.outbuffer[:320], self.outbuffer[:320]
        #print "sent %d to the network"%len(sound)
        return sound

    def write(self, data):
        #print "got %d bytes from network"%(len(data))
        out = self.to44Kstereo(data)
        self.inbuffer += out

    def reopen(self):
        if not self.running:
            print "Installing coreaudio callback"
            coreaudio.installAudioCallback(self)
            self.running = True

    def close(self):
        if self.running:
            print "and (not) stopping it again"
            #coreaudio.stopAudio(self)
            #self.running = False

    def toStdFmt(self, buffer):
        r = []
        b = buffer * self.SCALE - self.SCALE/2
        b = b.astype(Int16)
        # Damn. Endianness?  
        b = b.tostring()
        b, self.tostate = audioop.ratecv(b, 2, 2, 44100, 8000, self.tostate)
        b = audioop.tomono(b, 2, 1, 1)
        return b

    def to44Kstereo(self, buffer):
        b = audioop.tostereo(buffer, 2, 1, 1)
        b, self.fromstate = audioop.ratecv(b, 2, 2, 8000, 44100, self.fromstate)
        return b

    def fromPCMString(self, buffer):
        from numarray import fromstring, Int16, Float32
        r = []
        b = fromstring(buffer, Int16)
        r.append(int(RMS(b)))
        b = b.astype(Float32)
        r.append(int(RMS(b)))
        b = ( b + 32768/2 ) / self.SCALE
        r.append(int(RMS(b)))
        #print "out", r
        return b

    def callback(self, buffer):
        # Gets passed in a 1024-element buffer. Put the output
        # sound in the buffer and return it
        r1 = RMS(buffer)
        sound = self.toStdFmt(buffer)
        r2 = RMS(buffer)
        #print r1, r2
        self.outbuffer += sound
        return 
        try:
            if len(self.inbuffer) < 2048:
                # we got nothing. pad.
                buffer[:] = zeros(1024)
                return buffer
            else:
                sound, self.inbuffer = self.inbuffer[:2048], self.inbuffer[:2048]
                buffer[:] = self.fromPCMString(sound)
                return buffer
        except:
            e,v,t = sys.exc_info()
            print e, v
            traceback.print_tb(t)

def getAudioDevice(mode):
    from __main__ import app
    global opened
    if opened is None:
        opened = MultipleConv(OSXAudio())
    return opened

