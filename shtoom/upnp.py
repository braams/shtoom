#
# Copyright (C) 2004 Anthony Baxter
# $Id: upnp.py,v 1.2 2004/01/13 14:20:52 anthonybaxter Exp $
# 
# UPnP support.

# We have three modes. No UPnP at all, UPnP only for the SIP port, or 
# UPnP for the SIP port, followed by UPnP for the RTP/RTCP ports.

# UPnP_IGD_WANIPConnection 1.0.doc defines the ExternalPort configuration
# magic.

# Theory of operation:
#
# Multicast address for SSDP is 239.255.255.250 port 1900 (multicast)
#    Listen for SSDP NOTIFYs on mcast 
#    Send an M_SEARCH request to query for any IGDs that are out there - 
#       send 3 packets, listen for a response.



import struct, socket, time
from twisted.internet import reactor, defer, protocol
from twisted.internet.protocol import DatagramProtocol
from twisted.protocols import http


class NoUPnPFound(Exception): pass

def getUPnPSearch():
    return """M-SEARCH * HTTP/1.1\r
Host:239.255.255.250:1900\r
ST:urn:schemas-upnp-org:device:InternetGatewayDevice:1\r
Man:"ssdp:discover"\r
MX:3\r
\r
"""

_setup_portforward_call = """\
<s:Envelope
    xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
    s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:AddPortMapping xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">
      <NewRemoteHost></NewRemoteHost>
      <NewExternalPort>%(ExternalPort)s</NewExternalPort>
      <NewProtocol>%(Protocol)s</NewProtocol>
      <NewInternalPort>%(InternalPort)s</NewInternalPort>
      <NewInternalClient>%(InternalClient)s</NewInternalClient>
      <NewEnabled>%(Enabled)s</NewEnabled>
      <NewPortMappingDescription>%(Description)s</NewPortMappingDescription>
      <NewLeaseDuration>0</NewLeaseDuration>
    </u:AddPortMapping>
  </s:Body>
</s:Envelope>
"""

class UPnPConfig:
    def __init__(self):
        self.URLBase = None
        self.serviceMap = {}

class UPnPProtocol(DatagramProtocol, object):

    def __init__(self, *args, **kwargs):
        self.upnpconfig = UPnPConfig()
        DatagramProtocol.__init__(self, *args, **kwargs)

    def datagramReceived(self, dgram, address):
        response, message = dgram.split('\r\n', 1)
        version, status, textstatus = response.split(None, 2)
        print "got a %s, status %s message %s"%(version, status, message)
        if status == "200":
            self.handleSearchResponse(message)

    def handleSearchResponse(self, message):
        import urlparse
        headers, body = self.processMessage(message)
        loc = headers.get('location')
        if not loc:
            print "No location in response to search!"
            return
        else:
            loc = loc[0]
            prot, host, url, junk, junk, junk = urlparse.urlparse(loc)
            if ':' in host:
                host, port = host.split(':')
                port = int(port)
                protocol.ClientCreator(reactor, UPnPHTTP, 
                                            self, url, (host,port)
                                      ).connectTCP(host, port)

    def processMessage(self, message):
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

    def forwardPort(self, port):
        """Sets up a port forward. Returns a deferred that will be triggered
           with the external (host,port).
        """
        
    def cancelForwardedPort(self, port)
        """Sets up a port forward. Returns a deferred.
        """
        

    def discoverUPnP(self):
        "Discover UPnP devices. Returns a Deferred"
        self._discDef = defer.Deferred()
        search = getUPnPSearch()
        self.transport.write(search, ('239.255.255.250', 1900))
        self.transport.write(search, ('239.255.255.250', 1900))
        self.transport.write(search, ('239.255.255.250', 1900))
        reactor.callLater(3, self.timeoutUPnP)

    def timeoutUPnP(self):
        if hasattr(self, '_discDef'):
            if self.upnpconfig.URLBase is None:
                d = self._discDef
                del self._discDef
                d.errback(NoUPnPFound())

    def listenMulticast(self):
        import socket
        mcast = reactor.listenMulticast(1900, upnp)
        mcast.joinGroup('239.255.255.250', socket.INADDR_ANY)

    def gotRootDesc(self, headers, body):
        from xml.dom.expatbuilder import parseString
        if Debug:
            print "XML is\n", body
        dom = parseString(body, namespaces=0)
        devices = self.findDevicesFromXML(dom)
        if hasattr(self, '_discDef'):
            d = self._discDef 
            del self._discDef
            d.callback(self.upnpconfig)

    def findDevicesFromXML(self, dom):
        root = dom.childNodes[0]

        for c in root.childNodes:
            if c.nodeName == '#text':
                continue
            if c.nodeName == 'specVersion':
                # not that interesting
                continue
            if c.nodeName == 'URLBase':
                # Excellent!
                self.upnpconfig.URLBase = c.childNodes[0].nodeValue
            if c.nodeName == 'device':
                device = self._processDeviceEntry(c)


    def _processDeviceEntry(self, devicexml):
        print "pDE", devicexml
        for dev in devicexml.childNodes:
            if dev.nodeName == '#text':
                continue
            elif dev.nodeName == 'deviceType':
                self.upnpconfig.deviceType = dev.childNodes[0].nodeValue
            elif dev.nodeName == 'friendlyName':
                self.upnpconfig.friendlyName = dev.childNodes[0].nodeValue
            elif dev.nodeName == 'serviceList':
                # Process the serviceList
                for service in dev.childNodes:
                    print "sss5", service
                    serviceType = None
                    if service.nodeName == 'service':
                        for serviceEntry in service.childNodes:
                            if serviceEntry.nodeName == '#text':
                                continue
                            elif serviceEntry.nodeName == 'serviceType':
                                st = serviceEntry.childNodes[0]
                                urn,prefix,what,service,num = st.nodeValue.split(':')
                                serviceType = service
                            elif serviceEntry.nodeName == 'controlURL':
                                ctrlURL = serviceEntry.childNodes[0].nodeValue
                                if serviceType is not None:
                                    self.upnpconfig.serviceMap[serviceType] = ctrlURL

            elif dev.nodeName == 'deviceList':
                # Process the deviceList. 
                # We're looking for a WANDevice
                devices = dev.childNodes
                for subdev in devices:
                    if subdev.nodeName == '#text':
                        continue
                    elif subdev.nodeName == 'device':
                        self._processDeviceEntry(subdev)
            

class UPnPHTTP(http.HTTPClient):
    def __init__(self, upnp, url, (host, port)):
        self.upnp = upnp
        self.url = url
        self.host, self.port = host, port

    def connectionMade(self):
        self.headers = {}
        self.sendCommand('GET', self.url)
        self.sendHeader('Host', '%s:%d'%(self.host, self.port))
        self.sendHeader('User-Agent', 'Shtoom')
        self.endHeaders()

    def handleHeader(self, key, val):
        self.headers.setdefault(key.lower(), []).append(val)

    def handleResponse(self, data):
        self.body = data
        self.upnp.gotRootDesc(self.headers, self.body)

if __name__ == "__main__":
    prot = UPnPProtocol()
    Debug = 1
    prot.broadcastQuery()
    reactor.run()
