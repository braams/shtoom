# Copyright (C) 2004 Anthony Baxter

# $Id: rtp.py,v 1.40 2004/03/07 14:41:39 anthony Exp $
#

import struct
from time import sleep, time

# This class supports extension headers, but only one per packet.
class RTPPacket:
    """ Contains RTP data. """
    class Header:
        def __init__(self, ssrc, pt, ct, seq, ts, marker=0, xhdrtype=None, xhdrdata=''):
            """
            If xhdrtype is not None then it is required to be an int >= 0 and < 2**16 and xhdrdata is required to be a string.
            """
            assert isinstance(ts, (int, long,)), "ts: %s :: %s" % (ts, type(ts),)
            assert isinstance(ssrc, (int, long,))
            assert xhdrtype is None or isinstance(xhdrtype, int) and xhdrtype >= 0 and xhdrtype < 2**16
            assert xhdrtype is None or isinstance(xhdrdata, str)

            self.ssrc, self.pt, self.ct, self.seq, self.ts, self.marker, self.xhdrtype, self.xhdrdata = ssrc, pt, ct, seq, ts, marker, xhdrtype, xhdrdata

        def netbytes(self):
            "Return network-formatted header."
            assert isinstance(self.pt, int) and self.pt >= 0 and self.pt < 2**8, "pt is required to be a simple byte, suitable for stuffing into an RTP packet and sending. pt: %s" % self.pt
            if self.xhdrtype is not None:
                firstbyte = 0x90
                xhdrnetbytes = struct.pack('!HH', self.xhdrtype, len(self.xhdrdata)) + self.xhdrdata
            else:
                firstbyte = 0x80
                xhdrnetbytes = ''
            return struct.pack('!BBHII', firstbyte, self.pt | self.marker << 7, self.seq % 2**16, self.ts, self.ssrc) + xhdrnetbytes

    def __init__(self, ssrc, seq, ts, data, pt=None, ct=None, marker=0, authtag='', xhdrtype=None, xhdrdata=''):
        assert pt is None or isinstance(pt, int) and pt >= 0 and pt < 2**8, "pt is required to be a simple byte, suitable for stuffing into an RTP packet and sending. pt: %s" % pt
        self.header = RTPPacket.Header(ssrc, pt, ct, seq, ts, marker, xhdrtype, xhdrdata)
        self.data = data
        self.authtag = authtag # please leave this alone even if it appears unused -- it is required for SRTP

    def __repr__(self):
        if self.header.ct is not None:
            ptrepr = "%r" % (self.header.ct,)
        else:
            ptrepr = "pt %d" % (self.header.pt,)

        if self.header.xhdrtype is not None:
            return "<%s #%d (%s) %s [%s] at %x>"%(self.__class__.__name__, self.header.seq, self.header.xhdrtype, ptrepr, repr(self.header.xhdrdata), id(self))
        else:
            return "<%s #%d %s at %x>"%(self.__class__.__name__, self.header.seq, ptrepr, id(self))

    def netbytes(self):
        "Return network-formatted packet."
        return self.header.netbytes() + self.data + self.authtag

def parse_rtppacket(bytes):
    hdr = struct.unpack('!BBHII', bytes[:12])
    padding = hdr[0]&32 and 1 or 0
    cc = hdr[0]&15 and 1 or 0
    x = hdr[0]&16 and 1 or 0
    pt = hdr[1]&127
    marker = hdr[1]&128 and 1 or 0
    seq = hdr[2]
    ts = hdr[3]
    ssrc = hdr[4]
    headerlen = 12
    if cc > 1:
        headerlen = headerlen + 4 * cc
    data = bytes[headerlen:]
    if x:
        # Mmm. Tasty tasty header extensions. We eats them.  Except for the first one.
        xhdrtype,xhdrlen = struct.unpack('!HH', data[:4])
        xhdrdata = data[4:4+4*xhdrlen]
        data = data[4+4*xhdrlen:]
    else:
        xhdrtype, xhdrdata = None, None
    if padding:
        padcount = ord(data[-1])
        if padcount:
            data = data[:-padcount]
    return RTPPacket(ssrc, seq, ts, data, marker=marker, pt=pt, xhdrtype=xhdrtype, xhdrdata=xhdrdata)

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
