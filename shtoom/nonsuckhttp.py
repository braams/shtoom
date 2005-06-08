"""
    A less-sucky HTTP client.

    $Id: nonsuckhttp.py 453 2004-09-20 07:14:54Z anthony $
"""


#import tphttp as http
from twisted.protocols import basic
from twisted.internet import defer, protocol
from twisted.python import log
from urllib2 import Request as URLRequest



class HTTPError(Exception):
    def __init__(self, code, response):
        self.code = code
        self.url = response.geturl()
        self.args = (self.code,self.url)
        self.response = response

    def __repr__(self):
        return '<HTTP Error %d from %s>'%(self.code, self.url)

class Response:
    def __init__(self, url):
        self.status = None
        self.dict = {}
        self.data = ''
        self.url = url
        self._readcount = 0

    def info(self): return self.dict

    def geturl(self): return self.url

    def getheader(self, h):
        return self.dict.get(h)

    def read(self, bytes=None):
        if self._readcount >= len(self.data):
            return ''
        else:
            if bytes is None:
                bytes = len(self.data) - self._readcount

            res = self.data[self._readcount:self._readcount+bytes]
            self._readcount+=bytes
            return res

    def addheader(self, key, value):
        """Add header for field key handling repeats."""
        #print "got a header", key, value
        prev = self.dict.get(key)
        if prev is None:
            self.dict[key] = value
        else:
            combined = ", ".join((prev, value))
            self.dict[key] = combined

    def addcontinuation(self, key, more):
        """Add more field data from a continuation line."""
        prev = self.dict[key]
        self.dict[key] = prev + "\n " + more

    def addbody(self, data):
        self.data += data


class HTTPClient(basic.LineReceiver):

    length = None
    firstLine = 1
    __buffer = ''
    __reqbuffer = None

    def __init__(self, url, resdef, timeout=300):
        if not isinstance(url, URLRequest):
            url = URLRequest(url)
        self.request = url
        self.timeout = timeout
        self.resdef = resdef

    def write_transport(self, data):
        if self.__reqbuffer is None:
            self.__reqbuffer = data
        else:
            self.__reqbuffer += data

    def sendRequest(self):
        "We send the entire request in a single packet"
        self.transport.write(self.__reqbuffer)
        self.__reqbuffer = None

    def sendCommand(self, command, path):
        self.write_transport('%s %s HTTP/1.0\r\n' % (command, path))

    def sendHeader(self, name, value):
        self.write_transport('%s: %s\r\n' % (name, value))

    def endHeaders(self):
        self.write_transport('\r\n')

    def lineReceived(self, line):
        if self.firstLine:
            self.firstLine = 0
            try:
                version, status, message = line.split(None, 2)
            except ValueError:
                # sometimes there is no message
                version, status = line.split(None, 1)
                message = ""
            self.handleStatus(version, status, message)
            return
        if line:
            key, val = line.split(':', 1)
            val = val.lstrip()
            self.handleHeader(key, val)
            if key.lower() == 'content-length':
                self.length = int(val)
        else:
            self.handleEndHeaders()
            self.setRawMode()

    def connectionLost(self, reason):
        self.handleResponseEnd()

    def handleResponseEnd(self):
        if self.__buffer != None:
            b = self.__buffer
            self.__buffer = None
            self.handleResponse(b)

    def handleResponsePart(self, data):
        self.__buffer += data

    def connectionMade(self):
        #print "connectionMade"
        pass

    handleStatus = handleHeader = handleEndHeaders = lambda *args: None

    def rawDataReceived(self, data):
        if self.length is not None:
            data, rest = data[:self.length], data[self.length:]
            self.length -= len(data)
        else:
            rest = ''
        self.handleResponsePart(data)
        if self.length == 0:
            self.handleResponseEnd()
            self.setLineMode(rest)

    def connectionMade(self):
        from twisted.internet import reactor
        #print "sending request"
        self.sendCommand(self.request.get_method(), self.request.get_selector() or '/')
        self.sendHeader('Host', self.request.get_host())
        if self.request.has_data():
            self.sendHeader('Content-Length', str(len(self.request.data)))
        for k,v in self.request.headers.items():
            self.sendHeader(k, v)
        self.endHeaders()
        if self.request.has_data():
            # OMFG httpclient sucks so bad
            self.write_transport(self.request.data)
            self.write_transport('\r\n')
        if self.timeout:
            self._timeoutCall = reactor.callLater(self.timeout, self.requestTimedOut)
        self.sendRequest()
        self.response = Response(self.request.get_full_url())

    def handleTimeout(self):
        "override, if necessary"
        return None

    def requestTimedOut(self):
        # Damn. Request timed out. Oh well.
        self.transport.loseConnection()
        self.handleTimeout()

    def handleResponse401(self):
        from twisted.internet import reactor
        # Plug in a basic auth handler by default
        req = self.request
        resp = self.response
        auth = resp.getheader('WWW-Authenticate')
        if not auth:
            log.err("no auth header in 401 response")
            resdef, self.resdef = self.resdef, None
            resdef.errback(ValueError('401 without auth!'))
            return
        scheme, challenge = auth.split(' ', 1)
        authmeth = 'get%sAuthResponse'%(scheme.capitalize())
        if hasattr(self, authmeth):
            authresp = getattr(self, authmeth)(challenge)
            if authresp:
                resdef, self.resdef = self.resdef, None
                newreq = URLRequest(req.get_full_url(), data=req.data, headers=req.headers)
                newreq.add_header('Authorization', '%s %s'%(scheme, authresp))
                protocol.ClientCreator(reactor, HTTPClient, newreq, resdef, self.timeout
                                                    ).connectTCP(*splithostport(newreq))
        else:
            log.err("auth scheme %s not supported"%scheme)
            resdef, self.resdef = self.resdef, None
            resdef.errback(ValueError('401 auth scheme %s not supported'%scheme))
            return


    def getBasicAuthResponse(self, chal):
        from base64 import encodestring
        if _AuthSource is None:
            if self.resdef:
                log.err("can't auth, no auth source defined")
                resdef, self.resdef = self.resdef, None
                resdef.errback(ValueError('401 basic, but no auth source'))
            return
        else:
            user, password = _AuthSource.get(chal)
            return encodestring('%s:%s'%(user, password))

    def handleResponse(self, data):
        import urlparse
        from twisted.internet import reactor
        req = self.request
        resp = self.response
        resp.addbody(data)

        m = req.get_method()
        if not resp.status:
            # Interrupted, or something like that.
            log.msg('handleResponse without a status?', system='http')
            return
        if hasattr(self, 'handleResponse%d'%resp.status):
            getattr(self, 'handleResponse%d'%resp.status)()
        elif (resp.status in (301, 302, 303, 307) and m in ("GET", "HEAD")
            or resp.status in (301, 302, 303) and m == "POST"):
                # Some sane defaults
            newurl = self.response.getheader('Location')
            newurl = urlparse.urljoin(req.get_full_url(), newurl)
            log.msg("redirecting %s request to %s"%(m, newurl))
            newreq = URLRequest(newurl, data=req.data, headers=req.headers)
            resdef, self.resdef = self.resdef, None
            protocol.ClientCreator(reactor, HTTPClient, newreq, resdef, self.timeout
                                                ).connectTCP(*splithostport(newreq))
        elif (resp.status - resp.status%100) in (400, 500, 600):
            resdef, self.resdef = self.resdef, None
            resdef.errback(HTTPError(resp.status, resp))
        else:
            resdef, self.resdef = self.resdef, None
            resdef.callback(resp)

    def handleStatus(self, version, status, message):
        self._timeoutCall.cancel()
        resp = self.response
        resp.status = int(status)
        resp.version = version
        resp.message = message


    def handleHeader(self, key, value):
        self.response.addheader(key, value)

    def handleHeaderContinuation(self, key, value):
        self.response.addcontinuation(key, value)

