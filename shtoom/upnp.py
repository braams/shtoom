#
# Copyright (C) 2004 Anthony Baxter
# $Id: upnp.py,v 1.4 2004/01/23 06:34:23 anthony Exp $
#
# UPnP support.

# UPnP_IGD_WANIPConnection 1.0.doc defines the ExternalPort configuration
# magic.

# Theory of operation:
#
# Multicast address for SSDP is 239.255.255.250 port 1900 (multicast)
#    Listen for SSDP NOTIFYs on mcast
#    Send an M_SEARCH request to query for any IGDs that are out there -
#       send 3 packets, listen for a response.
#    Walk through existing port mappings to see if we've left one behind
#    Expose UI to add/delete/query port mappings


# To be done:
#    Higher level APIs - check if we've left an entry behind, for instance


from twisted.internet.protocol import DatagramProtocol
from twisted.python import log

import socket, random, urlparse
from nonsuckhttp import urlopen
from shtoom.soapsucks import BeautifulSoap, SOAPRequestFactory, soapenurl
from shtoom.defcache import DeferredCache

from shtoom.interfaces import NATMapper as INATMapper
from shtoom.nat import BaseMapper

UPNP_PORT = 1900
UPNP_MCAST = '239.255.255.250'
#from zope.interface import implements

DEBUG = False

class UPnPError(Exception): pass
class NoUPnPFound(UPnPError): pass

def cannedUPnPSearch():
    return """M-SEARCH * HTTP/1.1\r
Host:%s:%s\r
ST:urn:schemas-upnp-org:device:InternetGatewayDevice:1\r
Man:"ssdp:discover"\r
MX:3\r
\r
"""%(UPNP_MCAST, UPNP_PORT)

