import struct, socket
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol


DefaultServers = [
    ('tesla.divmod.net', 3478),
    ('erlang.divmod.net', 3478),
    ('tesla.divmod.net', 3479),
    ('erlang.divmod.net', 3479),
    ('stun.wirlab.net', 3478),
]

StunTypes = { 
   0x0001: 'MAPPED-ADDRESS',
   0x0002: 'RESPONSE-ADDRESS ',
   0x0003: 'CHANGE-REQUEST',
   0x0004: 'SOURCE-ADDRESS',
   0x0005: 'CHANGED-ADDRESS',
   0x0006: 'USERNAME',
   0x0007: 'PASSWORD',
   0x0008: 'MESSAGE-INTEGRITY',
   0x0009: 'ERROR-CODE',
   0x000a: 'UNKNOWN-ATTRIBUTES',
   0x000b: 'REFLECTED-FROM',
}


class StunProtocol(DatagramProtocol, object):
    def __init__(self, servers=DefaultServers, *args, **kwargs):
        self._map = {}
        self.servers = servers
        super(StunProtocol, self, *args, **kwargs)

    def datagramReceived(self, dgram, address):
        mt, pktlen, tid = struct.unpack('!hh16s', dgram[:20])
        # Check tid is one we sent and haven't had a reply to yet
        if mt == 0x0101:
            # response
            remainder = dgram[20:]
            while remainder:
                avtype, avlen = struct.unpack('!hh', remainder[:4])
                val = remainder[4:4+avlen]
                avtype = StunTypes.get(avtype, '(Unknown type %04x)'%avtype)
                remainder = remainder[4+avlen:]
                if avtype in ('MAPPED-ADDRESS',
                              'CHANGED-ADDRESS',
                              'SOURCE-ADDRESS'):
                    dummy,family,port,addr = struct.unpack('!cch4s', val)
                    print "%s: %s %s"%(avtype,socket.inet_ntoa(addr),port)
                else:
                    print "unhandled AV %s, val %r"%(avtype, repr(val))
        elif mt == 0x0111:
            print "error!"
        

    def sendRequest(self, server, avpairs=()):
        tid = open('/dev/urandom').read(16)
        mt = 0x1 # binding request
        avstr = ''
        # add any attributes
        for a,v in avpairs:
            raise NotImplementedError, "implement avpairs"
        pktlen = len(avstr)
        if pktlen > 65535:
            raise ValueError, "stun request too big (%d bytes)"%pktlen
        pkt = struct.pack('!hh16s', mt, pktlen, tid) + avstr
        print "len(pkt)", len(pkt)
        print "sending request to %s:%s"%server
        self.transport.write(pkt, server)

    def blatServers(self):
        for s in self.servers:
            self.sendRequest(s)


if __name__ == "__main__":
    stunClient = StunProtocol()
    reactor.listenUDP(5061, stunClient)
    reactor.callLater(2, stunClient.blatServers)
    reactor.run()
