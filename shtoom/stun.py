import struct, socket, time
from twisted.internet import reactor, defer
from twisted.internet.protocol import DatagramProtocol
from twisted.python import log
from interfaces import StunPolicy


DefaultServers = [
    ('stun2.wirlab.net', 3478),
    ('tesla.divmod.net', 3478),
    ('erlang.divmod.net', 3478),
    ('tesla.divmod.net', 3479),
    ('erlang.divmod.net', 3479),
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
        self._pending = {}
        self.servers = servers
        super(StunProtocol, self).__init__(*args, **kwargs)

    def datagramReceived(self, dgram, address):
        mt, pktlen, tid = struct.unpack('!hh16s', dgram[:20])
        # Check tid is one we sent and haven't had a reply to yet
        if self._pending.has_key(tid):
            del self._pending[tid]
        else:
            log.error("error, unknown transaction ID!")
            return
        if mt == 0x0101:
            log.msg("got STUN response from %s"%repr(address))
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
                    dummy,family,port,addr = struct.unpack('!ccH4s', val)
                    #log.msg("STUN response %s: %s %s"%(avtype,socket.inet_ntoa(addr),port))
                    if avtype == 'MAPPED-ADDRESS':
                        self.gotMappedAddress(socket.inet_ntoa(addr),port)
                else:
                    log.msg("STUN: unhandled AV %s, val %r"%(avtype, repr(val)))
        elif mt == 0x0111:
            log.error("STUN got an error response")
        
    def gotMappedAddress(self, addr, port):
        log.msg("got address %s %s (should I have been overridden?)"%(addr, 
                                                                      port))

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
        self._pending[tid] = (time.time(), server)
        # install a callLater for retransmit and timeouts
        self.transport.write(pkt, server)

    def blatServers(self):
        for s in self.servers:
            print "sending to", s
            self.sendRequest(s)

class StunHook(StunProtocol):
    """Hook a StunHook into a UDP protocol object, and it will discover 
       STUN settings for it
    """
    def __init__(self, prot, *args, **kwargs):
        self._protocol = prot
        super(StunHook, self).__init__(*args, **kwargs)

    def installStun(self):
        self._protocol._mp_datagramReceived = self._protocol.datagramReceived
        self._protocol.datagramReceived = self.datagramReceived
        self.transport = self._protocol.transport

    def discoverStun(self, deferred):
        ''' Work out STUN settings. Trigger the deferred with (ip,port)
            when we're done.
        '''
        self.installStun()
        self.sendRequest(self.servers[0])
        self.deferred = deferred

    def gotMappedAddress(self, address, port):
        self.deferred.callback((address, port))
        if not self._pending.keys():
            self.uninstallStun()
        # Check for timeouts here

    def uninstallStun(self):
        self._protocol.datagramReceived = self._protocol._mp_datagramReceived
        del self.transport 

# XXX should move this class somewhere else.
class NetAddress:
    """ A class that represents a net address of the form
        foo/nbits, e.g. 10/8, or 192.168/16, or whatever
    """
    def __init__(self, netaddress):
        parts = netaddress.split('/')
        if len(parts) > 2:
            raise ValueError, "should be of form address/mask"
        if len(parts) == 1:
            ip, mask = parts[0], 32
        else:
            ip, mask = parts[0], int(parts[1])
        if mask < 0 or mask > 32:
            raise ValueError, "mask should be between 0 and 32"

        self.net = self.inet_aton(ip)
        self.mask = ( 2L**32 -1 ) ^ ( 2L**(32-mask) - 1 )
        self.start = self.net
        self.end = self.start | (2L**(32-mask) - 1)

    def inet_aton(self, ipstr):
        "A sane inet_aton"
        net = [ int(x) for x in ipstr.split('.') ] + [ 0,0,0 ]
        net = net[:4]
        return  ((((((0L+net[0])<<8) + net[1])<<8) + net[2])<<8) +net[3]

    def inet_ntoa(self, ip):
        import socket, struct
        return socket.inet_ntoa(struct.pack('!I',ip))

    def __repr__(self):
        return '<NetAddress %s/%s (%s-%s) at %#x>'%(self.inet_ntoa(self.net),
                                           self.inet_ntoa(self.mask), 
                                           self.inet_ntoa(self.start), 
                                           self.inet_ntoa(self.end), 
                                           id(self))

    def check(self, ip):
        "Check if an IP or network is contained in this network address"
        if isinstance(ip, NetAddress):
            return self.check(ip.start) and self.check(ip.end)
        if type(ip) is str:
            ip = self.inet_aton(ip)
        if ip & self.mask == self.net:
            return True
        else:
            return False

    __contains__ = check


class AlwaysStun:
    __implements__ = StunPolicy

    def checkStun(self, localip, remoteip):
        return True

class NeverStun:
    __implements__ = StunPolicy

    def checkStun(self, localip, remoteip):
        return False

class RFC1918Stun:
    "A sane default policy"
    __implements__ = StunPolicy

    addresses = ( NetAddress('10/8'), 
                  NetAddress('172.16/12'), 
                  NetAddress('192.168/16'), 
                  NetAddress('127/8') )

    def checkStun(self, localip, remoteip):
        localIsRFC1918 = False
        remoteIsRFC1918 = False
        # Yay. getPeer() returns a name, not an IP
        # Since (according to radix), I should use "a non-existant 
        # high-level interface to twisted.names.client", and I have
        # no intentions of writing said interface just for this, 
        # punting to socket.gethostbyname() now.
        # This is a filthy filthy hack. But I'm screwed either way.
        if remoteip[0] not in '0123456789':
            import socket
            ai = socket.getaddrinfo(remoteip, None)
            remoteips = [x[4][1] for x in ai]
        else:
            remoteips = [remoteip,]
        for net in self.addresses:
            if localip in net:
                localIsRFC1918 = True
            # See comments above. Worse, if the host has an address that's
            # RFC1918, and externally advertised (which is wrong, and broken), 
            # the STUN check will be incorrect. Bah.
            for remoteip in remoteips:
                if remoteip in net:
                    remoteIsRFC1918 = True
        if localIsRFC1918 and not remoteIsRFC1918:
            return True
        else:
            return False

_defaultPolicy = RFC1918Stun()
def installPolicy(policy):
    global _defaultPolicy
    _defaultPolicy = policy

def getPolicy():
    return _defaultPolicy 


if __name__ == "__main__":
    import sys
    stunClient = StunProtocol()
    log.startLogging(sys.stdout)
    reactor.listenUDP(5061, stunClient)
    reactor.callLater(1, stunClient.blatServers)
    reactor.run()