class HTTPClientFactory(protocol.ClientFactory):
    noisy = 0
    protocol = HTTPClient

    def __init__(self, *args):
        self.args = args
        self.deferred = defer.Deferred()

    def buildProtocol(self, addr):
        self.instance = self.protocol(*self.args)
        self.instance.resdef.addCallbacks(
                                    self.deferred.callback,
                                    self.deferred.errback)
        return self.instance

    def clientConnectionFailed(self, connector, reason):
        from twisted.internet import reactor
        log.msg("%s.clientConnectionFailed(%s, %s)" % (self, connector, reason,))
        reactor.callLater(0, self.deferred.errback, reason)



class UDPHTTPClient(HTTPClient):
    "the pain, the pain!"

def splithostport(req):
    host = req.get_host()
    if ':' in host:
        host, port = host.split(':',1)
        port = int(port)
    else:
        port = 80
    return host, port

# Ugly hack. Should remove utterly, can be done with passing a factory
# to urlopen instead.
_OpenerClass = HTTPClient
def installOpener(klass):
    global _OpenerClass
    _OpenerClass = klass
    HTTPClientFactory.protocol = _OpenerClass

_AuthSource = None
def installAuthSource(obj):
    global _AuthSource
    _AuthSource = obj

def urlopen(url, factory=None, timeout=300):
    from twisted.internet import reactor

    if factory is None:
        factory = HTTPClientFactory
    resdef = defer.Deferred()
    if isinstance(url, basestring):
        url = URLRequest(url)

    host, port = splithostport(url)
    f = factory(url, resdef, timeout)
    resdef = reactor.connectTCP(host, port, f)
    return f.deferred


if __name__ == "__main__":
    from twisted.internet import reactor
    def testresp(r):
        print r, type(r)
        print r.info(), r.geturl()
        print r.read()
        reactor.stop()
    def testerr(e):
        print "http failed with", e
        reactor.stop()

    from twisted.internet import reactor
    from twisted.python import log
    import sys
    log.startLogging(sys.stdout)
    d = urlopen('http://www.google.com')
    d.addCallbacks(testresp, testerr).addErrback(log.err)
    reactor.run()
