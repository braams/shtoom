# Copyright (C) 2004 Anthony Baxter

'''SIP client code.'''

# A Note For The Reader: This code in this module is _hairy_. It's also
# ugly, a mess and sorely in need of redesign and refactoring. Do _not_
# try and use this to learn Python, or Twisted. Doing so _will_ void the
# warranty on your brain.

# And yes, a redesign (to make it unit testable, for one thing) is very
# much planned and it is gradually being refactored.

import copy, digestauth, md5, random, sha, socket, sys, time
from urllib2 import parse_http_list

from interfaces import SIP as ISip

from twisted.internet.protocol import DatagramProtocol, ConnectedDatagramProtocol
from twisted.internet import defer
from twisted.protocols import sip as tpsip
from twisted.python import log

from shtoom.exceptions import CallRejected, CallFailed, HostNotKnown
from shtoom import __version__ as ShtoomVersion
from shtoom.sdp import SDP

import struct, email.Parser

_CACHED_LOCAL_IP = None


def buildSDP(message):
    # Takes a message, constructs an SDP object. Has to deal with 
    # multipart/mixed and the like. Dear gods I hate cisco.
    if (message.headers.get('content-type') and 
            message.headers['content-type'][0].lower() != 'application/sdp'):
        parser = email.Parser.Parser()
        # strip the header line. rock on :-(
        txt = '\n'.join(message.toString().split('\n')[1:])
        m = parser.parsestr(txt)
        if not m.is_multipart():
            parts = [m.get_payload(),]
        else:
            parts = m.get_payload()
        # In _theory_ you could have nested multipart/mixeds, but really, who
        # would be that crackful? 
        for part in parts:
            if part['content-type'].lower() == 'application/sdp':
                sdp = SDP(part.get_payload())
                print "returning sdp object", sdp
                return sdp
        raise ValueError("couldn't find application/sdp in message!")
    else:
        sdp = SDP(message.body)
        return sdp



def errhandler(*args):
    print "BANG", args

def genCallId():
    return 400000000 + random.randint(0,2000000)

def genStandardDate(t=None):
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

VIA_COOKIE = "z9hG4bK"

def computeBranch(msg):
    """Create a branch tag to uniquely identify this message.  See
    RFC3261 sections 8.1.1.7 and 16.6.8."""
    if msg.headers.has_key('via') and msg.headers['via']:
        oldvia = msg.headers['via'][0]
    else:
        oldvia = ''
    return (VIA_COOKIE + 
            md5.new(
                    (tpsip.parseAddress(msg.headers['to'][0])[2].get('tag','') 
                     +
                     tpsip.parseAddress(msg.headers['from'][0])[2].get('tag','')
                     +
                     msg.headers['call-id'][0] 
                     +
                     msg.uri.toString() 
                     +
                     oldvia  
                     +
                     msg.headers['cseq'][0].split(' ')[0]
                    )
            ).hexdigest())


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
        if parsed:
            return self._uri
        else:
            return str(self._uri)

    def getParams(self): return self._params

    def __str__(self):
        return formatAddress((self._display, self._uri, self._params))

def _is_ip(hostname):
    nums = hostname.split('.')
    if len(nums) != 4:
        return False
    try:
        nums = map(int, nums)
    except ValueError:
        return False
    for num in nums:
        if num < 0 or num > 255:
            return False
    return True

def _hostportToIPPort(hostport):
    host, port = hostport
    if _is_ip(host):
        return hostport
    else:
        # if it doesn't resolve, just explode.
        return socket.gethostbyname(host), port

class Dialog:
    _contact = None

    def __init__(self, callid=None, caller=None, callee=None):
        self._callid = callid
        self._caller = caller
        self._callee = callee
        self._cseq = random.randint(1000,5000)
        self._direction = None

    def setDirection(self, inbound=False, outbound=False):
        if inbound:
            self._direction = 'inbound'
        elif outbound:
            self._direction = 'outbound'
        else:
            raise ValueError, "must be either inbound or outbound"

    def getDirection(self):
        return self._direction

    def getLocalTag(self):
        if self._direction == 'inbound':
            return self.getCallee()
        elif self._direction == 'outbound':
            return self.getCaller()
        else:
            raise ValueError, "direction be either inbound or outbound"

    def getRemoteTag(self):
        if self._direction == 'inbound':
            return self.getCaller()
        elif self._direction == 'outbound':
            return self.getCallee()
        else:
            raise ValueError, "direction be either inbound or outbound"

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
            callid = genCallId()
        self._callid = callid

    def setContact(self, username, ip, port):
        self._contact = tpsip.URL(ip, username=username, port=port)

    def getContact(self):
        return self._contact

    def getCaller(self):
        return self._caller

    def getCallee(self):
        return self._callee

    def getCallID(self):
        return self._callid

    def getCSeq(self, incr=0):
        if incr:
            self._cseq += 1
        return self._cseq

    def formatResponse(self, message, code, body, bodyCT='application/sdp'):
        resp = tpsip.Response(code)
        vias = message.headers['via']
        for via in vias:
            resp.addHeader('via', via)
        # XXX copy Record-Route headers
        if not self.getCallee():
            addr = message.headers['to'][0]
            self.setCallee(Address(addr, ensureTag=True))
        if not self.getCaller():
            addr = message.headers['from'][0]
            self.setCaller(Address(addr))
        #resp.addHeader('to', str(self.getCallee()))
        #resp.addHeader('from', str(self.getCaller()))
        resp.addHeader('to', message.headers['to'][0])
        resp.addHeader('from', message.headers['from'][0])
        resp.addHeader('date', genStandardDate())
        resp.addHeader('call-id', message.headers['call-id'][0])
        resp.addHeader('server', 'Shtoom/%s'%ShtoomVersion)
        resp.addHeader('cseq', message.headers['cseq'][0])
        resp.addHeader('allow-events', 'telephone-event')
        if message.method == 'INVITE' and code == 200:
            resp.addHeader('contact', str(self.getContact()))
            # We include SDP here
            resp.addHeader('content-length', len(body))
            resp.addHeader('content-type', bodyCT)
            resp.bodyDataReceived(body)
        else:
            resp.addHeader('content-length', 0)
        resp.creationFinished()
        return resp.toString()

    def __repr__(self):
        return "<Dialog %s->%s, %s>"%(self.getCaller(),self.getCallee(),self.getCallID())