class UPnPProtocol(DatagramProtocol, object):

    def __init__(self, *args, **kwargs):
        self.controlURL = None
        self.upnpInfo = {}
        self.urlbase = None
        self.gotSearchResponse = False
        super(UPnPProtocol,self).__init__(*args, **kwargs)

    def datagramReceived(self, dgram, address):
        response, message = dgram.split('\r\n', 1)
        version, status, textstatus = response.split(None, 2)
        if not version.startswith('HTTP'):
            return
        if self.controlURL:
            return
        log.msg("got a response from %s, status %s "%(address, status),
                                        system='UPnP')
        if status == "200":
            self.gotSearchResponse = True
            if self.upnpTimeout:
                self.upnpTimeout.cancel()
                self.upnpTimeout = None
            self.handleSearchResponse(message)

    def handleSearchResponse(self, message):
        headers, body = self.parseSearchResponse(message)
        loc = headers.get('location')
        if not loc:
            log.msg("No location header in response to M-SEARCH!",
                                                            system='UPnP')
            return
        loc = loc[0]
        d = urlopen(loc)
        log.msg("found a UPnP device at %s"%loc, system="UPnP")
        d.addCallback(self.handleIGDeviceResponse, loc).addErrback(log.err)

    def parseSearchResponse(self, message):
        hdict = {}
        body = ''
        remaining = message
        while remaining:
            line, remaining = remaining.split('\r\n', 1)
            line = line.strip()
            if not line:
                body = remaining
                break
            key, val = line.split(':', 1)
            key = key.lower()
            hdict.setdefault(key, []).append(val.strip())
        return hdict, body

    def discoverUPnP(self):
        "Discover UPnP devices. Returns a Deferred"
        from twisted.internet import reactor, defer
        self._discDef = defer.Deferred()
        search = cannedUPnPSearch()
        try:
            self.transport.write(search, (UPNP_MCAST, UPNP_PORT))
            self.transport.write(search, (UPNP_MCAST, UPNP_PORT))
            self.transport.write(search, (UPNP_MCAST, UPNP_PORT))
        except socket.error:
            del self._discDef
            return defer.fail(NoUPnPFound('no network available'))
        self.upnpTimeout = reactor.callLater(6, self.timeoutDiscovery)
        return self._discDef

    def isAvailable(self):
        from twisted.internet import defer
        if hasattr(self, '_discDef'):
            return self._discDef
        elif self.controlURL is not None:
            return defer.succeed(self)
        else:
            return defer.fail(NoUPnPFound())

    def completedDiscovery(self):
        log.msg("discovery completed", system="UPnP")
        if self.upnpTimeout:
            self.upnpTimeout.cancel()
            self.upnpTimeout = None
        if hasattr(self, '_discDef'):
            if self.controlURL is not None:
                d = self._discDef
                del self._discDef
                d.callback(self)

    def failedDiscovery(self, err):
        log.msg("discovery failed", system="UPnP")
        if hasattr(self, '_discDef'):
            if self.controlURL is not None:
                self.controlURL = None
            d = self._discDef
            del self._discDef
            d.callback(NoUPnPFound())

    def timeoutDiscovery(self):
        log.msg("discovery timed out", system="UPnP")
        self.upnpTimeout = None
        if hasattr(self, '_discDef'):
            if self.urlbase is None:
                d = self._discDef
                del self._discDef
                d.callback(NoUPnPFound())

    def listenMulticast(self):
        from twisted.internet import reactor
        from twisted.internet.error import CannotListenError
        attempt = 0
        while True:
            try:
                mcast = reactor.listenMulticast(1900+attempt, self)
                break
            except CannotListenError:
                attempt = random.randint(0,500)
                log.msg("couldn't listen on UPnP port, trying %d"%(
                                    attempt+1900), system='UPnP')
        if attempt != 0:
            log.msg("warning: couldn't listen on std upnp port", system='UPnP')
        mcast.joinGroup('239.255.255.250', socket.INADDR_ANY)

    def handleIGDeviceResponse(self, body, loc):
        from twisted.internet import reactor
        #log.msg("before stupidrandomdelaytoworkaroundbug got an IGDevice from %s"%(loc,), system='UPnP')
        reactor.callLater(0, self.stupidrandomdelaytoworkaroundbug, body, loc)

    def stupidrandomdelaytoworkaroundbug(self, body, loc):
        """
        On Mac (but not on Linux), Twisted seems to drop the ball on
        connecTCP().  The TCP connection gets set up (as confirmed by packet
        trace showing three-part handshake), but the factory object never gets
        buildProtocol().  Eventually (depending on the timeout value), the
        factory object gets its connectionFailed() method called instead.

        Mysteriously, this *always* happens on the urlopen in this method, and
        never on any of the other TCP connections that are made during Shtoom
        setup.  Also mysteriously, inserting this stupidrandomdelay of 4 seconds
        fixes it.

        Surely I should write a minimal test case and then either give the test
        case to the Twisted folks or fix it myself, but some other things are
        way too urgent today.

        The sequence of events that I observed was: connect 1; connect 2;
        connect 3; callback 1; callback 2; connect 4; callback 3; ...timeout 4".

        where connect 1-3 are the "are you an IG device", and the connect 4 is
        this "get WAN service desc".  So maybe in twisted the even of the 3rd
        tcp connection completing is screwing up the state of the 4th tcp
        connection, which has been initiated by hasn't completed yet.
        """
        #log.msg("after stupidrandomrelaytoworkaroundbug, got an IGDevice from %s"%(loc,), system='UPnP')
        if self.controlURL is not None:
            log.msg("already found UPnP, discarding duplicate response",
                                                                system="UPnP")
            # We already got a working one - ignore this one
            return
        data = body.read()
        bs = BeautifulSoap(data)
        manufacturer = bs.first('manufacturer')
        if manufacturer and manufacturer.contents:
            log.msg("you're behind a %s"%(manufacturer.contents[0]),
                                                                system='UPnP')
            self.upnpInfo['manufacturer'] = manufacturer.contents[0]
        friendly = bs.first('friendlyName')
        if friendly:
            self.upnpInfo['friendlyName'] = str(friendly.contents[0])
        urlbase = bs.first('URLBase')
        if urlbase and urlbase.contents:
            self.urlbase = str(urlbase.contents[0])
            log.msg("upnp urlbase is %s"%(self.urlbase), system='UPnP')
        else:
            log.msg("upnp response has no urlbase, falling back to %s"%(loc,), system='UPnP')
            self.urlbase = loc

        wanservices = bs.fetch('service',
            dict(serviceType='urn:schemas-upnp-org:service:WANIPConnection:%'))
        for service in wanservices:
            scpdurl = service.get('SCPDURL')
            controlurl = service.get('controlURL')
            if scpdurl and controlurl:
                break
        else:
            log.msg("upnp response showed no WANIPConnections", system='UPnP')
            if DEBUG:
                print "dump of response", bs
            return

        self.controlURL = urlparse.urljoin(self.urlbase, controlurl)
        log.msg("upnp %r controlURL is %s"%(self, self.controlURL), system='UPnP')
        d = urlopen(urlparse.urljoin(self.urlbase, scpdurl))
        d.addCallback(self.handleWanServiceDesc).addErrback(log.err)

    def handleWanServiceDesc(self, body):
        log.msg("got WANServiceDesc from %s"%(self.urlbase,), system='UPnP')
        data = body.read()
        self.soap = SOAPRequestFactory(self.controlURL,
                            "urn:schemas-upnp-org:service:WANIPConnection:1")
        self.soap.setSCPD(data)
        self.completedDiscovery()

    def getExternalIPAddress(self):
        from twisted.internet import defer
        cd = defer.Deferred()
        req = self.soap.GetExternalIPAddress()
        d = soapenurl(req)
        d.addCallbacks(lambda x: self.cb_gotExternalIPAddress(x, cd),
                       lambda x: self.cb_failedExternalIPAddress(x, cd))
        return cd

    def cb_gotExternalIPAddress(self, res, cd):
        cd.callback(res['NewExternalIPAddress'])

    def cb_failedExternalIPAddress(self, failure, cd):
        err = failure.value.args[0]
        cd.errback(UPnPError("GetGenericPortMappingEntry got %s"%(err)))

    def getPortMappings(self):
        from twisted.internet import defer
        cd = defer.Deferred()
        self.getGenericPortMappingEntry(0, cd)
        return cd

    def getGenericPortMappingEntry(self, nextPMI=0, cd=None, saved=None):
        if saved is None:
            saved = {}
        request = self.soap.GetGenericPortMappingEntry(
                                                NewPortMappingIndex=nextPMI)
        d = soapenurl(request)
        d.addCallbacks(lambda x: self.cb_gotGenericPortMappingEntry(x,
                                                                 nextPMI+1,
                                                                 cd, saved),
                       lambda x: self.cb_failedGenericPortMappingEntry(x,
                                                                    cd, saved))

    def cb_gotGenericPortMappingEntry(self, response, nextPMI, cd, saved):
        saved[response['NewProtocol'], response['NewExternalPort']] = response
        self.getGenericPortMappingEntry(nextPMI, cd, saved)

    def cb_failedGenericPortMappingEntry(self, failure, cd, saved):
        err = failure.value.args[0]
        # Some routers (reported on a Netgear DG834) return "Invalid Action"
        # instead of SpecifiedArrayIndexInvalid. This is double-plus bogus.
        if err == "SpecifiedArrayIndexInvalid":
            cd.callback(saved)
        else:
            cd.errback(UPnPError("GetGenericPortMappingEntry got %s"%(err)))

    def addPortMapping(self, intport, extport, desc, proto='UDP', lease=0):
        "add a port mapping. returns a deferred"
        from nat import getLocalIPAddress
        from twisted.internet import defer
        cd = defer.Deferred()
        d = getLocalIPAddress()
        d.addCallback(lambda locIP: self._cbAddPortMapping(intport, extport,
                                                           desc, proto, lease,
                                                           locIP, cd))
        return cd

    def _cbAddPortMapping(self, iport, eport, desc, proto, lease, locip, cd):
        request = self.soap.AddPortMapping(NewRemoteHost=None,
                                           NewExternalPort=eport,
                                           NewProtocol=proto,
                                           NewInternalPort=iport,
                                           NewInternalClient=locip,
                                           NewEnabled=1,
                                           NewPortMappingDescription=desc,
                                           NewLeaseDuration=lease)
        d = soapenurl(request)
        d.addCallbacks(lambda x,cd=cd:self.cb_gotAddPortMapping(x,cd),
                       lambda x,cd=cd:self.cb_failedAddPortMapping(x,cd))

    def cb_gotAddPortMapping(self, response, compdef):
        log.msg('AddPortMapping ok', system='UPnP')
        compdef.callback(None)

    def cb_failedAddPortMapping(self, failure, compdef):
        err = failure.value.args[0]
        log.err('AddPortMapping failed with: %s'%(err), system='UPnP')
        compdef.errback(UPnPError(err))

    def deletePortMapping(self, extport, proto='UDP'):
        "remove a port mapping"
        from twisted.internet import defer
        cd = defer.Deferred()
        request = self.soap.DeletePortMapping(NewRemoteHost=None,
                                              NewExternalPort=extport,
                                              NewProtocol=proto)
        d = soapenurl(request)
        d.addCallbacks(lambda x,cd=cd:self.cb_gotDeletePortMapping(x,cd),
                       lambda x,cd=cd:self.cb_failedDeletePortMapping(x,cd))
        return cd


    def cb_gotDeletePortMapping(self, response, compdef):
        log.msg('DeletePortMapping ok', system='UPnP')
        compdef.callback(None)

    def cb_failedDeletePortMapping(self, failure, compdef):
        err = failure.value.args[0]
        log.err('DeletePortMapping failed with: %s'%(err), system='UPnP')
        compdef.errback(UPnPError(err))

    def soapCall(self, name, **kwargs):
        request = getattr(self.soap, name)(**kwargs)
        d = soapenurl(request)
        return d

