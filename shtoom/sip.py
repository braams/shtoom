# Copyright (C) 2004 Anthony Baxter

'''SIP client code.'''

# A Note For The Reader: This code in this module is _hairy_. It's also 
# ugly, a mess and sorely in need of redesign and refactoring. Do _not_ 
# try and use this to learn Python, or Twisted. Doing so _will_ void the
# warranty on your brain. 

# And yes, a redesign (to make it unit testable, for one thing) is very
# much planned. 

from interfaces import SIP as ISip

from twisted.internet.protocol import DatagramProtocol, ConnectedDatagramProtocol
from twisted.internet import defer
from twisted.internet import reactor
from twisted.protocols import sip as tpsip
from rtp import RTPProtocol

import shtoom
from shtoom import __version__ as ShtoomVersion

_CACHED_LOCAL_IP = None

from twisted.python import log
import random, sys, socket

def errhandler(*args):
    print "BANG", args

def genCallId():
    return 400000000 + random.randint(0,2000000)

def genStandardDate(t=None):
    import time
    if t is None:
        t = time.gmtime()
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", t)

def formatAddress(threetuple):
    """ Format a ( 'display name', URL, {params} ) correctly. Inverse of
        twisted.protocols.sip.parseAddress() 
    """
    display, uri, params = threetuple
    params = ';'.join(['='.join(x) for x in params.items()])
    if params:
        params = ';'+params
    if display:
        out = '"%s" <%s>'%(display, str(uri))
    else:
        out = str(uri)
    if params:
        out = out + params
    return out

class Address:
    def __init__(self, addr, ensureTag=False):
        if isinstance(addr, basestring):
            threetuple = tpsip.parseAddress(addr)
            self._display, self._uri, self._params = threetuple
        elif isinstance(addr, tpsip.URL):
            threetuple = tpsip.parseAddress(str(addr))
            self._display, self._uri, self._params = threetuple
        elif isinstance(addr, self.__class__):
            threetuple = tpsip.parseAddress(str(addr))
            self._display, self._uri, self._params = threetuple
        elif len(addr) == 3:
            self._display, self._uri, self._params = addr
        else:
            raise ValueError, "Address() takes either an address or a 3-tuple"
        if ensureTag and not self._params.has_key('tag'):
            self._params['tag'] = self.genTag()

    def genTag(self):
        tag = ('%04x'%(random.randint(0, 2**10)))[:4]
        tag += ('%04x'%(random.randint(0, 2**10)))[:4]
        return tag

    def getDisplayName(self): 
        return self._display

    def getURI(self, parsed=True): 
        print self._uri, type(self._uri)
        if parsed:
            return self._uri
        else:
            return str(self._uri)

    def getParams(self): return self._params

    def __str__(self):
        return formatAddress((self._display, self._uri, self._params))
                
class Dialog:
    def __init__(self, callid=None, caller=None, callee=None):
        self._callid = callid
        self._caller = caller
        self._callee = callee

    def setCaller(self, address):
        if not isinstance(address, Address):
            address = Address(address)
        self._caller = address

    def setCallee(self, address):
        if not isinstance(address, Address):
            address = Address(address)
        self._callee = address

    def setCallID(self, callid=None):
        if not callid:
            callid = getCallId()
        self._callid = callid

