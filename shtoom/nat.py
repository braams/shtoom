
# Code for NATs and the like. Also includes code for determining local IP
# address (suprisingly tricky, in the presence of STUPID STUPID STUPID
# networking stacks)

from twisted.internet import defer
from twisted.internet.protocol import DatagramProtocol
import random, socket
from twisted.python import log
from shtoom.defcache import DeferredCache

_Debug = False

class LocalNetworkMulticast(DatagramProtocol, object):

    def __init__(self, *args, **kwargs):
        self.compDef = defer.Deferred()
        self.completed = False
        super(LocalNetworkMulticast,self).__init__(*args, **kwargs)

    def listenMulticast(self):
        from twisted.internet import reactor
        from twisted.internet.error import CannotListenError
        attempt = 0
        port = 11000 + random.randint(0,5000)
        while True:
            try:
                mcast = reactor.listenMulticast(port, self)
                break
            except CannotListenError:
                port = 11000 + random.randint(0,5000)
                attempt += 1
                print "listenmulticast failed, trying", port
        if attempt > 5:
            log.msg("warning: couldn't listen ony mcast port", system='network')
            d, self.compDef = self.compDef, None
            d.callback(None)
        mcast.joinGroup('239.255.255.250', socket.INADDR_ANY)
        self.mcastPort = port

    def blatMCast(self):
        # XXX might need to set an option to make sure we see our own packets
        self.transport.write('ping', ('239.255.255.250', self.mcastPort))
        self.transport.write('ping', ('239.255.255.250', self.mcastPort))
        self.transport.write('ping', ('239.255.255.250', self.mcastPort))

    def datagramReceived(self, dgram, addr):
        if self.completed:
            return
        elif dgram != 'ping':
            return
        else:
            self.completed = True
            d, self.compDef = self.compDef, None
            d.callback(addr[0])

_cachedLocalIP = None
def _cacheLocalIP(res):
    global _cachedLocalIP
    if _Debug: print "caching value", res
    _cachedLocalIP = res
    return res

# If there's a need to clear the cache, call this method (e.g. DHCP client)
def _clearCachedLocalIP():
    _cacheresult(None)

def _getLocalIPAddress():
    # So much pain. Don't even bother with 
    # socket.gethostbyname(socket.gethostname()) - the number of ways this
    # is broken is beyond belief.
    from twisted.internet import reactor
    global _cachedLocalIP
    if _cachedLocalIP is not None:
        return defer.succeed(_cachedLocalIP)
    # first we try a connected udp socket
    if _Debug: print "resolving A.ROOT-SERVERS.NET"
    d = reactor.resolve('A.ROOT-SERVERS.NET')
    d.addCallbacks(_getLocalIPAddressViaConnectedUDP, _noDNSerrback)
    return d

getLocalIPAddress = DeferredCache(_getLocalIPAddress)

def clearCache():
    "Clear cached NAT settings (e.g. when moving to a different network)"
    from shtoom.upnp import clearCache as uClearCache
    from shtoom.stun import clearCache as sClearCache
    getLocalIPAddress.clearCache()
    uClearCache()
    sClearCache()

def _noDNSerrback(failure):
    # No global DNS? What the heck, it's possible, I guess.
    if _Debug: print "no DNS, trying multicast"
    return _getLocalIPAddressViaMulticast()

def _getLocalIPAddressViaConnectedUDP(ip):
    from twisted.internet import reactor
    from twisted.internet.protocol import ConnectedDatagramProtocol
    if _Debug: print "connecting UDP socket to", ip
    prot = ConnectedDatagramProtocol()
    p = reactor.listenUDP(0, prot)
    res = prot.transport.connect(ip, 7)
    locip = prot.transport.getHost().host
    p.stopListening()
    del prot, p

    if _Debug: print "connected UDP socket says", locip
    if locip.startswith('127.') or locip.startswith('0.'):
        # #$#*(&??!@#$!!!
        if _Debug: print "connected UDP socket gives crack, trying mcast instead"
        return _getLocalIPAddressViaMulticast()
    else:
        return locip


def _getLocalIPAddressViaMulticast():
    # We listen on a new multicast address (using UPnP group, and 
    # a random port) and send out a packet to that address - we get 
    # our own packet back and get the address from it. 
    from twisted.internet import reactor
    from twisted.internet.interfaces import IReactorMulticast
    try:
        IReactorMulticast(reactor)
    except:
        if _Debug: print "no multicast support in reactor"
        log.msg("warning: no multicast in reactor", system='network')
        return None
    locprot = LocalNetworkMulticast()
    if _Debug: print "listening to multicast"
    locprot.listenMulticast()
    if _Debug: print "sending multicast packets"
    locprot.blatMCast()
    locprot.compDef.addCallback(_cacheLocalIP)
    return locprot.compDef