class UPnPMapper(BaseMapper):
    __implements__ = INATMapper
    _ptypes = [ 'UDP', 'TCP']

    def __init__(self):
        self._mapped = {}
        self.upnp = None

    def map(self, port):
        "See shtoom.interfaces.NATMapper.map"
        from twisted.internet import reactor, defer
        self._checkValidPort(port)

        if port in self._mapped:
            return defer.succeed(self._mapped[port])

        cd = defer.Deferred()
        self._mapped[port] = cd

        if self.upnp is None:
            d = getUPnP()
            d.addCallback(lambda x: self._cb_map_gotUPnP(x, port))
        else:
            reactor.callLater(0, lambda: self._cb_map_gotUPnP(self.upnp, port))
        return cd
    map = DeferredCache(map, inProgressOnly=True)

    def _cb_map_gotUPnP(self, upnp, port):
        from shtoom.nat import isBogusAddress, getLocalIPAddress
        # XXX Test that upnp is present
        self.upnp = upnp
        # Extract local address from the port
        locAddr = port.getHost().host
        if isBogusAddress(locAddr):
            # lookup local IP.
            d = getLocalIPAddress()
            d.addCallback(lambda x: self._cb_map_gotLocalIP(x, port))
        else:
            self._cb_map_gotLocalIP(locAddr, port)

    def _cb_map_gotLocalIP(self, locIP, port):
        # Ok, we have the local IP, and the upnp object is setup. Let's rock.
        d = self.upnp.getPortMappings()
        d.addCallback(lambda x:self._cb_map_gotPortMappings(x, locIP, port))

    def _cb_map_gotPortMappings(self, mappings, locIP, port):
        log.msg("existing mappings %r"%(mappings.keys(),), system="UPnP")
        ptype = port.getHost().type
        intport = extport = port.getHost().port
        while True:
            existing = mappings.get((ptype,extport))
            # XXX when the SOAP code fixes up types, remove the 'str()' version
            if existing is None:
                existing = mappings.get((ptype,str(extport)))
            if existing is None:
                break
            exhost = existing['NewInternalClient']
            exint = existing['NewInternalPort']
            exproto = existing['NewProtocol']
            # More string nasties when I fix SOAP typing
            if exproto == ptype and exhost == locIP and exint in (intport, str(intport)):
                # Existing binding for this host/port/proto - replace it
                log.msg("replacing existing mapping for %s:%s"%(ptype,extport),
                                            system="UPnP")
                break
            # skip the obvious race condition as everyone wants 5060 :-(
            extport += random.randint(1,20)
        # XXX hardcoded description makes me sad - should be an optional
        # argument!?
        d = self.upnp.addPortMapping(intport=intport, extport=extport,
                                        desc='Shtoom', proto=ptype, lease=0)
        d.addCallback(lambda x: self.upnp.getExternalIPAddress())
        d.addCallback(lambda x: self.cb_map_addedPortMapping(x, extport, port))

    def cb_map_addedPortMapping(self, extaddr, extport, port):
        cd = self._mapped[port]
        self._mapped[port] = (extaddr, extport)
        cd.callback((extaddr, extport))

    def info(self, port):
        "See shtoom.interfaces.NATMapper.info"
        if port in self._mapped:
            return self._mapped[port]
        else:
            raise ValueError('Port %r is not currently mapped'%(port))

    def unmap(self, port):
        "See shtoom.interfaces.NATMapper.unmap"
        existing = self._mapped.get(port)
        if not existing:
            raise ValueError('Port %r is not currently mapped'%(port))
        if type(existing) is not tuple:
            # Is this a sane decision? Queue up an unmap to trigger when the
            # map is done? Maybe I should make map and unmap share a defcache?
            existing.addCallback(lambda *x: self.unmap(port))
            return existing
        del self._mapped[port]
        return self.upnp.deletePortMapping(existing[1], port.getHost().type)