class Call(object):
    '''State machine for a phone call (inbound or outbound).'''

    cookie = _callID = uri = None
    nonce_count = 1
    sip = None
    _invite = None
    def __init__(self, phone, deferred, uri=None, callid=None):
        self.sip = phone
        self.compDef = deferred
        self.call_attempts = 0
        self._callID = None
        self._remoteURI = None
        self._remoteAOR = None
        self._localAOR = None
        self._outboundProxyURI = None
        self._caller = None
        self._callee = None
        self.state = 'NEW'
        self._needSTUN = False
        self.cancel_trigger = None
        if callid:
            self.setCallID(callid)
        self.cseq = random.randint(1000,5000)

    def setupLocalSIP(self, uri=None, via=None):
        ''' Setup SIP stuff at this end. Call with either a t.p.sip.URL
            (for outbound calls) or a t.p.sip.Via object (for inbound calls).

            returns a Deferred that will be triggered when the local SIP
            end is setup
        '''
        self.setupDeferred = defer.Deferred()
        outboundProxyURI = self.sip.app.getPref('outbound_proxy_url')
        if outboundProxyURI:
            print 'outboundProxyURI=' + outboundProxyURI
            self._outboundProxyURI = tpsip.parseURL(outboundProxyURI)
        if via is not None:
	    remote = tpsip.URL(host=via.host, port=via.port)
        elif isinstance(uri, Address):
            remote = uri.getURI(parsed=True)
        else:
            remote = uri
        # XXX tofix
        self.setLocalIP(dest=(remote.host, remote.port or 5060))
        return self.setupDeferred

    def abortCall(self):
        # Bail out.
        self.state = 'ABORTED'

    def setCallID(self, callid=None):
        if callid:
            self._callID = callid
        else:
            self._callID = '%s@%s'%(genCallId(), self.getLocalSIPAddress()[0])

    def setState(self, state):
        self.state = state

    def getState(self):
        return self.state

    def getSTUNState(self):
        return self._needSTUN


    def setLocalIP(self, dest):
        """ Try and determine the local IP address to use. We use a
            ConnectedDatagramProtocol in the (faint?) hope that on a machine
            with multiple interfaces, we'll get the right one
        """
        # XXX Allow over-riding
        from shtoom.stun import StunHook, getPolicy
        global _CACHED_LOCAL_IP
        host, port = dest
        getPref = self.sip.app.getPref
        if getPref('localip') is not None or _CACHED_LOCAL_IP is not None:
            ip = getPref('localip') or _CACHED_LOCAL_IP
            locAddress = (ip, getPref('listenport') or 5060)
            remAddress = ( host, port )
            # Argh. Do a DNS lookup on remAddress
        else:
            # it is a hack!
            protocol = ConnectedDatagramProtocol()
            port = reactor.connectUDP(host, port, protocol)
            if protocol.transport:
                locAddress = (protocol.transport.getHost()[1], getPref('listenport') or 5060)
                remAddress = protocol.transport.getPeer()[1:3]
                port.stopListening()
                log.msg("discovered local address %r, remote %r"%(locAddress,
                                                                  remAddress))
                _CACHED_LOCAL_IP = locAddress[0]
            else:
                self.compDef.errback(ValueError("couldn't connect to %s"%(
                                            host)))
                self.abortCall()
                return None
        useStun = getPolicy().checkStun(locAddress[0], remAddress[0])
        if useStun is True:
            self._needSTUN = True
            log.msg("stun policy says yes, use STUN")
            deferred = defer.Deferred()
            deferred.addCallback(self.setStunnedLocalIP).addErrback(log.err)
            SH = StunHook(self.sip)
            deferred = SH.discoverStun(deferred)
        elif useStun is False:
            self._localIP, self._localPort = locAddress
            if not self._callID:
                self.setCallID()
            self.sip.updateCallObject(self, self.getCallID())
            self.setupDeferred.callback((self._localIP, self._localPort))
        else:
            # None. STUN stuff failed. Abort.
            from shtoom.exceptions import HostNotKnown
            d = self.compDef
            del self.compDef
            d.errback(HostNotKnown)
            self.setState('ABORTED')

    def setStunnedLocalIP(self, (host, port)):
        log.msg("according to STUN, local address is %s:%s"%(host, port))
        self._localIP = host
        self._localPort = port
        # XXX Check for multiple firings!
        if not self._callID:
            self.setCallID()
            self.sip.updateCallObject(self, self.getCallID())
        self.setupDeferred.callback((host,port))

    def getCSeq(self, incr=0):
        if incr:
            self.cseq += 1
        return self.cseq

    def getCallID(self):
        return self._callID

    def getLocalSIPAddress(self):
        return (self._localIP, self._localPort or 5060)

    def getRemoteSIPAddress(self):
        if self._outboundProxyURI is not None:
            return (self._outboundProxyURI.host, (self._outboundProxyURI.port or 5060))
        elif self._remoteURI is not None:
            return (self._remoteURI.host, (self._remoteURI.port or 5060))
        else:
            return (self._remoteAOR.host, (self._remoteAOR.port or 5060))

    def getLocalAOR(self, full=False):
        if not self._localAOR:
            username = self.sip.app.getPref('username')
            email_address = self.sip.app.getPref('email_address')
            self._localFullAOR = Address('"%s" <sip:%s>'%(
                            username, email_address) ,ensureTag=True)
            self._localAOR = self._localFullAOR.getURI(parsed=True)
        if full:
            return self._localFullAOR
        else:
            return self._localAOR

    def acceptedCall(self, cookie):
        print "acceptedCall setting cookie to", cookie
        self.cookie = cookie
        self.sendResponse(self._invite, 200)
        self.setState('INVITE_OK')

    def rejectCall(self, message=None):
        ''' Accept currently pending call.
        '''
        from shtoom.exceptions import CallRejected
        print "rejecting because", message
        self.sendResponse(self._invite, 603)
        self.setState('ABORTED')
        self.compDef.errback(CallRejected)

    def sendResponse(self, message, code):
        ''' Send a response to a message. message is the response body,
            code is the response code (e.g.  200 for OK)
        '''
        from shtoom.multicast.SDP import SDP
        if message.method == 'INVITE' and code == 200:
            sdp = self.sip.app.getSDP(self.cookie)
            othersdp = SDP(message.body)
            sdp.intersect(othersdp)
            if not sdp.rtpmap:
                self.sendResponse(message, 406)
                self.setState('ABORTED')
                return
            self.sip.app.selectFormat(self.cookie, sdp.rtpmap)
        resp = tpsip.Response(code)
        #via = tpsip.parseViaHeader(message.headers['via'][0])
        #branch = via.branch
        #if branch:
        #    branch = ';branch=%s'%branch
        #else:
        #    branch = ''
        vias = message.headers['via']
        for via in vias:
            resp.addHeader('via', via)
        if not self._callee:
            addr = message.headers['to'][0]
            self._callee = Address(addr, ensureTag=True)
        if not self._caller:
            addr = message.headers['from'][0]
            self._caller = Address(addr)
        resp.addHeader('to', str(self._callee))
        resp.addHeader('from', str(self._caller))
        resp.addHeader('date', genStandardDate())
        resp.addHeader('call-id', message.headers['call-id'][0])
        resp.addHeader('server', 'Shtoom/%s'%ShtoomVersion)
        resp.addHeader('cseq', message.headers['cseq'][0])
        resp.addHeader('allow-events', 'telephone-event')
        if message.method == 'INVITE' and code == 200:
            lhost, lport = self.getLocalSIPAddress()
            username = self.sip.app.getPref('username')
            resp.addHeader('contact', '<sip:%s@%s:%s>'%(
                                        username, lhost, lport))
            # We include SDP here
            resp.addHeader('content-type', 'application/sdp')
            sdp = sdp.show()
            resp.addHeader('content-length', len(sdp))
            resp.bodyDataReceived(sdp)
        else:
            resp.addHeader('content-length', 0)
        resp.creationFinished()
        try:
            via0 = tpsip.parseViaHeader(vias[0])
            viaAddress = (via0.host, via0.port)
            self.sip.transport.write(resp.toString(),viaAddress)
            self.sip.app.debugMessage("Response sent to %r\n%s"%(viaAddress,resp.toString()))
        except (socket.error, socket.gaierror):
            e,v,t = sys.exc_info()
            #self.compDef.errback(e(v))
            self.setState('ABORTED')

    def startOutboundCall(self, toAddr):
        # XXX Set up a callLater in case we don't get a response, for a
        # retransmit
        # XXX Set up a timeout for the call completion
        uri = tpsip.parseURL(toAddr)
        self._remoteAOR = uri
        # XXX Display name? needs an option
        self._callee = Address(uri, ensureTag=False)
        self._caller = self.getLocalAOR()
        d = self.setupLocalSIP(uri=uri)
        d.addCallback(lambda x:self.startSendInvite(toAddr, init=1)
                                                        ).addErrback(log.err)

    def startInboundCall(self, invite):
        via = tpsip.parseViaHeader(invite.headers['via'][0])
        d = self.setupLocalSIP(via=via)
        contact = invite.headers['contact']
        if type(contact) is list:
            contact = contact[0]
        self.contact = contact
        self._caller = Address(invite.headers['from'][0])
        self._callee = Address(invite.headers['to'][0], ensureTag=True)
        self._remoteURI = Address(self.contact).getURI(parsed=True)
        self._remoteAOR = self._callee.getURI()
        d.addCallback(lambda x:self.recvInvite(invite)).addErrback(log.err)
        if invite.headers.has_key('subject'):
            desc = invite.headers['subject'][0]
        else:
            name,uri,params =  tpsip.parseAddress(invite.headers['from'][0])
            desc = "From: %s %s" %(name,uri)
        d.addCallback(lambda justWaitingForGetLocalSIP:
                      self.sip.app.acceptCall(self,
                                              calltype='inbound',
                                              desc=desc,
                                              localIP=self.getLocalSIPAddress()[0],
                                              withSTUN=self.getSTUNState() ,
                                              toAddr=invite.headers.get('to'),
                                              fromAddr=invite.headers.get('from'),
                                              ).addCallbacks(
                                                   self.acceptedCall, 
                                                   self.rejectCall).addErrback(log.err)
                      and None)
        #self.app.incomingCall(subj, call, defaccept, defsetup)

    def recvInvite(self, invite):
        ''' Received an INVITE from another UA. If we're already on a
            call, it's an attempt to modify - send a 488 in this case.
        '''
        # XXX if self.getState() is not 'NEW', send a 488
        if self.getState() in ( 'SENT_RINGING', 'INVITE_OK' ):
            # Nag, nag, nag. Shut the fuck up, I'm answering...
            return
        self._invite = invite
        self.sendResponse(invite, 180)
        if self.getState() != 'ABORTED':
            self.setState('SENT_RINGING')
        self.installTeardownTrigger()

    def startSendInvite(self, toAddr, init=0):
        print "startSendInvite", init
        if init:
            d = self.sip.app.acceptCall(self,
                                        calltype='outbound',
                                        localIP=self.getLocalSIPAddress()[0],
                                        withSTUN=self.getSTUNState(),
                                        )
            d.addCallback(lambda x:self.sendInvite(toAddr, cookie=x, init=init)
                                                        ).addErrback(log.err)
        else:
            self.sendInvite(toAddr, init=0)

    def sendInvite(self, toAddr, cookie=None, auth=None, authhdr=None, init=0):
        if cookie:
            print "sendinvite setting cookie to", cookie
            self.cookie = cookie
        if self.getState() == "ABORTED":
            d = self.compDef
            del self.compDef
            d.callback('call aborted')
            return
        invite = tpsip.Request('INVITE', str(self._remoteAOR))
        # XXX refactor all the common headers and the like
        invite.addHeader('via', 'SIP/2.0/UDP %s:%s;rport'%
                                                self.getLocalSIPAddress())
        invite.addHeader('cseq', '%s INVITE'%self.getCSeq(incr=1))
        invite.addHeader('to', str(self._callee))
        invite.addHeader('content-type', 'application/sdp')
        invite.addHeader('from', str(self._caller))
        invite.addHeader('call-id', self.getCallID())
        invite.addHeader('subject', str(self.getLocalAOR(full=True)))
        invite.addHeader('allow-events', 'telephone-event')
        invite.addHeader('user-agent', 'Shtoom/%s'%ShtoomVersion)
        if auth is not None:
            print auth, authhdr
            invite.addHeader(authhdr, auth)
        lhost, lport = self.getLocalSIPAddress()
        username = self.sip.app.getPref('username')
        invite.addHeader('contact', '"%s" <sip:%s:%s;transport=udp>'%(
                                username, lhost, lport))
        s = self.sip.app.getSDP(self.cookie)
        sdp = s.show()
        invite.addHeader('content-length', len(sdp))
        invite.bodyDataReceived(sdp)
        invite.creationFinished()
        self._remoteAOR = self._callee.getURI()
        try:
            self.sip.transport.write(invite.toString(), self.getRemoteSIPAddress())
            #print "Invite sent", invite.toString()
        except (socket.error, socket.gaierror):
            e,v,t = sys.exc_info()
            self.compDef.errback(e(v))
            self.setState('ABORTED')
        else:
            self.setState('SENT_INVITE')
            self.installTeardownTrigger()

    def extractURI(self, val):
        name,uri,params = tpsip.parseAddress(val)
        return uri.toString()

    def sendAck(self, okmessage, startRTP=0):
        from shtoom.multicast.SDP import SDP
        username = self.sip.app.getPref('username')
        oksdp = SDP(okmessage.body)
        sdp = self.sip.app.getSDP(self.cookie)
        sdp.intersect(oksdp)
        if not sdp.rtpmap:
            self.sendResponse(message, 406)
            self.setState('ABORTED')
            return
        self.sip.app.selectFormat(self.cookie, sdp.rtpmap)
        contact = okmessage.headers['contact']
        if type(contact) is list:
            contact = contact[0]
        self.contact = contact
        self._remoteURI = Address(self.extractURI(contact)).getURI(parsed=True)
        self._callee = Address(okmessage.headers['to'][0])
        ack = tpsip.Request('ACK', str(self._remoteAOR))
        # XXX refactor all the common headers and the like
        ack.addHeader('via', 'SIP/2.0/UDP %s:%s;rport'%self.getLocalSIPAddress())
        ack.addHeader('cseq', '%s ACK'%self.getCSeq())
        ack.addHeader('to', str(self._callee))
        ack.addHeader('from', str(self._caller))
        ack.addHeader('call-id', self.getCallID())
        ack.addHeader('allow-events', 'telephone-event')
        ack.addHeader('user-agent', 'Shtoom/%s'%ShtoomVersion)
        ack.addHeader('content-length', 0)
        ack.creationFinished()
        if hasattr(self, 'compDef'):
            cb = self.compDef.callback
            del self.compDef
        else:
            cb = lambda *args: None
        addr = self._remoteURI.host, self._remoteURI.port or 5060
        log.msg("sending ACK to %s %s"%addr)
        print "sending ACK to %s %s"%addr
        self.sip.transport.write(ack.toString(), addr)
        self.setState('CONNECTED')
        if startRTP:
            self.sip.app.startCall(self.cookie, (oksdp.ipaddr,oksdp.port), cb)
        self.sip.app.statusMessage("Call Connected")

    def sendBye(self):
        username = self.sip.app.getPref('username')
        uri = self._remoteURI
        dest = uri.host, (uri.port or 5060)
        bye = tpsip.Request('BYE', str(self._remoteAOR))
        # XXX refactor all the common headers and the like
        bye.addHeader('via', 'SIP/2.0/UDP %s:%s;rport'%self.getLocalSIPAddress())
        bye.addHeader('cseq', '%s BYE'%self.getCSeq(incr=1))
        bye.addHeader('to', str(self._callee))
        bye.addHeader('from', str(self._caller))
        bye.addHeader('call-id', self.getCallID())
        bye.addHeader('user-agent', 'Shtoom/%s'%ShtoomVersion)
        bye.addHeader('content-length', 0)
        bye.creationFinished()
        bye = bye.toString()
        print "sending BYE to %s %s"%dest
        self.sip.transport.write(bye, dest)
        self.setState('SENT_BYE')

    def sendCancel(self):
        """ Sends a CANCEL message to kill a call that's in the process of
            being established
        """
        username = self.sip.app.getPref('username')
        uri = self._remoteAOR
        dest = uri.host, (uri.port or 5060)
        cancel = tpsip.Request('CANCEL', str(self._remoteAOR))
        # XXX refactor all the common headers and the like
        cancel.addHeader('via', 'SIP/2.0/UDP %s:%s;rport'%self.getLocalSIPAddress())
        cancel.addHeader('cseq', '%s CANCEL'%self.getCSeq(incr=1))
        cancel.addHeader('to', str(self._callee))
        cancel.addHeader('from', str(self._caller))
        cancel.addHeader('call-id', self.getCallID())
        cancel.addHeader('user-agent', 'Shtoom/%s'%ShtoomVersion)
        cancel.addHeader('content-length', 0)
        cancel.creationFinished()
        cancel = cancel.toString()
        print "sending CANCEL to %s %s"%dest
        self.sip.transport.write(cancel, dest)
        self.setState('SENT_CANCEL')

    def recvBye(self, message):
        ''' An in-progress call got a BYE from the other end. Hang up
            call, send a 200.
        '''
        self.sendResponse(message, 200)

    def recvCancel(self, message):
        """ The remote UAC changed it's mind about the new call and
            gave up.
        """
        self.sendResponse(message, 487)
        self.setState('ABORTED')
        self.sip.app.endCall(self.cookie)

    def recvAck(self, message):
        ''' The remote UAC has ACKed our response to their INVITE.
            Start sending and receiving audio.
        '''
        from shtoom.multicast.SDP import SDP
        sdp = SDP(self._invite.body)
        self.setState('CONNECTED')
        if hasattr(self, 'compDef'):
            d, self.compDef = self.compDef, None
            self.sip.app.startCall(self.cookie, (sdp.ipaddr,sdp.port),
                                   d.callback)

    def recvOptions(self, message):
        """ Received an OPTIONS request from a remote UA.
            Put together a 200 response if we're ok with the Require headers,
            otherwise an error (XXXXX)
        """

    def installTeardownTrigger(self):
        if 0 and self.cancel_trigger is None:
            t = reactor.addSystemEventTrigger('before',
                                              'shutdown',
                                              self.dropCall,
                                              appTeardown=True)
            self.cancel_trigger = t

    def dropCall(self, appTeardown=False):
        '''Drop call '''
        # XXX return a deferred, and handle responses properly
        if not appTeardown and self.cancel_trigger is not None:
            reactor.removeSystemEventTrigger(self.cancel_trigger)
        state = self.getState()
        print "dropcall in state", state
        if state == 'NONE':
            self.sip.app.debugMessage("no call to drop")
        elif state in ( 'CONNECTED', ):
            self.sendBye()
            self.setState('SENT_BYE')
            # XXX callLater to give up...
        elif state in ( 'SENT_INVITE', ):
            self.sendCancel()
            self.setState('SENT_CANCEL')
            # XXX callLater to give up...
        elif state in ( 'NEW', ):
            self.setState('ABORTED')

    def _getHashingImplementation(self, algorithm):
        # lambdas assume digest modules are imported at the top level
        import md5, sha
        if algorithm.lower() == 'md5':
            H = lambda x: md5.new(x).hexdigest()
        elif algorithm.lower() == 'sha':
            H = lambda x: sha.new(x).hexdigest()
        # XXX MD5-sess
        KD = lambda s, d, H=H: H("%s:%s" % (s, d))
        return H, KD

    def calcAuth(self, method, uri, authchal, cred):
        (user, passwd) = cred
        from urllib2 import parse_http_list
        import digestauth
        authmethod, auth = authchal.split(' ', 1)
        if authmethod.lower() != 'digest':
            raise ValueError, "Unknown auth method %s"%(authmethod)
        chal = digestauth.parse_keqv_list(parse_http_list(auth))
        qop = chal.get('qop', None)
        if qop and qop.lower() != 'auth':
            raise ValueError, "can't handle qop '%s'"%(qop)
        realm = chal.get('realm')
        algorithm = chal.get('algorithm', 'md5')
        nonce = chal.get('nonce')
        opaque = chal.get('opaque')
        H, KD = self._getHashingImplementation(algorithm)
        if user is None or passwd is None:
            raise RuntimeError, "Auth required, %s %s"%(user,passwd)
        A1 = '%s:%s:%s'%(user, chal['realm'], passwd)
        A2 = '%s:%s'%(method, uri)
        if qop is not None:
            self.nonce_count += 1
            ncvalue = '%08x'%(self.nonce_count)
            cnonce = digestauth.generate_nonce(bits=16,
                                           randomness=
                                              str(nonce)+str(self.nonce_count))
            # XXX nonce isn't there for proxy-auth. :-(
            noncebit =  "%s:%s:%s:%s:%s" % (nonce,ncvalue,cnonce,qop,H(A2))
            respdig = KD(H(A1), noncebit)
        else:
            noncebit =  "%s:%s" % (nonce,H(A2))
            respdig = KD(H(A1), noncebit)
        base = '%s username="%s", realm="%s", nonce="%s", uri="%s", ' \
               'response="%s"' % (authmethod, user, realm, nonce,
                                  uri, respdig)
        if opaque:
            base = base + ', opaque="%s"' % opaque
        if algorithm.lower() != 'md5':
            base = base + ', algorithm="%s"' % algorithm
        if qop:
            base = base + ', qop=auth, nc=%s, cnonce="%s"'%(ncvalue, cnonce)
        return base

    def recvResponse(self, message):
        state = self.getState()
        print "Handling %s while in state %s"%(message.code, state)
        if message.code in ( 100, 180, 181, 182 ):
            return
        elif message.code == 183:
            self.sip.app.debugMessage('Should handle early media here:\n' + message.toString())            
        elif message.code == 200:
            if state == 'SENT_INVITE':
                self.sip.app.debugMessage("Got Response 200\n")
                self.sendAck(message, startRTP=1)
            elif state == 'CONNECTED':
                self.sip.app.debugMessage('Got duplicate OK to our ACK')
                self.sendAck(message)
            elif state == 'SENT_BYE':
                self.sip.app.endCall(self.cookie)
                self.sip._delCallObject(self.getCallID())
                self.sip.app.debugMessage("Hung up on call %s"%self.getCallID())
                self.sip.app.statusMessage("Call Disconnected")
            else:
                self.sip.app.debugMessage('Got OK in unexpected state %s'%state)
        elif message.code - (message.code%100) == 400:
            if state == 'SENT_CANCEL' and message.code == 487:
                print "cancelled"
                self.sip.app.endCall(self.cookie)
                self.sip._delCallObject(self.getCallID())
                self.sip.app.debugMessage("Hung up on call %s"%self.getCallID())
                self.sip.app.statusMessage("Call Disconnected")
                return
            self.call_attempts += 1
            if self.call_attempts > 5:
                print "TOO MANY AUTH FAILURES"
                self.setState('ABORTED')
                return
            if message.code in ( 401, 407 ):
                if state in ( 'SENT_INVITE', ):
                    if message.code == 401:
                        inH, outH = 'www-authenticate', 'authorization'
                    else:
                        inH, outH = 'proxy-authenticate', 'proxy-authorization'
                    a = message.headers.get(inH)
                    if a:
                        uri = str(self._remoteAOR)

                        credDef = self.sip.app.authCred('INVITE', uri,
                                        retry=(self.call_attempts > 1)).addErrback(log.err)
                        credDef.addCallback(lambda c, uri=uri, chal=a[0]:
                                        self.calcAuth('INVITE',
                                                      uri=uri,
                                                      authchal=chal,
                                                      cred=c)
                            ).addCallback(lambda a, h=outH:
                                        self.sendInvite(toAddr=None,
                                                        auth=a,
                                                        authhdr=h)
                            ).addErrback(log.err)
                    else:
                        # * is retarded. If you send in an incorrect digest auth,
                        # you just get back a 401/407, with no auth challenge.
                        # In this case, retry without an auth header to get another
                        # challenge.
                        if self.call_attempts > 1:
                            self.sendInvite(str(self._callee))
                        else:
                            print "401/407 and no auth header"
                else:
                    print "Unknown state '%s' for a 401/407"%(state)
            else:
                self.sip.app.debugMessage(message.toString())
                self.sip.app.endCall(self.cookie, 'Other end sent %s'%message.toString())
                self.sip._delCallObject(self.getCallID())
                self.sip.app.statusMessage("Call Failed: %s %s"%(message.code,
                                                             message.phrase))
        elif message.code - (message.code%100) == 500:
            self.sip.app.debugMessage(message.toString())
            self.sip.app.endCall(self.cookie, 'Other end sent %s'%message.toString())
            self.sip._delCallObject(self.getCallID())
            self.sip.app.statusMessage("Call Failed: %s %s"%(message.code,
                                                             message.phrase))
        elif message.code - (message.code%100) == 600:
            self.sip.app.debugMessage(message.toString())
            self.sip.app.endCall(self.cookie, 'Other end sent %s'%message.toString())
            self.sip._delCallObject(self.getCallID())
            self.sip.app.statusMessage("Call Failed: %s %s"%(message.code,
                                                             message.phrase))
        else:
            self.sip.app.debugMessage(message.toString())