class Call(object):
    '''State machine for a phone call (inbound or outbound).'''

    cookie = uri = None
    nonce_count = 1
    sip = None
    _invite = None
    def __init__(self, phone, uri=None, callid=None):
        self.sip = phone
        self.auth_attempts = 0
        self._remoteURI = None
        self._remoteAOR = None
        self._localAOR = None
        self._outboundProxyURI = None
        self.dialog = Dialog()
        self.state = 'NEW'
        self._needSTUN = False
        self.cancel_trigger = None
        if callid:
            self.setCallID(callid)

    def callStart(self):
        self.compDef = defer.Deferred()
        return self.compDef

    def setupLocalSIP(self, uri=None, via=None):
        ''' Setup SIP stuff at this end. Call with either a t.p.sip.URL
            (for outbound calls) or a t.p.sip.Via object (for inbound calls).

            returns a Deferred that will be triggered when the local SIP
            end is setup
        '''
        self.setupDeferred = defer.Deferred()
        outboundProxyURI = self.sip.app.getPref('outbound_proxy_url')
        if outboundProxyURI:
            log.msg('using outboundProxyURI of %s'%(outboundProxyURI,),system="sip")
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
            self.dialog.setCallID(callid)
        else:
            self.dialog.setCallID('%s@%s'%(genCallId(), self.getLocalSIPAddress()[0]))

    def setState(self, state):
        self.state = state

    def getState(self):
        return self.state

    def getSTUNState(self):
        return self._needSTUN


    def setLocalIP(self, dest):
        from twisted.internet import reactor
        from shtoom.nat import getLocalIPAddress
        global _CACHED_LOCAL_IP
        host, port = dest
        getPref = self.sip.app.getPref
        lport = self.sip.transport.getHost().port
        if getPref('localip') is not None or _CACHED_LOCAL_IP is not None:
            ip = getPref('localip') or _CACHED_LOCAL_IP
            locAddress = (ip, lport)
            remAddress = ( host, port )
            self._checkNATPolicy(locAddress, remAddress)
            # Argh. Do a DNS lookup on remAddress
        else:
            d = getLocalIPAddress()
            d.addCallback(lambda lhost, lport=lport, dest=dest:
                                self._checkNATPolicy((lhost,lport), dest)
                         )

    def _checkNATPolicy(self, locAddress, remAddress):
        from shtoom.nat import getPolicy, getMapper
        pol = getPolicy()
        useNAT = pol.checkStun(locAddress[0], remAddress[0])
        if useNAT is True:
            self._needSTUN = True
            log.msg("NAT policy says yes, we're transitting a NAT",system='sip')
            getMapper().addCallback(self._cb_getMappedAddress
                                                    ).addErrback(log.err)
        elif useNAT is False:
            self._localIP, self._localPort = locAddress
            if not self.dialog.getCallID():
                self.setCallID()
            self.sip.updateCallObject(self, self.getCallID())
            self.setupDeferred.callback((self._localIP, self._localPort))
        else:
            print "STUN policy %r failed for %r %r"%(pol, locAddress[0], remAddress[0])
            # None. STUN stuff failed. Abort.
            d = self.compDef
            del self.compDef
            d.errback(HostNotKnown)
            self.setState('ABORTED')

    def _cb_getMappedAddress(self, mapper):
        deferred = mapper.map(self.sip.transport)
        deferred.addCallback(self.setStunnedAddress).addErrback(log.err)

    def setStunnedAddress(self, address):
        if address:
            host,port = address
        else:
            host,port = '',''
        log.msg("after NAT mapping,external address is %s:%s"%(host, port), system='sip')
        self.sip.app.notifyEvent('discoveredStunnedIP', host, port)
        self._localIP = host
        self._localPort = port
        # XXX Check for multiple firings!
        if not self.dialog.getCallID():
            self.setCallID()
            self.sip.updateCallObject(self, self.getCallID())
        self.setupDeferred.callback((host,port))

    def getCallID(self):
        return self.dialog.getCallID()

    def getLocalSIPAddress(self):
        return (self._localIP, self._localPort or 5060)

    def getRemoteSIPAddress(self):
        if self._outboundProxyURI is not None:
            return (self._outboundProxyURI.host, (self._outboundProxyURI.port or 5060))
        elif self._remoteURI is not None:
            return (self._remoteURI.host, (self._remoteURI.port or 5060))
        else:
            return (self._remoteAOR.host, (self._remoteAOR.port or 5060))

    def getLocalAOR(self, full=False, addr=None):
        if addr is not None:
            self._localFullAOR = Address(addr, ensureTag=True)
            self._localAOR = self._localFullAOR.getURI(parsed=True)
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

    def _cb_incomingCall(self, response):
        from shtoom.exceptions import CallFailed
        if isinstance(response, CallFailed):
            return self.rejectedIncoming(response)
        else:
            assert isinstance(response, basestring)
            return self.acceptedIncoming(response)

    def acceptedIncoming(self, cookie):
        assert isinstance(cookie, basestring)
        log.msg("acceptIncoming setting cookie to %r"%(cookie), system='sip')
        self.cookie = cookie
        lhost, lport = self.getLocalSIPAddress()
        username = self.sip.app.getPref('username')
        self.dialog.setContact(username, lhost, lport)

        othersdp = buildSDP(self._invite)
        sdp = self.sip.app.getSDP(self.cookie, othersdp)
        if not sdp.hasMediaDescriptions():
            self.sendResponse(self._invite, 406)
            self.setState('ABORTED')
            return
        body = sdp.show()

        self.sendResponse(self._invite, 200, body)
        self.setState('INVITE_OK')

    def rejectedIncoming(self, response):
        ''' Reject currently pending call.
        '''
        log.msg("rejecting because %r"%(response,), system='sip')
        if hasattr(response, 'sipCode'):
            code = response.sipCode
        else:
            code = 603
        self.sendResponse(self._invite, code)
        self.setState('ABORTED')
        self.compDef.errback(response)

    def failedIncoming(self, failure):
        log.msg('failedIncoming because %r'%(failure,), system='sip')
        log.msg('exception: %r'%(failure.value.args,), system='sip')
        # XXX Can I produce a more specific error than 500?
        self.sendResponse(self._invite, 500)
        self.setState('ABORTED')
        self.compDef.errback(failure)

    def terminateCall(self, message):
        if self.getState() == 'SENT_INVITE':
            d, self.compDef = self.compDef, None
            if d is not None:
                if (message.code - (message.code % 100)) in ( 400, 500 ):
                    exc = CallFailed
                elif  (message.code - (message.code % 100)) == 600:
                    exc = CallRejected
                else:
                    exc = CallFailed
                print "call terminated on a", message.code
                log.msg("call terminated on a %s"%message.code, system="sip")
                d.errback(exc('%s: %s'%(message.code, message.phrase)))
        self.sip.app.endCall(self.cookie,
                             'other end sent\n%s'%message.toString())


    def sendResponse(self, message, code, body=None):
        ''' Send a response to a message. message is the response body,
            code is the response code (e.g.  200 for OK)
        '''
        resp = self.dialog.formatResponse(message, code, body)

        vias = message.headers['via']
        try:
            via0 = tpsip.parseViaHeader(vias[0])
            viaAddress = (via0.host.strip(), via0.port)
            self.sip.transport.write(resp, _hostportToIPPort(viaAddress))
            self.sip.app.debugMessage("Response sent to %r\n%s"%(viaAddress,resp))
        except (socket.error, socket.gaierror):
            e,v,t = sys.exc_info()
            #self.compDef.errback(e(v))
            self.setState('ABORTED')

    def startOutboundCall(self, toAddr, fromAddr=None):
        # XXX Set up a callLater in case we don't get a response, for a
        # retransmit
        # XXX Set up a timeout for the call completion
        uri = tpsip.parseURL(toAddr)
        self._remoteAOR = uri
        # XXX Display name? needs an option
        self.dialog.setDirection(outbound=True)
        self.dialog.setCallee(Address(uri, ensureTag=False))
        self.dialog.setCaller(self.getLocalAOR(addr=fromAddr, full=True))
        d = self.setupLocalSIP(uri=uri)
        d.addCallback(lambda x:self.startSendInvite(toAddr, init=1)
                                                        ).addErrback(log.err)

    def startInboundCall(self, invite):
        "help me. this is awful"
        via = tpsip.parseViaHeader(invite.headers['via'][0])
        if via.host.startswith(' '):
            via.host = via.host.strip()
        d = self.setupLocalSIP(via=via)
        contact = invite.headers['contact']
        if type(contact) is list:
            contact = contact[0]
        self.contact = contact
        self.dialog.setDirection(inbound=True)
        self.dialog.setCaller(Address(invite.headers['from'][0]))
        self.dialog.setCallee(Address(invite.headers['to'][0], ensureTag=True))
        if invite.headers.get('record-route'):
            rr = invite.headers['record-route']
            if type(rr) is list: rr = rr[0]
            self._remoteURI = Address(self.extractURI(rr)).getURI(parsed=True)
        else:
            self._remoteURI = Address(self.extractURI(contact)
                                                ).getURI(parsed=True)
        self._remoteAOR = self.dialog.getCaller().getURI()
        d.addCallback(lambda x:self.recvInvite(invite)).addErrback(log.err)
        if invite.headers.has_key('subject'):
            desc = invite.headers['subject'][0]
        else:
            name,uri,params =  tpsip.parseAddress(invite.headers['from'][0])
            desc = "From: %s %s" %(name,uri)
        d.addCallback(lambda x: self.sip.app.acceptCall(call=self))
        d.addCallbacks(self._cb_incomingCall, self.failedIncoming)
        d.addErrback(log.err)
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
        #print "startSendInvite", init
        if init:
            d = self.sip.app.acceptCall(call=self)
            d.addCallback(lambda x:self.sendInvite(toAddr, cookie=x, init=init)
                                                        ).addErrback(log.err)
        else:
            self.sendInvite(toAddr, init=0)


    def addViaHeader(self, msg):
        # Add the initial Via header. 
        nathost, natport = self.getLocalSIPAddress()
        msg.addHeader('via', tpsip.Via(nathost, natport, 
                                       rport=True, 
                                       branch=computeBranch(msg)
                                                               ).toString()
                     )
        
        
    def sendInvite(self, toAddr, cookie=None, auth=None, authhdr=None, init=0):
        if cookie:
            assert isinstance(cookie, basestring)
            print "sendinvite setting cookie to", cookie
            self.cookie = cookie
        lhost, lport = self.getLocalSIPAddress()
        username = self.sip.app.getPref('username')
        self.dialog.setContact(username, lhost, lport)
        if self.getState() == "ABORTED":
            d = self.compDef
            del self.compDef
            d.callback('call aborted')
            return
        invite = tpsip.Request('INVITE', str(self._remoteAOR))
        # XXX refactor all the common headers and the like
        invite.addHeader('cseq', '%s INVITE'%self.dialog.getCSeq(incr=1))
        invite.addHeader('to', str(self.dialog.getCallee()))
        invite.addHeader('content-type', 'application/sdp')
        invite.addHeader('from', str(self.dialog.getCaller()))
        invite.addHeader('call-id', self.getCallID())
        invite.addHeader('subject', str(self.getLocalAOR()))
        invite.addHeader('allow-events', 'telephone-event')
        invite.addHeader('user-agent', 'Shtoom/%s'%ShtoomVersion)
        if auth is not None:
            #print auth, authhdr
            invite.addHeader(authhdr, auth)
        invite.addHeader('contact', str(self.dialog.getContact()))
        s = self.sip.app.getSDP(self.cookie)
        sdp = s.show()
        invite.addHeader('content-length', len(sdp))
        invite.bodyDataReceived(sdp)
        invite.creationFinished()
        self.addViaHeader(invite)
        self._remoteAOR = self.dialog.getCallee().getURI()
        try:
            log.msg('Sending INVITE to %r:\n%s'%(_hostportToIPPort(self.getRemoteSIPAddress()), invite.toString()), system='sip')
            self.sip.transport.write(invite.toString(), _hostportToIPPort(self.getRemoteSIPAddress()))
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
        username = self.sip.app.getPref('username')
        if okmessage.code == 200:
            oksdp = buildSDP(okmessage)
            print "oksdp", oksdp
            sdp = self.sip.app.getSDP(self.cookie, oksdp)
            if not sdp.hasMediaDescriptions():
                # Bollocks. Can't 488 a response!
                self.sendResponse(okmessage, 488)
                self.setState('ABORTED')
                log.msg("call failed, no suitable media", system='sip')
                if self.compDef is not None:
                    cb, self.compDef = self.compDef.errback, None
                    e = CallFailed('Call failed: no suitable media')
                    e.sipCode = 488
                    cb(e)
                    return
        elif okmessage.code == 407:
            log.msg("sending Ack for a 407", system='sip') 
        else:
            self.setState('ABORTED')
            log.msg("call failed with %s"%(okmessage.code), system='sip')
            if self.compDef is not None:
                cb, self.compDef = self.compDef.errback, None
                e = CallFailed('Call failed: %s'%(okmessage.code))
                e.sipCode = okmessage.code
                cb(e)
                return
        via = okmessage.headers.get('via')
        if type(via) is list: via = via[0]
        via = tpsip.parseViaHeader(via)
        if via.rport and via.rport != True:
            print "correcting local port to %r"%(via.rport)
            self._localPort = int(via.rport)
        if 'contact' in okmessage.headers:
            contact = okmessage.headers['contact']
        else:
            contact = okmessage.headers['to']
        if type(contact) is list:
            contact = contact[0]
        self.contact = contact
        # If there's a record-route header, we need to send to the specified
        # host, not the contact.
        if okmessage.headers.get('record-route'):
            rr = okmessage.headers['record-route']
            if type(rr) is list: rr = rr[0]
            self._remoteURI = Address(self.extractURI(rr)).getURI(parsed=True)
            print "using record-route header of", self._remoteURI
            ackdest = self._remoteURI.host, self._remoteURI.port or 5060
        elif 'contact' in okmessage.headers:
            self._remoteURI = Address(self.extractURI(contact)
                                                ).getURI(parsed=True)
            ackdest = self._remoteURI.host, self._remoteURI.port or 5060
        elif via:
            ackdest = via.host, via.port or 5060
        else:
            self._remoteURI = Address(self.extractURI(contact)
                                                ).getURI(parsed=True)
            ackdest = self._remoteURI.host, self._remoteURI.port or 5060

        self.dialog.setCallee(Address(okmessage.headers['to'][0]))
        ack = tpsip.Request('ACK', str(self._remoteAOR))
        # XXX refactor all the common headers and the like
        ack.addHeader('cseq', '%s ACK'%self.dialog.getCSeq())
        ack.addHeader('to', str(self.dialog.getCallee()))
        ack.addHeader('from', str(self.dialog.getCaller()))
        ack.addHeader('call-id', self.getCallID())
        ack.addHeader('allow-events', 'telephone-event')
        ack.addHeader('user-agent', 'Shtoom/%s'%ShtoomVersion)
        ack.addHeader('content-length', 0)
        ack.creationFinished()
        self.addViaHeader(ack)
        if hasattr(self, 'compDef') and self.compDef is not None \
                                                and okmessage.code == 200:
            cb = self.compDef.callback
            del self.compDef
        else:
            cb = lambda *args: None
        log.msg("sending ACK to %s %s"% _hostportToIPPort(ackdest), system='sip')
        if self.getState() != 'ABORTED' and okmessage.code == 200:
            self.setState('CONNECTED')
            if startRTP:
                self.sip.app.startCall(self.cookie, oksdp, cb)
            self.sip.app.statusMessage("Call Connected")
        self.sip.transport.write(ack.toString(), _hostportToIPPort(ackdest))
        log.msg("sending ACK to %r\n%s"%(ackdest, ack.toString()), system="sip")

    def sendBye(self, toAddr="ignored", auth=None, authhdr=None):
        username = self.sip.app.getPref('username')
        uri = self._remoteURI
        dest = uri.host, (uri.port or 5060)
        bye = tpsip.Request('BYE', str(self._remoteAOR))
        # XXX refactor all the common headers and the like
        bye.addHeader('cseq', '%s BYE'%self.dialog.getCSeq(incr=1))
        bye.addHeader('from', str(self.dialog.getLocalTag()))
        bye.addHeader('to', str(self.dialog.getRemoteTag()))
        bye.addHeader('call-id', self.getCallID())
        bye.addHeader('user-agent', 'Shtoom/%s'%ShtoomVersion)
        bye.addHeader('content-length', 0)
        if auth:
            bye.addHeader(authhdr, auth)
        bye.creationFinished()
        self.addViaHeader(bye)
        bye = bye.toString()
        log.msg("sending BYE to %r\n%s"%(dest, bye), system="sip")
        self.sip.transport.write(bye, _hostportToIPPort(dest))
        #for i in range(5):
        #    super-klooge: send five copies of this because it is unreliable
        #    self.sip.transport.write(bye, dest)
        self.setState('SENT_BYE')

    def sendCancel(self):
        """ Sends a CANCEL message to kill a call that's not yet seen a
            non-provisional response (i.e. a 1xx, but not a 2xx).
        """
        username = self.sip.app.getPref('username')
        uri = self._remoteAOR
        dest = uri.host, (uri.port or 5060)
        cancel = tpsip.Request('CANCEL', str(self._remoteAOR))
        # XXX refactor all the common headers and the like
        cancel.addHeader('via', 'SIP/2.0/UDP %s:%s'%self.getLocalSIPAddress())
        cancel.addHeader('cseq', '%s CANCEL'%self.dialog.getCSeq())
        cancel.addHeader('to', str(self.dialog.getCallee()))
        cancel.addHeader('from', str(self.dialog.getCaller()))
        cancel.addHeader('call-id', self.getCallID())
        cancel.addHeader('user-agent', 'Shtoom/%s'%ShtoomVersion)
        cancel.addHeader('content-length', 0)
        cancel.creationFinished()
        self.addViaHeader(cancel)
        cancel = cancel.toString()
        log.msg("sending CANCEL to %r\n%s"%(dest, cancel), system="sip")
        self.sip.transport.write(cancel, _hostportToIPPort(dest))
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
        sdp = SDP(self._invite.body)
        self.setState('CONNECTED')
        if hasattr(self, 'compDef'):
            d, self.compDef = self.compDef, None
            self.sip.app.startCall(self.cookie, sdp,
                                   d.callback)

    def recvOptions(self, message):
        """ Received an OPTIONS request from a remote UA.
            Put together a 200 response if we're ok with the Require headers,
            otherwise an error (XXXXX)
        """

    def installTeardownTrigger(self):
        from twisted.internet import reactor
        if 0 and self.cancel_trigger is None:
            t = reactor.addSystemEventTrigger('before',
                                              'shutdown',
                                              self.dropCall,
                                              appTeardown=True)
            self.cancel_trigger = t

    def dropCall(self, appTeardown=False):
        '''Drop call '''
        from twisted.internet import reactor
        # XXX return a deferred, and handle responses properly
        if not appTeardown and self.cancel_trigger is not None:
            reactor.removeSystemEventTrigger(self.cancel_trigger)
        state = self.getState()
        log.msg("dropcall in state %r"%state, system="sip")
        if state == 'NONE':
            self.sip.app.debugMessage("no call to drop")
            return defer.succeed('no call to drop')
        elif state in ( 'CONNECTED', ):
            self.sendBye()
            self.dropDef = defer.Deferred()
            return self.dropDef
            # XXX callLater to give up...
        elif state in ( 'SENT_INVITE', ):
            self.sendCancel()
            self.setState('SENT_CANCEL')
            return defer.succeed('cancelled')
            # XXX callLater to give up...
        elif state in ( 'NEW', ):
            self.setState('ABORTED')
            return defer.succeed('aborted')

    def _getHashingImplementation(self, algorithm):
        if algorithm.lower() == 'md5':
            H = lambda x: md5.new(x).hexdigest()
        elif algorithm.lower() == 'sha':
            H = lambda x: sha.new(x).hexdigest()
        # XXX MD5-sess
        KD = lambda s, d, H=H: H("%s:%s" % (s, d))
        return H, KD

    def calcAuth(self, method, uri, authchal, cred):
        if not cred:
            raise RuntimeError, "Auth required, but not provided?"
        (user, passwd) = cred
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
        print "auth", A1, H(A1), respdig
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
        log.msg("Handling %s while in state %s"%(message.code, state), system="sip")
        if message.code == 180:
            self.sip.app.ringBack()
        elif message.code in ( 100, 181, 182 ):
            return
        elif message.code == 183:
            # Many things are 183. For instance, ciscos with GTD enabled 
            # send multipart/mixed with an application/gtd part to pass on
            # ISDN signalling information. XXX handle some of the fascinating
            # variants at some point.
            self.sip.app.debugMessage('Should handle early media here:\n' + message.toString())
        elif message.code == 200:
            self.auth_attempts = 0
            if state == 'SENT_INVITE':
                self.sip.app.debugMessage("Got Response 200\n")
                self.sendAck(message, startRTP=1)
            elif state == 'CONNECTED':
                self.sip.app.debugMessage('Got duplicate OK to our ACK')
                #self.sendAck(message)
            elif state == 'SENT_BYE':
                self.sip.app.endCall(self.cookie)
                self.sip._delCallObject(self.getCallID())
                self.sip.app.debugMessage("Hung up on call %s"%self.getCallID())
                self.sip.app.statusMessage("Call Disconnected")
                d, self.dropDef = self.dropDef, None
                d.callback('call disconnected')
            else:
                self.sip.app.debugMessage('Got OK in unexpected state %s'%state)
        elif message.code - (message.code%100) == 400:
            if state == 'SENT_CANCEL' and message.code == 487:
                #print "cancelled"
                self.sip.app.endCall(self.cookie)
                self.sip._delCallObject(self.getCallID())
                self.sip.app.debugMessage("Hung up on call %s"%self.getCallID())
                self.sip.app.statusMessage("Call Disconnected")
                return
            self.auth_attempts += 1
            if self.auth_attempts > 5:
                #print "TOO MANY AUTH FAILURES"
                self.setState('ABORTED')
                return
            if message.code in ( 401, 407 ):
                if state in ( 'SENT_INVITE', 'SENT_BYE'):
                    # Send an ACK - 3261, S17.1.1
                    self.sendAck(message)
                    method = message.headers['cseq'][0].split()[1]
                    if method == "BYE":
                        resend = self.sendBye
                    else:
                        resend = self.sendInvite
                    if message.code == 401:
                        inH, outH = 'www-authenticate', 'authorization'
                    else:
                        inH, outH = 'proxy-authenticate', 'proxy-authorization'
                    a = message.headers.get(inH)
                    interm1 = a[0].split(' ',1)
                    interm2 = interm1[1]
                    httpList = parse_http_list(interm2)
                    chal = digestauth.parse_keqv_list(httpList)
                    if a:
                        uri = str(self._remoteAOR)
                        credDef = self.sip.app.authCred(method, uri,
                                                realm=chal.get('realm','unknown'),
                                                retry=(self.auth_attempts > 1)
                                                          ).addErrback(log.err)
                        credDef.addCallback(lambda c, uri=uri, chal=a[0]:
                                        self.calcAuth(method,
                                                      uri=uri,
                                                      authchal=chal,
                                                      cred=c)
                            ).addCallback(lambda a, h=outH:
                                        resend(toAddr=None,
                                                        auth=a,
                                                        authhdr=h)
                            ).addErrback(log.err)
                    else:
                        # * is retarded. If you send in an incorrect digest auth,
                        # you just get back a 401/407, with no auth challenge.
                        # In this case, retry without an auth header to get another
                        # challenge.
                        if self.auth_attempts > 1:
                            self.sendInvite(str(self.dialog.getCallee()))
                        else:
                            log.err("FATAL 401/407 and no auth header")
                else:
                    log.err("Unknown state '%s' for a 401/407"%(state))
            else:
                if self.state == 'SENT_BYE':
                    d, self.dropDef = self.dropDef, None
                    # XXX failed to drop call. need exception here
                    d.errback(message.code)
                # We should send an ACK to a failed request.
                if self.state == 'SENT_INVITE':
                    self.sendAck(message)
                self.sip.app.debugMessage(message.toString())
                self.terminateCall(message)
                self.sip._delCallObject(self.getCallID())
                self.sip.app.statusMessage("Call Failed: %s %s"%(message.code,
                                                             message.phrase))
        elif message.code - (message.code%100) == 500:
            if self.state == 'SENT_BYE':
                d, self.dropDef = self.dropDef, None
                # XXX failed to drop call. need exception here
                d.errback(message.code)
            self.sip.app.debugMessage(message.toString())
            self.terminateCall(message)
            if self.state == 'SENT_INVITE':
                self.sendAck(message)
            self.sip._delCallObject(self.getCallID())
            self.sip.app.statusMessage("Call Failed: %s %s"%(message.code,
                                                             message.phrase))
        elif message.code - (message.code%100) == 600:
            if self.state == 'SENT_BYE':
                d, self.dropDef = self.dropDef, None
                # XXX failed to drop call. need exception here
                d.errback(message.code)
            self.sip.app.debugMessage(message.toString())
            if self.state == 'SENT_INVITE':
                self.sendAck(message)
            self.terminateCall(message)
            #self.sip.app.endCall(self.cookie, 'Other end sent %s'%message.toString())
            self.sip._delCallObject(self.getCallID())
            self.sip.app.statusMessage("Call Failed: %s %s"%(message.code,
                                                             message.phrase))
        else:
            self.sip.app.debugMessage(message.toString())

