# Copyright (C) 2004 Anthony Baxter

'''SIP client code.'''

from interfaces import SIP as ISip

from twisted.internet.protocol import DatagramProtocol, ConnectedDatagramProtocol
from twisted.internet import defer
from twisted.internet import reactor
from twisted.protocols import sip as tpsip
from rtp import RTPProtocol

import shtoom

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

class Call(object):
    '''State machine for a phone call (inbound or outbound).'''

    cookie = _callID = uri = None
    sip = None
    _invite = None
    def __init__(self, phone, deferred, uri=None, callid=None):
        self.sip = phone
        self.compDef = deferred
        self._callID = None
        self.uri = None
        self.state = 'NEW'
        self._needSTUN = False
        self.cancel_trigger = None
        if uri:
            self.uri = uri
        if callid:
            self.setCallID(callid)
        self.cseq = random.randint(1000,5000)

    def setupLocalSIP(self, uri=None, via=None):
        ''' Setup SIP stuff at this end. Call with either a t.p.sip.URL
            (for outbound calls) or a t.p.sip.Via object (for inbound calls).

            returns a Deferred that will be triggered when the local SIP
            end is setup
        '''
        if not via:
            self.remote = uri
        else:
            self.remote = via
        self.setupDeferred = defer.Deferred()
        self.setLocalIP(dest=(self.remote.host, self.remote.port or 5060))
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

    def getTag(self):
        if not hasattr(self, '_tag'):
            self._tag = ('%04x'%(random.randint(0, 2**10)))[:4]
            self._tag += ('%04x'%(random.randint(0, 2**10)))[:4]
        return self._tag

    def setLocalIP(self, dest):
        """ Try and determine the local IP address to use. We use a
            ConnectedDatagramProtocol in the (faint?) hope that on a machine
            with multiple interfaces, we'll get the right one
        """
        # XXX Allow over-riding
        from shtoom.stun import StunHook, getPolicy
        host, port = dest
        getPref = self.sip.app.getPref
        if getPref('localip') is not None:
            self._localAddress = (getPref('localip'), getPref('localport') or 5060)
        else:
            # it is a hack!
            protocol = ConnectedDatagramProtocol()
            port = reactor.connectUDP(host, port, protocol)
            if protocol.transport:
                locAddress = (protocol.transport.getHost()[1], getPref('localport') or 5060)
                remAddress = protocol.transport.getPeer()[1:3]
                port.stopListening()
                log.msg("discovered local address %r, remote %r"%(locAddress,
                                                                  remAddress))
            else:
                self.compDef.errback(ValueError("couldn't connect to %s"%(
                                            host)))
                self.abortCall()
                return None
        if getPolicy().checkStun(locAddress[0], remAddress[0]):
            self._needSTUN = True
            log.msg("stun policy says yes, use STUN")
            deferred = defer.Deferred()
            deferred.addCallback(self.setStunnedLocalIP).addErrback(log.err)
            SH = StunHook(self.sip)
            deferred = SH.discoverStun(deferred)
        else:
            self._localIP, self._localPort = locAddress
            if not self._callID:
                self.setCallID()
            self.sip.updateCallObject(self, self.getCallID())
            self.setupDeferred.callback((host,port))

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
        return (self.remote.host, (self.remote.port or 5060))

    def acceptedCall(self, junk):
        self.sendResponse(self._invite, 200)
        self.setState('INVITE_OK')

    def rejectCall(self, message=None):
        ''' Accept currently pending call.
        '''
        from shtoom.exceptions import CallRejected
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
        #resp.addHeader('via', 'SIP/2.0/UDP %s:%s%s'%(
        #                            self.getLocalSIPAddress()+(branch,)))
        for via in vias:
            resp.addHeader('via', via)
        resp.addHeader('from', message.headers['from'][0])
        toaddr = message.headers['to'][0]
        toname,touri,toparams = tpsip.parseAddress(toaddr)
        if not toparams.has_key('tag'):
            toaddr = "%s;tag=%s"%(toaddr, self.getTag())
        resp.addHeader('to', toaddr)
        resp.addHeader('date', genStandardDate())
        resp.addHeader('call-id', message.headers['call-id'][0])
        resp.addHeader('server', 'Shtoom/%s'%shtoom.Version)
        resp.addHeader('cseq', message.headers['cseq'][0])
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
            self.sip.transport.write(resp.toString(), self.getRemoteSIPAddress())
            print "Response sent", resp.toString()
        except (socket.error, socket.gaierror):
            e,v,t = sys.exc_info()
            #self.compDef.errback(e(v))
            self.setState('ABORTED')

    def startOutboundCall(self, toAddr):
        uri = tpsip.parseURL(toAddr)
        d = self.setupLocalSIP(uri=uri)
        d.addCallback(lambda x:self.startSendInvite(toAddr, init=1)).addErrback(log.err)


    def startInboundCall(self, invite):
        via = tpsip.parseViaHeader(invite.headers['via'][0])
        d = self.setupLocalSIP(via=via)
        d.addCallback(lambda x:self.recvInvite(invite)).addErrback(log.err)
        if invite.headers.has_key('subject'):
            desc = invite.headers['subject'][0]
        else:
            name,uri,params =  tpsip.parseAddress(invite.headers['from'][0])
            desc = "From: %s %s" %(name,uri)
        self.cookie, defaccept = \
                    self.sip.app.acceptCall(self,
                                            calltype='inbound',
                                            desc=desc,
                                            fromIP=self.getRemoteSIPAddress()[0],
                                            withSTUN=self.getSTUNState() 
                                           )
        defaccept.addCallbacks(self.acceptedCall, self.rejectCall).addErrback(
                                                                        log.err)
        #self.app.incomingCall(subj, call, defaccept, defsetup)

    def recvInvite(self, invite):
        ''' Received an INVITE from another UA. If we're already on a
            call, it's an attempt to modify - send a 488 in this case.
        '''
        # XXX if self.getState() is not 'NEW', send a 488
        self._invite = invite
        contact = invite.headers['contact']
        if type(contact) is list:
            contact = contact[0]
        self.contact = contact
        self.uri = invite.headers['from'][0]
        self.sendResponse(invite, 180)
        if self.getState() != 'ABORTED':
            self.setState('SENT_RINGING')
        self.installTeardownTrigger()

    def startSendInvite(self, toAddr, init=0):
        print "startSendInvite", init
        if init:
            print "ok"
            cookie, d = self.sip.app.acceptCall(self,
                                            calltype='outbound', 
                                            fromIP=self.getLocalSIPAddress()[0],
                                            withSTUN=self.getSTUNState(),
                                                )
            self.cookie = cookie
            d.addCallback(lambda x:self.sendInvite(toAddr, init)).addErrback(log.err)
        else:
            self.sendInvite(toAddr, init=0)

    def sendInvite(self, toAddr, init=0):
        print "sendInvite"
        username = self.sip.app.getPref('username')
        email_address = self.sip.app.getPref('email_address')
        invite = tpsip.Request('INVITE', str(self.remote))
        # XXX refactor all the common headers and the like
        invite.addHeader('via', 'SIP/2.0/UDP %s:%s;rport'%
                                                self.getLocalSIPAddress())
        invite.addHeader('cseq', '%s INVITE'%self.getCSeq(incr=1))
        invite.addHeader('to', str(self.uri))
        invite.addHeader('content-type', 'application/sdp')
        invite.addHeader('from', '"%s" <sip:%s>;tag=%s'%(
                            username, email_address, 
                            self.getTag()))
        invite.addHeader('call-id', self.getCallID())
        invite.addHeader('subject', 'sip: %s'%(email_address))
        invite.addHeader('user-agent', 'Shtoom/%s'%shtoom.Version)
        lhost, lport = self.getLocalSIPAddress()
        invite.addHeader('contact', '"%s" <sip:%s:%s;transport=udp>'%(
                                username, lhost, lport))
        s = self.sip.app.getSDP(self.cookie)
        sdp = s.show()
        invite.addHeader('content-length', len(sdp))
        invite.bodyDataReceived(sdp)
        invite.creationFinished()
        try:
            self.sip.transport.write(invite.toString(), self.getRemoteSIPAddress())
            print "Invite sent", invite.toString()
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
        print "sending ACK"
        username = self.sip.app.getPref('username')
        email_address = self.sip.app.getPref('email_address')
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
        to = okmessage.headers['to']
        if type(to) is list:
            to = to[0]
        self.uri = self.extractURI(contact)
        uri = tpsip.parseURL(self.uri)

        # XXX Check the OK response's SDP, find what codec we
        # should be using

        ack = tpsip.Request('ACK', self.uri)
        # XXX refactor all the common headers and the like
        ack.addHeader('via', 'SIP/2.0/UDP %s:%s;rport'%self.getLocalSIPAddress())
        ack.addHeader('cseq', '%s ACK'%self.getCSeq())
        ack.addHeader('to', to)
        ack.addHeader('from', '"%s" <sip:%s>;tag=%s'%(
                            username, email_address, self.getTag()))
        ack.addHeader('call-id', self.getCallID())
        ack.addHeader('user-agent', 'Shtoom/%s'%shtoom.Version)
        ack.addHeader('content-length', 0)
        ack.creationFinished()
        if hasattr(self, 'compDef'):
            cb = self.compDef.callback
            del self.compDef
        else:
            cb = lambda *args: None
        print "sending ACK to %s %s"%(uri.host, uri.port or 5060)
        self.sip.transport.write(ack.toString(), (uri.host, (uri.port or 5060)))
        self.setState('CONNECTED')
        if startRTP:
            self.sip.app.startCall(self.cookie, (oksdp.ipaddr,oksdp.port), cb)

    def sendBye(self):
        username = self.sip.app.getPref('username')
        email_address = self.sip.app.getPref('email_address')
        dest = self.extractURI(self.contact)
        uri = tpsip.parseURL(dest)
        bye = tpsip.Request('BYE', dest)
        # XXX refactor all the common headers and the like
        bye.addHeader('via', 'SIP/2.0/UDP %s:%s;rport'%self.getLocalSIPAddress())
        bye.addHeader('cseq', '%s BYE'%self.getCSeq(incr=1))
        bye.addHeader('to', self.uri)
        bye.addHeader('from', '"%s" <sip:%s>;tag=%s'%(
                            username, email_address, self.getTag()))
        bye.addHeader('call-id', self.getCallID())
        bye.addHeader('user-agent', 'Shtoom/%s'%shtoom.Version)
        bye.addHeader('content-length', 0)
        bye.creationFinished()
        bye, dest = bye.toString(), (uri.host, (uri.port or 5060))
        self.sip.transport.write(bye, dest)
        self.setState('SENT_BYE')

    def sendCancel(self):
        """ Sends a CANCEL message to kill a call that's in the process of
            being established
        """
        raise NotImplementedError

    def recvBye(self, message):
        ''' An in-progress call got a BYE from the other end. Hang up
            call, send a 200.
        '''
        self.sendResponse(message, 200)

    def recvCancel(self, message):
        """ The remote UAC changed it's mind about the new call and
            gave up.
        """

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
        if state == 'NONE':
            self.sip.app.debugMessage("no call to drop")
        elif state in ( 'CONNECTED', ):
            self.sendBye()
            self.setState('SENT_BYE')
        elif state in ( 'SENT_INVITE', ):
            self.sendCancel()
            self.setState('SENT_CANCEL')

    def calcAuth(self, authhdr):
        from urllib2 import parse_http_list
        import digestauth
        method, auth = authhdr.split(' ', 1)
        if method.lower() != 'digest':
            raise ValueError, "Unknown auth method %s"%(method)
        chal = digestauth.parse_keqv_list(parse_http_list(auth))
        print chal
        qop = chal.get('qop')
        if not qop:
            # Bogus Quotient bug.
            qop = chal.get('qop-options')
        if not qop:
            qop = 'auth'
        if qop.lower() != 'auth':
            raise ValueError, "can't handle qop '%s'"%(qop)
        realm = chal.get('realm')
        algorithm = chal.get('algorithm', 'md5')
        nonce = chal.get('nonce')
        opaque = chal.get('opaque')
        H, KD = self._getHashingImplementation(algorithm)
        user = self.sip.app.getPref('register_authuser')
        passwd = self.sip.app.getPref('register_authpasswd')
        if user is None or passwd is None:
            raise RuntimeError, "Auth required"
        A1 = '%s:%s:%s'%(user, chal['realm'], passwd)
        A2 = 'REGISTER:%s'%str(self.regServer)
        self.nonce_count += 1
        ncvalue = '%08x'%(self.nonce_count)
        cnonce = digestauth.generate_nonce(bits=16,
                                           randomness=
                                              str(nonce)+str(self.nonce_count))
        # XXX nonce isn't there for proxy-auth. :-(
        noncebit =  "%s:%s:%s:%s:%s" % (nonce,ncvalue,cnonce,qop,H(A2))
        respdig = KD(H(A1), noncebit)
        base = '%s username="%s", realm="%s", nonce="%s", uri="%s", ' \
               'response="%s"' % (method, user, realm, nonce, 
                                  str(self.regServer), respdig)
        if opaque:
            base = base + ', opaque="%s"' % opaque
        if algorithm != 'MD5':
            base = base + ', algorithm="%s"' % algorithm
        if qop:
            base = base + ', qop=auth, nc=%s, cnonce="%s"'%(ncvalue, cnonce)
        return base

    def recvResponse(self, message):
        state = self.getState()
        print "Handling %s while in state %s"%(message.code, state)
        if message.code in ( 100, 180, 181, 182 ):
            return
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
                self.sip.app.statusMessage("idle")
            else:
                self.sip.app.debugMessage('Got OK in unexpected state %s'%state)
        elif message.code - (message.code%100) == 400:
            # XXX Auth failure (401)
            self.sip.app.debugMessage(message.toString())
            self.sip.app.endCall(self.cookie, 'Other end sent %s'%message.toString())
            self.sip._delCallObject(self.getCallID())
        elif message.code - (message.code%100) == 500:
            self.sip.app.debugMessage(message.toString())
            self.sip.app.endCall(self.cookie, 'Other end sent %s'%message.toString())
            self.sip._delCallObject(self.getCallID())
        elif message.code - (message.code%100) == 600:
            self.sip.app.debugMessage(message.toString())
            self.sip.app.endCall(self.cookie, 'Other end sent %s'%message.toString())
            self.sip._delCallObject(self.getCallID())
        else:
            self.sip.app.debugMessage(message.toString())