class Registration(Call):
    "State machine for registering with a server."

    def __init__(self, phone, deferred):
        self.sip = phone
        self.compDef = deferred
        self.regServer = None
        self.regAOR = None
        self.state = 'NEW'
        self._needSTUN = False
        self.cseq = random.randint(1000,5000)
        self.nonce_count = 0
        self.cancel_trigger = None
        self.register_attempts = 0
        self._outboundProxyURI = None

    def startRegistration(self):
        import copy
        self.regServer = Address(self.sip.app.getPref('register_uri'))
        self.regAOR = self.regServer.getURI(parsed=True)
        self._remoteURI = self._remoteAOR = self.regAOR
        # XXX Display Name
        self.regAOR.username = self.sip.app.getPref('username')
        self.regAOR = Address(self.regAOR)
        self._localAOR = self._localFullAOR = Address(self.regAOR)
        self.regURI = copy.copy(self.regServer)
        #self.regURI.port = None
        d = self.setupLocalSIP(self.regServer)
        d.addCallback(self.sendRegistration).addErrback(log.err)

    def sendRegistration(self, cb=None, auth=None, authhdr=None):
        username = self.sip.app.getPref('username')
        invite = tpsip.Request('REGISTER', str(self.regURI))
        # XXX refactor all the common headers and the like
        invite.addHeader('via', 'SIP/2.0/UDP %s:%s;rport'%
                                                self.getLocalSIPAddress())
        invite.addHeader('cseq', '%s REGISTER'%self.getCSeq(incr=1))
        invite.addHeader('to', str(self.regAOR))
        invite.addHeader('from', str(self.regAOR))
        state =  self.getState()
        if state in ( 'NEW', 'SENT_REGISTER', 'REGISTERED' ):
            invite.addHeader('expires', 900)
        elif state in ( 'CANCEL_REGISTER' ):
            invite.addHeader('expires', 0)
        invite.addHeader('call-id', self.getCallID())
        if auth is not None:
            invite.addHeader(authhdr, auth)
        invite.addHeader('user-agent', 'Shtoom/%s'%ShtoomVersion)
        lhost, lport = self.getLocalSIPAddress()
        invite.addHeader('contact', '<sip:%s@%s:%s>'%(
                                username, lhost, lport))
        invite.addHeader('content-length', '0')
        invite.creationFinished()
        try:
            self.sip.transport.write(invite.toString(), self.getRemoteSIPAddress())
        except (socket.error, socket.gaierror):
            e,v,t = sys.exc_info()
            self.compDef.errback(e(v))
            self.setState('ABORTED')
        else:
            if self.getState() in ( 'NEW', 'REGISTERED' ):
                self.setState('SENT_REGISTER')
        self.sip.app.debugMessage("register sent\n"+invite.toString())

    def sendAuthResponse(self, authhdr, auth):
        self.sendRegistration(auth=auth, authhdr=authhdr)

    def recvResponse(self, message):
        state = self.getState()
        if message.code in ( 401, 407 ):
            self.register_attempts += 1
            if self.register_attempts > 5:
                print "REGISTRATION FAILED"
                self.setState('FAILED')
                return
            if state in ( 'SENT_REGISTER', 'CANCEL_REGISTER' ):
                if message.code == 401:
                    inH, outH = 'www-authenticate', 'authorization'
                else:
                    inH, outH = 'proxy-authenticate', 'proxy-authorization'
                a = message.headers.get(inH)
                if a:
                    uri = str(self.regURI)
                    credDef = self.sip.app.authCred('REGISTER', uri,
                                        retry=(self.register_attempts > 1)).addErrback(log.err)
                    credDef.addCallback(lambda c, uri=uri, chal=a[0]:
                                        self.calcAuth('REGISTER',
                                                      uri=uri,
                                                      authchal=chal,
                                                      cred=c)
                            ).addCallback(lambda a, h=outH:
                                        self.sendRegistration(auth=a, authhdr=h)
                            ).addErrback(log.err)

                else:
                    # * is retarded. If you send in an incorrect digest auth,
                    # you just get back a 401/407, with no auth challenge.
                    # In this case, retry without an auth header to get another
                    # challenge.
                    if self.register_attempts > 1:
                        self.sendRegistration()
                    elif state == 'CANCEL_REGISTER':
                        self.setState('UNREGISTERED')
                        d = self._cancelDef
                        del self._cancelDef
                        d.callback(self)
                    else:
                        self.sip.app.statusMessage("Registration: auth failed")
            else:
                print "Unknown registration state '%s' for a 401/407"%(state)
        elif message.code in ( 200, ):
            self.sip.app.statusMessage("Registration: OK")
            # Woo. registration succeeded.
            self.register_attempts = 0
            if state == 'SENT_REGISTER':
                self.setState('REGISTERED')
                reactor.callLater(840, self.sendRegistration)
                if 0 and self.cancel_trigger is None:
                    t = reactor.addSystemEventTrigger('before',
                                                      'shutdown',
                                                      self.cancelRegistration)
                    self.cancel_trigger = t
            elif state == 'CANCEL_REGISTER':
                self.setState('UNREGISTERED')
                d = self._cancelDef
                del self._cancelDef
                d.callback(self)
            else:
                print "Unknown state '%s' for a 200"%(state)
        elif message.code in ( 100, ):
            # Trying?!?
            pass
        else:
            if state == 'CANCEL_REGISTER':
                self.setState('UNREGISTERED')
                d = self._cancelDef
                del self._cancelDef
                d.callback(self)
            else:
                log.err("don't know about %s for registration"%(message.code))

    def cancelRegistration(self):
        # Cancel this outstanding registration. Should return a deferred
        # to pause the shutdown until we're done.
        # Send a registration with expires:0
        d = defer.Deferred()
        self.setState('CANCEL_REGISTER')
        self.sendRegistration()
        self._cancelDef = d
        return d