_cached_upnp = None
def getUPnP():
    "Returns a deferred, which returns a UPnP object"
    global _cached_upnp
    if _cached_upnp is None:
        prot = UPnPProtocol()
        prot.listenMulticast()
        d = prot.discoverUPnP()
        d.addCallback(_cb_gotUPnP).addErrback(log.err)
        return d
    else:
        return _cached_upnp.isAvailable()
getUPnP = DeferredCache(getUPnP, inProgressOnly=False)

def _cb_gotUPnP(upnp):
    if isinstance(upnp, NoUPnPFound):
        log.msg("no UPnP found!", system="UPnP")
        return None
    # A little bit of tricksiness here. If we got the same upnp server,
    # keep the UPnPMapper alive, so that unmap of existing entries work
    # correctly. Otherwise, kill it.
    global _cached_mapper
    if _cached_mapper and _cached_mapper.upnp and _cached_mapper.upnp.controlURL != upnp.controlURL:
        _cached_mapper = None
    return upnp

_cached_mapper = None
def getMapper():
    global _cached_mapper
    if _cached_mapper is None:
        _cached_mapper = UPnPMapper()
    return _cached_mapper

def clearCache():
    getUPnP.clearCache()

if __name__ == "__main__":
    import sys
    from twisted.internet import reactor

    DEBUG = True

    log.startLogging(sys.stdout)
    def done(upnp):
        print "got upnp", upnp
        reactor.stop()
    d = getUPnP()
    d.addCallbacks(done, log.err)
    reactor.run()
