# Copyright (C) 2004 Anthony Baxter

from twisted.internet.protocol import DatagramProtocol
from twisted.python import log

# Placeholder until I get time to integrate old rtcp code into new
# codebase

# got RTCP from ('192.168.41.250', 18867) (72 bytes): 
#    81c90007 261a29fa
#    03cfe121 06000018
#    000018b7 00000000
#    00000000 00000000
#    81ca0007 261a29fa
#    0114302e 302e3040
#    3139322e 3136382e
#    34312e32 35300000
#    81cb0001 261a29fa
#    00000000 00000000

RTCP_PT_SR = 200
RTCP_PT_RR = 201
RTCP_PT_SDES = 202
RTCP_PT_BYE = 203
RTCP_PT_APP = 204
rtcpPTdict = {RTCP_PT_SR: 'SR', RTCP_PT_RR: 'RR', RTCP_PT_SDES:'SDES', RTCP_PT_BYE:'BYE'}
for k,v in rtcpPTdict.items(): 
    rtcpPTdict[v] = k

RTCP_SDES_CNAME = 1
RTCP_SDES_NAME = 2
RTCP_SDES_EMAIL = 3
RTCP_SDES_PHONE = 4
RTCP_SDES_LOC = 5
RTCP_SDES_TOOL = 6
RTCP_SDES_NOTE = 7
RTCP_SDES_PRIV = 8
rtcpSDESdict = {RTCP_SDES_CNAME: 'CNAME', 
                RTCP_SDES_NAME: 'NAME', 
                RTCP_SDES_EMAIL: 'EMAIL', 
                RTCP_SDES_PHONE: 'PHONE', 
                RTCP_SDES_LOC: 'LOC', 
                RTCP_SDES_TOOL: 'TOOL', 
                RTCP_SDES_NOTE: 'NOTE', 
                RTCP_SDES_PRIV: 'PRIV', 
               }
for k,v in rtcpSDESdict.items(): 
    rtcpSDESdict[v] = k




import struct

def hexrepr(bytes):
    out = ''
    bytes = bytes + '\0'* ( 8 - len(bytes)%8 )
    for i in range(0,len(bytes), 8):
        out = out +  "    %02x%02x%02x%02x %02x%02x%02x%02x\n"%tuple(
                                                    [ord(bytes[i+x]) for x in range(8)])
    return out

class RTCPPacket:
    def __init__(self, pt, count, body):
        self.pt = pt
        self.count = count
        self.body = body
        getattr(self, 'decode_%s'%pt)()

    def decode_SDES(self):
        for i in range(self.count):
            self._sdes = []
            print len(self.body)
            ssrc, = struct.unpack('!I', self.body[:4])
            self._sdes.append((ssrc,[]))
            self.body = self.body[4:]
            while True:
                type, length = ord(self.body[0]), ord(self.body[1])
                off = length+2
                maybepadlen = 4-((length+2)%4)
                body, maybepad = self.body[2:off], self.body[off:off+maybepadlen]
                self.body = self.body[length+2:]
                self._sdes[-1][1].append((rtcpSDESdict[type], body))
                if ord(maybepad[0]) == 0:
                    # end of list. eat the padding.
                    self.body = self.body[maybepadlen:]
                    break
        self._pretty = 'SDES %r'%(self._sdes,)

    def decode_BYE(self):
        self._bye = [[],'']
        for i in range(self.count):
            ssrc, = struct.unpack('!I', self.body[:4])
            self._bye[0].append(ssrc)
            self.body = self.body[4:]
        if self.body:
            # A reason!
            length = ord(self.body[0]) 
            reason = self.body[1:length+1]
            self._bye[1] = reason
            self.body = ''
        self._pretty = 'BYE %r: %r'%tuple(self._bye)

    def decode_SR(self):
        self._pretty = 'SR'

    def decode_RR(self):
        self._pretty = 'RR'

    def decode_APP(self):
        self._pretty = 'APP'

    def decode_UNKNOWN(self):
        self._pretty = 'UNKNOWN'

    def __repr__(self):
        if self.body:
            leftover = ' '+repr(self.body)
        else:
            leftover = ''
        return '<RTCP %s%s>'%(self._pretty, leftover)

class RTCPCompound:
    "A single RTCP packet can contain multiple RTCP items"
    def __init__(self, bytes):
        self._rtcp = []
        self.decode(bytes)

    def decode(self, bytes):
        while bytes:
            count = ord(bytes[0]) & 31
            PT = rtcpPTdict.get(ord(bytes[1]), 'UKNOWN')
            length, = struct.unpack('!H', bytes[2:4])
            offset = 4*(length+1)
            body, bytes = bytes[4:offset], bytes[offset:]
            self._rtcp.append(RTCPPacket(PT, count, body))
            

class RTCPProtocol(DatagramProtocol):
    def datagramReceived(self, datagram, addr):
        print "got RTCP from %r (%d bytes): \n%s"%(addr, len(datagram), hexrepr(datagram))
        

    def sendDatagram(self, packet):
        self.transport.write(packet)