class Registration(Call):
    "State machine for registering with a server."

    # XXX make the retransmit timer an option?
    REGISTER_REFRESH_TIME = 840

    def __init__(self, phone):
        self.sip = phone
        self.regServer = None
        self.regAOR = None
        self.state = 'NEW'
        self._needSTUN = False
        self.cseq = random.randint(1000,5000)
        self.dialog = Dialog()
        self.nonce_count = 0
        self.cancel_trigger = None
        self.register_attempts = 0
        self._outboundProxyURI = None

    def startRegistration(self):
        from twisted.internet import reactor
        self.compDef = defer.Deferred()
        self.regServer = Address(self.sip.app.getPref('register_uri'))
        self.regURI = copy.copy(self.regServer)
        self.regAOR = copy.copy(self.regServer.getURI(parsed=True))
        self._remoteURI = self._remoteAOR = self.regAOR
        # XXX Display Name
        self.regAOR.username = self.sip.app.getPref('username')
        self.regAOR = Address(self.regAOR)
        self._localAOR = self._localFullAOR = Address(self.regAOR)
        #self.regURI.port = None
        d = self.setupLocalSIP(self.regServer)
        reactor.callLater(self.REGISTER_REFRESH_TIME, self.refreshRegistration)
        d.addCallback(self.sendRegistration).addErrback(log.err)
        return self.compDef

    def refreshRegistration(self):
        from twisted.internet import reactor
        reactor.callLater(self.REGISTER_REFRESH_TIME, self.refreshRegistration)
        self.state = 'NEW'
        self.register_attempts = 0
        self.sendRegistration()

    def sendRegistration(self, cb=None, auth=None, authhdr=None):
        # reset a lot of counters and the like
        username = self.sip.app.getPref('username')
        register = tpsip.Request('REGISTER', str(self.regURI))
        # XXX refactor all the common headers and the like
        register.addHeader('cseq', '%s REGISTER'%self.dialog.getCSeq(incr=1))
        register.addHeader('to', str(self.regAOR))
        register.addHeader('from', str(self.regAOR))
        state =  self.getState()
        if state in ( 'NEW', 'SENT_REGISTER', 'REGISTERED' ):
            register.addHeader('expires', 900)
        elif state in ( 'CANCEL_REGISTER' ):
            register.addHeader('expires', 0)
        register.addHeader('call-id', self.getCallID())
        if auth is not None:
            register.addHeader(authhdr, auth)
        register.addHeader('user-agent', 'Shtoom/%s'%ShtoomVersion)
        lhost, lport = self.getLocalSIPAddress()
        register.addHeader('contact', '<sip:%s@%s:%s>'%(
                                username, lhost, lport))
        register.addHeader('content-length', '0')
        register.creationFinished()
        self.addViaHeader(register)
        try:
            self.sip.transport.write(register.toString(), _hostportToIPPort(self.getRemoteSIPAddress()))
        except (socket.error, socket.gaierror):
            e,v,t = sys.exc_info()
            if self.compDef is not None:
                d, self.compDef = self.compDef, None
                d.errback(e(v))
            self.setState('ABORTED')
        else:
            if self.getState() in ( 'NEW', 'REGISTERED' ):
                self.setState('SENT_REGISTER')
        self.sip.app.debugMessage("register sent\n"+register.toString())

    def sendAuthResponse(self, authhdr, auth):
        self.sendRegistration(auth=auth, authhdr=authhdr)

    def recvResponse(self, message):
        from twisted.internet import reactor
        state = self.getState()
        if message.code in ( 401, 407 ):
            self.register_attempts += 1
            if self.register_attempts > 5:
                #print "REGISTRATION FAILED"
                self.setState('FAILED')
                return
            if state in ( 'SENT_REGISTER', 'CANCEL_REGISTER', 'REGISTERED' ):
                if message.code == 401:
                    inH, outH = 'www-authenticate', 'authorization'
                else:
                    inH, outH = 'proxy-authenticate', 'proxy-authorization'
                a = message.headers.get(inH)
                chal = digestauth.parse_keqv_list(
                                    parse_http_list(a[0].split(' ',1)[1])
                                                 )
                if a:
                    uri = str(self.regURI)
                    credDef = self.sip.app.authCred('REGISTER', uri,
                                            realm=chal.get('realm','unknown'),
                                            retry=(self.register_attempts > 1)
                                            )
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
                log.err("Unknown registration state '%s' for a 401/407"%(state))
        elif message.code in ( 200, ):
            self.sip.app.statusMessage("Registration: OK")
            # Woo. registration succeeded.
            self.sip.app.notifyEvent('registrationOK', self)
            self.register_attempts = 0
            if state == 'SENT_REGISTER':
                self.setState('REGISTERED')
                if 0 and self.cancel_trigger is None:
                    t = reactor.addSystemEventTrigger('before',
                                                      'shutdown',
                                                      self.cancelRegistration)
                    self.cancel_trigger = t
                if self.compDef is not None:
                    d, self.compDef = self.compDef, None
                    d.callback('registered')
            elif state == 'CANCEL_REGISTER':
                self.setState('UNREGISTERED')
                d = self._cancelDef
                del self._cancelDef
                d.callback(self)
            elif state == 'REGISTERED':
                # duplicate, or something
                pass
            else:
                log.err("Unknown state '%s' for a 200"%(state))
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