class SipPhone(DatagramProtocol, object):
    '''A SIP phone.'''

    __implements__ = ISip,

    def __init__(self, app, *args, **kwargs):
        self.app = app
        self._calls = {}
        super(SipPhone, self).__init__(*args, **kwargs)

    def getCalls(self):
        return [c for c in self._calls.values() if not isinstance(c, Registration)]

    def getRegistrations(self):
        return [c for c in self._calls.values() if isinstance(c, Registration)]

    def register(self, removed=None):
        if removed:
            print "cancelled", removed
            self._delCallObject(removed.getCallID())
        if self.app.getPref('register_uri') is not None:
            existing = self.getRegistrations()
            if existing:
                for reg in existing:
                    print "removing", reg, existing
                    d = reg.cancelRegistration()
                    d.addCallbacks(self.register, log.err)
            else:
                print "no outstanding registrations, registering"
                d = defer.Deferred()
                r = Registration(self,d)
                r.startRegistration()
                return d

    def _newCallObject(self, deferred, to=None, callid=None):
        call = Call(self, deferred, uri=to, callid=callid)
        print "XXX", call, call.getState(), call.getCallID()
        if call.getState() != 'ABORTED':
            if call.getCallID():
                self._calls[call.getCallID()] = call
            return call

    def updateCallObject(self, call, callid):
        "Used when Call setup returns a deferred result (e.g. STUN)"
        self._calls[call.getCallID()] = call

    def _getCallObject(self, callid):
        if type(callid) is list:
            callid = callid[0]
        if callid.startswith('<') and callid.endswith('>'):
            callid = callid[1:-1]
        return self._calls.get(callid)

    def _delCallObject(self, callid):
        if type(callid) is list:
            callid = callid[0]
        if callid.startswith('<') and callid.endswith('>'):
            callid = callid[1:-1]
        del self._calls[callid]

    def placeCall(self, uri):
        """Place a call.

        uri should be a string, an address of the person we are calling,
        e.g. 'sip:foo@example.com'.

        Returns a Call object and a Deferred
        """
        self.app.debugMessage("placeCall starting")
        _d = defer.Deferred()
        try:
            call = self._newCallObject(_d, to=uri)
        except:
            e,v,t = sys.exc_info()
            print "call creation failed", v
            return defer.fail(v)
        print "call is", call
        if call is None:
            from shtoom.exceptions import CallFailed
            _d.errback(CallFailed)
            return _d
        invite = call.startOutboundCall(uri)
        return _d

    def datagramReceived(self, datagram, addr):
        self.app.debugMessage("Got a SIP packet from %s:%s"%(addr))
        mp = tpsip.MessagesParser(self.sipMessageReceived)
        self.app.debugMessage("SIP PACKET\n%s"%(datagram))
        mp.dataReceived(datagram)
        mp.dataDone()

    def sipMessageReceived(self, message):
        if hasattr(message, 'code'):
            message.response, message.request = True, False
        elif hasattr(message, 'method'):
            message.response, message.request = False, True
        else:
            raise ValueError("message is neither fish nor fowl %s"%(message))
        if message.response:
            self.app.debugMessage("got SIP response %s: %s"%(
                                        message.code, message.phrase))
            self.app.statusMessage("%s: %s"%(message.code,message.phrase))
            self.app.debugMessage("got SIP response\n %s"%( message.toString()))
        else:
            self.app.debugMessage("got SIP request %s: %s"%(
                                        message.method, message.uri))
            self.app.debugMessage("got SIP request\n %s"%( message.toString()))
        callid = message.headers['call-id']
        call = self._getCallObject(callid)
        if message.response and not call:
            self.app.debugMessage("SIP response refers to unknown call %s %r"%(
                                                    callid, self._calls.keys()))
            #print "unknown", message.toString()
            return
        if message.request and message.method.lower() != 'invite' and not call:
            self.app.debugMessage("SIP request refers to unknown call %s %r"%(
                                                    callid, self._calls.keys()))
            _d = defer.Deferred()
            callid = message.headers['call-id'][0]
            call = self._newCallObject(_d, callid = callid)
            _d.addCallbacks(lambda x: call.sendResponse(message, 481), log.err
                                                                ).addErrback(log.err)
            self._delCallObject(callid)
            # XXX In this case, send a 481!
            return
        if message.request:
            print "handling request", message.method
            if not call:
                # We must have received an INVITE here. Handle it, reply with
                # a 180 Ringing.
                callid = message.headers['call-id'][0]
                defsetup = defer.Deferred()
                call = self._newCallObject(defsetup, callid=callid)
                call.startInboundCall(message)
            else:
                if message.method == 'BYE':
                    # Aw. Other end goes away :-(
                    self.app.statusMessage("received BYE")
                    # Drop the call, send a 200.
                    call.recvBye(message)
                    self.app.endCall(call.cookie)
                    self._delCallObject(callid)
                elif message.method == 'INVITE':
                    # modify dialog
                    call.recvInvite(message)
                elif message.method == 'ACK':
                    call.recvAck(message)
                elif message.method == 'CANCEL':
                    call.recvCancel(message)

        elif message.response:
            print "handling response", message.code
            call.recvResponse(message)
