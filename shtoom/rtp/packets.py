# Copyright (C) 2004 Anthony Baxter

# $Id: rtp.py,v 1.40 2004/03/07 14:41:39 anthony Exp $
#

import struct, random, os, md5, socket
from time import sleep, time

from twisted.internet import defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall
from twisted.python import log

class RTPPacket:
    "An RTPPacket contains RTP data to/from the RTP object"
    def __init__(self, pt, data, ts, marker=0):
        self.pt = pt
        self.data = data
        self.ts = ts
        self.marker = marker
        self.ssrc = None
        self.seq = None

    def __repr__(self):
        return "<RTPPacket containing %r at %x>"%(self.pt, id(self))


class RTPParser:
    """ An RTPParser creates RTPPacket objects from a bytestring. It is
        created with a mapping of RTP PT bytes to PT markers"""
    def __init__(self, ptdict):
        self.ptdict = ptdict

    def tonet(self, packet, seq, ts, ssrc):
        "Return network formatted packet"
        pt = packet.pt
        # XXX handle cc and x!
        byte0 = 0x80
        fmt = self.ptdict[pt] & 127
        if packet.marker: fmt = fmt | 128
        hdr = struct.pack('!BBHII', byte0, fmt, seq, ts, ssrc)
        # Padding?
        return hdr + packet.data

    # XXX Note that the MediaLayer will create it's own RTPPackets - this is
    # purely for packets coming off the network.
    def fromnet(self, bytes, fromaddr):
        hdr = struct.unpack('!BBHII', bytes[:12])
        padding = hdr[0]&32 and 1 or 0
        cc = hdr[0]&15 and 1 or 0
        x = hdr[0]&16 and 1 or 0
        pt = hdr[1]&127
        pt = self.ptdict[pt]
        marker = hdr[1]&128 and 1 or 0
        seq = hdr[2]
        ts = hdr[3]
        ssrc = hdr[4]
        headerlen = 12
        if cc > 1:
            headerlen = headerlen + 4 * cc
        data = bytes[headerlen:]
        if x:
            # Mmm. Tasty tasty header extensions. We eats them.
            xhdrtype,xhdrlen = struct.unpack('!HH', data[:4])
            data = data[4+xhdrlen:]
        if padding:
            padcount = ord(data[-1])
            if padcount:
                data = data[:-padcount]
        packet = RTPPacket(pt, data, ts, marker)
        packet.ssrc = ssrc
        packet.seq = seq
        return packet

    def haspt(self, key):
        return self.ptdict.has_key(key)



class NTE:
    "An object representing an RTP NTE (rfc2833)"
    # XXX at some point, this should be hooked into the RTPPacketFactory.
    def __init__(self, key, startTS):
        self.startTS = startTS
        self.ending = False
        self.counter = 3
        self.key = key
        if key >= '0' and key <= '9':
            self._payKey = chr(int(key))
        elif key == '*':
            self._payKey = chr(10)
        elif key == '#':
            self._payKey = chr(11)
        elif key >= 'A' and key <= 'D':
            # A - D are 12-15
            self._payKey = chr(ord(key)-53)
        elif key == 'flash':
            self._payKey = chr(16)
        else:
            raise ValueError, "%s is not a valid NTE"%(key)

    def getKey(self):
        return self.key

    def end(self):
        self.ending = True
        self.counter = 1

    def getPayload(self, ts):
        if self.counter > 0:
            if self.ending:
                end = 128
            else:
                end = 0
            payload = self._payKey + chr(10|end) + \
                                struct.pack('!H', ts - self.startTS)
            self.counter -= 1
            return payload
        else:
            return None

    def isDone(self):
        if self.ending and self.counter < 1:
            return True
        else:
            return False

    def __repr__(self):
        return '<NTE %s%s>'%(self.key, self.ending and ' (ending)' or '')
