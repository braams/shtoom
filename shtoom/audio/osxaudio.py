# Copyright (C) 2004 Anthony Baxter

## Have to initialize the threading mechanisms in order for PyGIL_Ensure to work
from twisted.python import threadable
threadable.init(1)
import thread ; thread.start_new_thread(lambda: None, ())

import coreaudio
from math import sin, sqrt
from numarray import multiply, add, Int16, Int32, zeros, Float32
from twisted.internet import reactor
import sys, traceback, audioop
from converters import MediaLayer
from time import time

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
    prevtime = None
    SCALE = 32768/2

    def __init__(self):
        self.outbuffer = '' # Buffer from mac sound out to the network
        self.inbuffer = '' # Buffer from the network back to the mac
        self.running = False
        self.reopen()
        self.counter = 0

    def read(self, bytes=320, buffer=320*0):
        if self.prevtime is None:
            delta = 0
        else:
            delta = 1000*(time() - self.prevtime)
        self.prevtime = time()
        if len(self.outbuffer) < (buffer + bytes):
            #if self.counter % 20 == 0:
                #print "silence, because %d < %d"%(len(self.outbuffer), buffer+bytes)
            return ''
        else:
            sound, self.outbuffer = self.outbuffer[:bytes], self.outbuffer[bytes:]
        return sound

    def write(self, data):
        #print "got %d bytes from network"%(len(data))
        out = self.to44KStereo(data)
        self.inbuffer += out

    def reopen(self):
        if not self.running:
            print "Installing coreaudio callback"
            coreaudio.installAudioCallback(self)
            self.running = True

    def _close(self):
        if self.running:
            print "uninstalling coreaudio callback"
            coreaudio.stopAudio(self)
            self.outbuffer = ''
            self.running = False

    def from44KStereo(self, buffer):
        b, self.tostate = audioop.ratecv(buffer, 2, 2, 44100, 8000, self.tostate)
        b = audioop.tomono(b, 2, 1, 1)
        return b

    def toPCMString(self, buffer):
        b = buffer * self.SCALE - self.SCALE/2
        b = b.astype(Int16)
        # Damn. Endianness?
        b = b.tostring()
        return b

    def to44KStereo(self, buffer):
        try:
            b = audioop.tostereo(buffer.data, 2, 1, 1)
            b, self.fromstate = audioop.ratecv(b, 2, 2, 8000, 44100, self.fromstate)
        except audioop.error:
            return ''
        return b

    def fromPCMString(self, buffer):
        from numarray import fromstring, Int16, Float32
        #print "buffer", len(buffer)
        b = fromstring(buffer, Int16)
        b = b.astype(Float32)
        b = ( b + 32768/2 ) / self.SCALE
        return b

    def _maybeLoopback(self):
        # For test purposes - copies the audio from the audio device back out again
        if len(self.outbuffer) > 200:
            buf, self.outbuffer = self.outbuffer[:200], self.outbuffer[200:]
            buf = self.to44KStereo(buf)
            self.inbuffer = self.inbuffer + buf

    def storeSamples(self, samples):
        "Takes an array of 512 32bit float samples, stores as 8KHz 16bit ints"
        std = self.toPCMString(samples)
        std = self.from44KStereo(std)
        self.outbuffer = self.outbuffer + std
        if len(self.outbuffer) > (3 * 320):
            self.outbuffer = self.outbuffer[-960:]
        #self._maybeLoopback()

    def getSamples(self):
        "Returns an array of 512 32 bit samples from the pending audio"
        if len(self.inbuffer) < 2048:
            return None
        else:
            res, self.inbuffer = self.inbuffer[:2048], self.inbuffer[2048:]
            res = self.fromPCMString(res)
            return res

    def callback(self, buffer):
        self.counter += 1
        #if self.counter % 20 == 0:
            #print "callback #%d"%(self.counter)
        try:
            self.storeSamples(buffer)
            out = self.getSamples()
            if out is None:
                buffer[:] = zeros(1024)
                return
            else:
                buffer[:] = out
                return
        except:
            e,v,t = sys.exc_info()
            print e, v
            traceback.print_tb(t)
        return

    def selectDefaultFormat(self, format):
        pass

Device = OSXAudio