class Registration(Call):
    "State machine for registering with a server."

    def __init__(self, phone, deferred):
        self.sip = phone
        self.compDef = deferred
        self.regServer = None
        self.regAOR = None
        self.authCred = None
        self.state = 'NEW'
        self._needSTUN = False
        self.cseq = random.randint(1000,5000)
        self.nonce_count = 0
        self.cancel_trigger = None
        self.register_attempts = 0

    def startRegistration(self):
        import copy
        self.regServer = tpsip.parseURL(self.sip.app.getPref('register_uri'))
        self.regAOR = copy.copy(self.regServer)
        self.regAOR.username = self.sip.app.getPref('username')
        d = self.setupLocalSIP(self.regServer)
        d.addCallback(self.sendRegistration).addErrback(log.err)

    def sendRegistration(self, cb=None, auth=None, authhdr=None):
        username = self.sip.app.getPref('username')
        invite = tpsip.Request('REGISTER', str(self.regServer))
        # XXX refactor all the common headers and the like
        invite.addHeader('via', 'SIP/2.0/UDP %s:%s;rport'%
                                                self.getLocalSIPAddress())
        invite.addHeader('cseq', '%s REGISTER'%self.getCSeq(incr=1))
        invite.addHeader('to', '"anthony baxter" <%s>'%(str(self.regAOR)))
        invite.addHeader('from', '"anthony baxter" <%s>'%(str(self.regAOR)))
        state =  self.getState() 
        if state in ( 'NEW', 'SENT_REGISTER', 'REGISTERED' ):
            invite.addHeader('expires', 900)
        elif state in ( 'CANCEL_REGISTER' ):
            invite.addHeader('expires', 0)
        #invite.addHeader('event', 'registration')
        #invite.addHeader('allow-events', 'presence')
        invite.addHeader('call-id', self.getCallID())
        if auth is not None:
            invite.addHeader(authhdr, auth)
        invite.addHeader('user-agent', 'Shtoom/%s'%shtoom.Version)
        lhost, lport = self.getLocalSIPAddress()
        invite.addHeader('contact', '<sip:%s@%s:%s>'%(
                                username, lhost, lport))
        invite.addHeader('content-length', '0')
        invite.creationFinished()
        try:
            self.sip.transport.write(invite.toString(), self.getRemoteSIPAddress())
            print "register sent", invite.toString()
        except (socket.error, socket.gaierror):
            e,v,t = sys.exc_info()
            self.compDef.errback(e(v))
            self.setState('ABORTED')
        else:
            if self.getState() in ( 'NEW', 'REGISTERED' ):
                self.setState('SENT_REGISTER')

    def recvResponse(self, message):
        state = self.getState()
        if message.code in ( 401, ):
            self.register_attempts += 1
            if self.register_attempts > 5:
                print "REGISTRATION FAILED"
                self.setState('FAILED')
                return
            if state in ( 'SENT_REGISTER', 'CANCEL_REGISTER' ):
                a = message.headers.get('www-authenticate')
                if a:
                    auth = self.calcAuth(a[0])
                    self.sendRegistration(auth=auth, authhdr='authorization')
                else:
                    # We got bounced and told to bugger off.
                    print "401, no further possible actions"
            else:
                print "Unknown state '%s' for a 401"%(state)
        elif message.code in ( 407, ):
            self.register_attempts += 1
            if self.register_attempts > 5:
                print "REGISTRATION FAILED"
                self.setState('FAILED')
                return
            # XXX todo handle proxy-auth
            if state in ( 'SENT_REGISTER', 'CANCEL_REGISTER' ):
                auth = self.calcAuth(message.headers['proxy-authenticate'][0])
                self.sendRegistration(auth=auth, authhdr='proxy-authorization')
            else:
                print "Unknown state '%s' for a 401"%(state)
        elif message.code in ( 200, ):
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
                d.callback('ok')
            else:
                print "Unknown state '%s' for a 200"%(state)
        elif message.code in ( 100, ):
            # Trying?!?
            print "TODO: 'Trying' from register??!"
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


class SipPhone(DatagramProtocol, object):
    '''A SIP phone.'''

    __implements__ = ISip,

    def __init__(self, app, *args, **kwargs):
        self.app = app
        self._calls = {}
        super(SipPhone, self, *args, **kwargs)

    def register(self):
        if self.app.getPref('register_uri') is not None:
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
        call = self._newCallObject(_d, to=uri)
        if call is None:
            return '', _d
        invite = call.startOutboundCall(uri)
        # Set up a callLater in case we don't get a response, for a retransmit
        # Set up a timeout for the call completion
        return _d


    def startDTMF(self, digit):
        """Start sending DTMF digit 'digit'
        """
        self.app.debugMessage("startDTMF not implemented yet!")

    def stopDTMF(self):
        """Stop sending DTMF digit 'digit'
        """
        self.app.debugMessage("stopDTMF not implemented yet!")

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
            return
        if message.request and message.method.lower() != 'invite' and not call:
            self.app.debugMessage("SIP request refers to unknown call %s %r"%(
                                                    callid, self._calls.keys()))
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


        elif message.response:
            print "handling response", message.code
            call.recvResponse(message)