def cb_detectNAT(res):
    (ufired,upnp), (sfired,stun) = res
    if not ufired and not sfired:
        log.msg("no STUN or UPnP results", system="nat")
        return None
    if ufired:
        return upnp
    return stun

def detectNAT():
    # We prefer UPnP when available, as it's less pissing about (ha!)
    from shtoom.upnp import getUPnP
    from shtoom.stun import getSTUN
    ud = getUPnP()
    sd = getSTUN()
    dl = defer.DeferredList([ud, sd])
    dl.addCallback(cb_detectNAT).addErrback(log.err)
    return dl

def cb_getMapper(res):
    from shtoom.upnp import getMapper as getUMapper
    from shtoom.stun import getMapper as getSTUNMapper
    (ufired,upnp), (sfired,stun) = res
    log.msg("detectNAT got %r"%res, system="nat")
    if not upnp and not stun:
        log.msg("no STUN or UPnP results", system="nat")
        return getNullMapper()
    if upnp:
        log.msg("using UPnP mapper", system="nat")
        return getUMapper()
    if not stun.blocked:
        log.msg("using STUN mapper", system="nat")
        return getSTUNMapper()
    log.msg("No UPnP, and STUN is useless", system="nat")
    return getNullMapper()

def getMapper():
    # We prefer UPnP when available, as it's less pissing about (ha!)
    from shtoom.upnp import getUPnP
    from shtoom.stun import getSTUN
    ud = getUPnP()
    sd = getSTUN()
    dl = defer.DeferredList([ud, sd])
    dl.addCallback(cb_getMapper).addErrback(log.err)
    return dl

def isBogusAddress(addr):
    """ Returns true if the given address is bogus, i.e. 0.0.0.0 or
        127.0.0.1. Additional forms of bogus might be added later.
    """
    if addr.startswith('0.') or addr.startswith('127.'):
        return True
    return False

class BaseMapper:
    "Base class with useful functionality for Mappers"
    _ptypes = []

    def _checkValidPort(self, port):
        from twisted.internet.base import BasePort
        # Ugh. Why is there no IPort ?
        if not isinstance(port, BasePort):
            raise ValueError("expected a Port, got %r"%(port))
        # XXX Check it's listening! How???
        if not hasattr(port, 'socket'):
            raise ValueError("Port %r appears to be closed"%(port))

        locAddr = port.getHost()
        if locAddr.type not in self._ptypes:
            raise ValueError("can only map %s, not %s"%
                        (', '.join(self._ptypes),locAddr.type))
        if locAddr.port == 0:
            raise ValueError("Port %r has port number of 0"%(port))

        if not port.connected:
            raise ValueError("Port %r is not listening"%(port))

class NullMapper(BaseMapper):
    "Mapper that does nothing"

    _ptypes = ( 'TCP', 'UDP' )

    def __init__(self):
        self._mapped = {}

    def map(self, port):
        "See shtoom.interfaces.NATMapper.map"
        self._checkValidPort(port)
        if port in self._mapped:
            return defer.succeed(self._mapped[port])
        cd = defer.Deferred()
        self._mapped[port] = cd
        locAddr = port.getHost().host
        if isBogusAddress(locAddr):
            # lookup local IP.
            d = getLocalIPAddress()
            d.addCallback(lambda x: self._cb_map_gotLocalIP(x, port))
        else:
            reactor.callLater(0, lambda: self._cb_map_gotLocalIP(locAddr, port))
        return cd
    map = DeferredCache(map, inProgressOnly=True)

    def _cb_map_gotLocalIP(self, locIP, port):
        cd = self._mapped[port]
        self._mapped[port] = (locIP, port.getHost().port)
        cd.callback(self._mapped[port])
        
    def info(self, port):
        "See shtoom.interfaces.NATMapper.info"
        if port in self._mapped:
            return self._mapped[port]
        else:
            raise ValueError('Port %r is not currently mapped'%(port))

    def unmap(self, port):
        "See shtoom.interfaces.NATMapper.unmap"
        # A no-op for NullMapper
        if port not in self._mapped:
            raise ValueError('Port %r is not currently mapped'%(port))
        del self._mapped[port]
        return defer.succeed(None)

_cached_nullmapper = None
def getNullMapper():
    global _cached_nullmapper
    if _cached_nullmapper is None:
        _cached_nullmapper = NullMapper()
    return _cached_nullmapper
        


if __name__ == "__main__":
    from twisted.internet import reactor
    import sys

    log.FileLogObserver.timeFormat = "%H:%M:%S"
    log.startLogging(sys.stdout)

    def cb_gotip(addr):
        print "got local IP address of", addr
    def cb_gotnat(res):
        print "got NAT of", res
    d1 = getLocalIPAddress().addCallback(cb_gotip)
    d2 = detectNAT().addCallback(cb_gotnat)
    dl = defer.DeferredList([d1,d2])
    dl.addCallback(lambda x:reactor.stop())
    reactor.run()