class SipProtocol(DatagramProtocol, object):
    '''A SIP protocol handler.'''

    __implements__ = ISip,

    def __init__(self, app, *args, **kwargs):
        self.app = app
        self._calls = {}
        super(SipProtocol, self).__init__(*args, **kwargs)

    def getCalls(self):
        return [c for c in self._calls.values() if not isinstance(c, Registration)]

    def getRegistrations(self):
        return [c for c in self._calls.values() if isinstance(c, Registration)]

    def register(self, removed=None):
        if removed:
            #print "cancelled", removed
            self._delCallObject(removed.getCallID())
        if self.app.getPref('register_uri') is not None:
            existing = self.getRegistrations()
            if existing:
                for reg in existing:
                    #print "removing", reg, existing
                    d = reg.cancelRegistration()
                    d.addCallbacks(self.register, log.err)
            else:
                log.msg("no outstanding registrations, registering", system="sip")
                r = Registration(self)
                d = r.startRegistration()
                return d

    def _newCallObject(self, to=None, callid=None):
        call = Call(self, uri=to, callid=callid)
        d = call.callStart()
        if call.getState() != 'ABORTED':
            if call.getCallID():
                self._calls[call.getCallID()] = call
            return call, d

    def updateCallObject(self, call, callid):
        "Used when Call setup returns a deferred result (e.g. STUN)"
        self._calls[call.getCallID()] = call

    def _getCallObject(self, callid):
        if type(callid) is list:
            callid = callid[0]
        if callid and callid.startswith('<') and callid.endswith('>'):
            callid = callid[1:-1]
        return self._calls.get(callid)

    def _delCallObject(self, callid):
        if type(callid) is list:
            callid = callid[0]
        if callid.startswith('<') and callid.endswith('>'):
            callid = callid[1:-1]
        del self._calls[callid]

    def placeCall(self, uri, fromuri=None, cookie=None):
        """Place a call.

        uri should be a string, an address of the person we are calling,
        e.g. 'sip:foo@example.com'.

        Returns a Call object and a Deferred
        """
        self.app.debugMessage("placeCall starting")
        try:
            call, _d = self._newCallObject(to=uri)
        except:
            e,v,t = sys.exc_info()
            log.err("call creation failed %r %s"%(v,v), system="sip")
            return defer.fail(v)
        #print "call is", call
        if call is None:
            _d.errback(CallFailed)
            return _d
        if cookie is not None:
            call.cookie = cookie
        invite = call.startOutboundCall(uri, fromAddr=fromuri)
        return _d

    def datagramReceived(self, datagram, addr):
        # We need to be careful here that we aren't getting late STUN packets :-(
        if len(datagram) < 100:
            maybestun = struct.unpack('!h', datagram[:2])
            if maybestun[0] in (0x0101, 0x0111):
                log.msg("late stun packet, ignoring", system="sip")
                return
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
            self.app.debugMessage("sip Protocol got SIP response %s: %s"%(
                                        message.code, message.phrase))
            if message.code == 401:
                self.app.statusMessage("Trying SIP registration password...")
            else:
                self.app.statusMessage("%s: %s"%(message.code,message.phrase))
        else:
            self.app.debugMessage("got SIP request %s: %s"%(
                                        message.method, message.uri))
            self.app.debugMessage("got SIP request\n %s"%( message.toString()))
        callid = message.headers.get('call-id')
        call = self._getCallObject(callid)
        if message.response and not call:
            # XXX  should keep a cache of recently discarded calls
            self.app.debugMessage("SIP response refers to unknown call %s %r"%(
                                                    callid, self._calls.keys()))
            return
        if message.request and message.method.lower() != 'invite' and not call:
            self.app.debugMessage("SIP request refers to unknown call %s %r"%(
                                                    callid, self._calls.keys()))
            callid = message.headers['call-id'][0]
            call, _d = self._newCallObject(callid = callid)
            call.sendResponse(message, 481)
            self._delCallObject(callid)
            return
        if message.request:
            #print "handling request", message.method
            if not call:
                # We must have received an INVITE here. Handle it, reply with
                # a 180 Ringing.
                callid = message.headers['call-id'][0]
                call, defsetup = self._newCallObject(callid=callid)
                call.startInboundCall(message)
            else:
                if message.method == 'BYE':
                    # Aw. Other end goes away :-(
                    self.app.statusMessage("received BYE")
                    # Drop the call, send a 200.
                    call.recvBye(message)
                    call.terminateCall(message)
                    self._delCallObject(callid)
                elif message.method == 'INVITE':
                    # modify dialog
                    call.recvInvite(message)
                elif message.method == 'ACK':
                    call.recvAck(message)
                elif message.method == 'CANCEL':
                    call.recvCancel(message)

        elif message.response:
            #print "handling response", message.code
            call.recvResponse(message)
