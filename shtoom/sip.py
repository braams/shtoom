# Copyright (C) 2003 Anthony Baxter

'''SIP client code.'''

from interfaces import ISipPhone

from twisted.internet.protocol import DatagramProtocol, ConnectedDatagramProtocol
from twisted.internet import defer
from twisted.internet import reactor
from twisted.protocols import sip as tpsip
from rtp import RTPProtocol

import shtoom

from twisted.python import log
import random, sys, socket

from shtoom import prefs


def genCallId():
    return 400000000 + random.randint(0,2000000)

def genStandardDate(t=None):
    import time
    if t is None:
        t = time.gmtime()
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", t)

class Call(object):
    '''State machine for a phone call.'''
    
    def __init__(self, phone, deferred, uri=None, callid=None):
        self.phone = phone
        self.compDef = deferred
        self._callID = None
        self.uri = None
        self.state = 'NEW'
        self.rtp = None
        self._needSTUN = False

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

    def getTag(self):
        if not hasattr(self, '_tag'):
            self._tag = ('%04x'%(random.randint(0, 2**10)))[:4]
            self._tag += ('%04x'%(random.randint(0, 2**10)))[:4]
        return self._tag

    def setLocalIP(self, dest):
        ''' Try and determine the local IP address to use. We use a 
            ConnectedDatagramProtocol in the (faint?) hope that on a machine 
            with multiple interfaces, we'll get the right one
        '''
        # XXX Allow over-riding
        from shtoom.stun import StunHook, getPolicy
        host, port = dest
        import prefs
        if prefs.localip is not None:
            self._localAddress = (prefs.localip, prefs.localport or 5060)
        else:
            # it is a hack! 
            protocol = ConnectedDatagramProtocol()
            port = reactor.connectUDP(host, port, protocol)
            if protocol.transport:
                locAddress = protocol.transport.getHost()[1:3]
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
            deferred.addCallback(self.setStunnedLocalIP)
            SH = StunHook(self.phone)
            deferred = SH.discoverStun(deferred)
        else:
            self._localIP, self._localPort = locAddress
            if not self._callID:
                self.setCallID()
            self.setupDeferred.callback((host,port))

    def setStunnedLocalIP(self, (host, port)):
        log.msg("according to STUN, local address is %s:%s"%(host, port))
        self._localIP = host
        self._localPort = port
        # XXX Check for multiple firings!
        if not self._callID:
            self.setCallID()
            self.phone.updateCallObject(self, self.getCallID())
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

    def setupRTP(self, cb):
        ''' Create local RTP socket. At this point, we have already set up
            the local SIP socket, so we can cheat a bit for STUN &c 
        '''
        self.rtp = RTPProtocol()
        d = self.rtp.createRTPSocket(self.getLocalSIPAddress()[0], 
                                     self._needSTUN)
        d.addCallback(cb)

    def teardownRTP(self):
        self.rtp.stopSendingAndReceiving()

    def acceptCall(self, message=None):
        ''' Accept currently pending call.
        '''
        self.setupRTP(cb=lambda x:self.acceptedCall())

    def acceptedCall(self):
        self.sendResponse(self._invite, 200)
        self.setState('INVITE_OK')

    def rejectCall(self, message=None):
        ''' Accept currently pending call.
        '''
        self.sendResponse(self._invite, 603)
        self.setState('ABORTED')
        self.compDef.errback('rejected')

    def sendResponse(self, message, code):
        ''' Send a response to a message. message is the response body, 
	    code is the response code (e.g.  200 for OK)
        '''
        from shtoom.multicast.SDP import SDP
        if message.method == 'INVITE' and code == 200:
            sdp = self.rtp.getSDP()
            othersdp = SDP(message.body)
            sdp.intersect(othersdp)
            if not sdp.rtpmap:
                self.sendResponse(message, 406)
                self.setState('ABORTED')
                return
            self.rtp.setFormat(sdp.rtpmap)
        resp = tpsip.Response(code) 
        # XXXXXXX add a branch= ...
        via = tpsip.parseViaHeader(message.headers['via'][0])
        branch = via.branch
        if branch:
            branch = ';branch=%s'%branch
        else:
            branch = ''
        resp.addHeader('via', 'SIP/2.0/UDP %s:%s%s'%(
                                    self.getLocalSIPAddress()+(branch,)))
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
            resp.addHeader('contact', message.headers['to'][0])
            # We include SDP here
            resp.addHeader('content-type', 'application/sdp')
            sdp = sdp.show()
            resp.addHeader('content-length', len(sdp))
            resp.bodyDataReceived(sdp)
        else:
            resp.addHeader('content-length', 0)
        resp.creationFinished()
        try:
            self.phone.transport.write(resp.toString(), self.getRemoteSIPAddress())
            print "Response sent", resp.toString()
        except (socket.error, socket.gaierror):
            e,v,t = sys.exc_info()
            #self.compDef.errback(e(v))
            self.setState('ABORTED')
        
    def startOutboundCall(self, toAddr):
        uri = uri=tpsip.parseURL(toAddr)
        d = self.setupLocalSIP(uri=uri)
        d.addCallback(lambda x:self.startSendInvite(toAddr, init=1))

    def startInboundCall(self, invite):
        via = tpsip.parseViaHeader(invite.headers['via'][0])
        d = self.setupLocalSIP(via=via)
        d.addCallback(lambda x:self.recvInvite(invite))

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

    def startSendInvite(self, toAddr, init=0):
        if init:
            self.setupRTP(cb=lambda x:self.sendInvite(toAddr, init))
        else:
            self.sendInvite(toAddr, init=0)

    def sendInvite(self, toAddr, init=0):
        invite = tpsip.Request('INVITE', str(self.remote))
        # XXX refactor all the common headers and the like
        invite.addHeader('via', 'SIP/2.0/UDP %s:%s;rport'%
                                                self.getLocalSIPAddress())
        invite.addHeader('cseq', '%s INVITE'%self.getCSeq(incr=1))
        invite.addHeader('to', str(self.uri))
        invite.addHeader('content-type', 'application/sdp')
        invite.addHeader('from', '"%s" <sip:%s>;tag=%s'%(
                            prefs.username, prefs.email_address, self.getTag()))
        invite.addHeader('call-id', self.getCallID())
        invite.addHeader('subject', 'sip: %s'%(prefs.email_address))
        invite.addHeader('user-agent', 'Shtoom/%s'%shtoom.Version)
        lhost, lport = self.getLocalSIPAddress()
        invite.addHeader('contact', '"%s" <sip:%s:%s;transport=udp>'%(
                                prefs.username, lhost, lport))
        s = self.rtp.getSDP()
        sdp = s.show()
        invite.addHeader('content-length', len(sdp))
        invite.bodyDataReceived(sdp)
        invite.creationFinished()
        try:
            self.phone.transport.write(invite.toString(), self.getRemoteSIPAddress())
            print "Invite sent", invite.toString()
        except (socket.error, socket.gaierror):
            e,v,t = sys.exc_info()
            self.compDef.errback(e(v))
            self.setState('ABORTED')
        else:
            self.setState('SENT_INVITE')

    def extractURI(self, val):
        name,uri,params = tpsip.parseAddress(val)
        return uri.toString()

    def sendAck(self, okmessage, startRTP=0):
        from shtoom.multicast.SDP import SDP
        sdp = SDP(okmessage.body)
        log.msg("RTP server:port is %s:%s"%(sdp.ipaddr, sdp.port))
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
                            prefs.username, prefs.email_address, self.getTag()))
        ack.addHeader('call-id', self.getCallID())
        ack.addHeader('user-agent', 'Shtoom/%s'%shtoom.Version)
        ack.addHeader('content-length', 0)
        ack.creationFinished()
        if startRTP:
            self.rtp.startSendingAndReceiving((sdp.ipaddr,sdp.port))
        if hasattr(self, 'compDef'):
            self.compDef.callback(self)
            del self.compDef
        self.phone.transport.write(ack.toString(), (uri.host, (uri.port or 5060)))
        self.setState('CONNECTED')

    def sendBye(self):
        dest = self.extractURI(self.contact)
        uri = tpsip.parseURL(dest)
        bye = tpsip.Request('BYE', dest)
        # XXX refactor all the common headers and the like
        bye.addHeader('via', 'SIP/2.0/UDP %s:%s;rport'%self.getLocalSIPAddress())
        bye.addHeader('cseq', '%s BYE'%self.getCSeq(incr=1))
        bye.addHeader('to', self.uri)
        bye.addHeader('from', '"%s" <sip:%s>;tag=%s'%(
                            prefs.username, prefs.email_address, self.getTag()))
        bye.addHeader('call-id', self.getCallID())
        bye.addHeader('user-agent', 'Shtoom/%s'%shtoom.Version)
        bye.addHeader('content-length', 0)
        bye.creationFinished()
        bye, dest = bye.toString(), (uri.host, (uri.port or 5060))
        self.phone.transport.write(bye, dest)
        self.setState('SENT_BYE')

    def sendCancel(self):
        ''' Sends a CANCEL message to kill a call that's in the process of
            being established 
        '''
        raise NotImplementedError

    def recvBye(self, message):
        ''' An in-progress call got a BYE from the other end. Hang up
            call, send a 200.
        '''
        self.sendResponse(message, 200)

    def recvCancel(self, message):
        ''' The remote UAC changed it's mind about the new call and 
            gave up.
        '''

    def recvAck(self, message):
        ''' The remote UAC has ACKed our response to their INVITE. 
            Start sending and receiving audio.
        '''
        from shtoom.multicast.SDP import SDP
        sdp = SDP(self._invite.body)
        self.setState('CONNECTED')
        if hasattr(self, 'compDef'):
            self.rtp.startSendingAndReceiving((sdp.ipaddr,sdp.port))
            deferred, self.compDef = self.compDef, None
            deferred.callback('connected')

    def recvOptions(self, message):
        ''' Received an OPTIONS request from a remote UA.
            Put together a 200 response if we're ok with the Require headers,
            otherwise an error (XXXXX)
        '''


class SipPhone(DatagramProtocol, object):
    '''A SIP phone.'''
    
    __implements__ = ISipPhone,

    def __init__(self, ui, *args, **kwargs):
        self.ui = ui
        self._calls = {}
        super(SipPhone, self, *args, **kwargs)

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
        '''Place a call.

        uri should be a string, an address of the person we are calling,
        e.g. 'sip:foo@example.com'.

        Returns a Call object and a Deferred
        '''
        self.ui.debugMessage("placeCall starting")
        _d = defer.Deferred()
        call = self._newCallObject(_d, to=uri)
        if call is None:
            return '', _d
        invite = call.startOutboundCall(uri)
        # Set up a callLater in case we don't get a response, for a retransmit
        # Set up a timeout for the call completion
        return call, _d

    def dropCall(self, call):
        '''Drop call '''
        # XXX return a deferred.
        state = call.getState()
        print "looking for state %s"%state
        if state == 'NONE':
            self.ui.debugMessage("no call to drop")
        elif state in ( 'CONNECTED', ):
            call.sendBye()
        elif state in ( 'SENT_INVITE', ):
            call.sendCancel()
            call.setState('SENT_CANCEL')

    def startDTMF(self, digit):
        '''Start sending DTMF digit 'digit'
        '''
        self.ui.debugMessage("startDTMF not implemented yet!")

    def stopDTMF(self):
        '''Stop sending DTMF digit 'digit'
        '''
        self.ui.debugMessage("stopDTMF not implemented yet!")

    def datagramReceived(self, datagram, addr):
        self.ui.debugMessage("Got a SIP packet from %s:%s"%(addr))
        mp = tpsip.MessagesParser(self.sipMessageReceived)
        self.ui.debugMessage("SIP PACKET\n%s"%(datagram))
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
            self.ui.debugMessage("got SIP response %s: %s"%(
                                        message.code, message.phrase))
            self.ui.statusMessage("%s: %s"%(message.code,message.phrase))
            self.ui.debugMessage("got SIP response\n %s"%( message.toString()))
        else:
            self.ui.debugMessage("got SIP request %s: %s"%(
                                        message.method, message.uri))
            self.ui.debugMessage("got SIP request\n %s"%( message.toString()))
        callid = message.headers['call-id']
        call = self._getCallObject(callid)
        if message.response and not call:
            self.ui.debugMessage("SIP response refers to unknown call %s %r"%(
                                                    callid, self._calls.keys()))
            return
        if message.request and message.method.lower() != 'invite' and not call:
            self.ui.debugMessage("SIP request refers to unknown call %s %r"%(
                                                    callid, self._calls.keys()))
            return
        if message.request:
            print "handling request", message.method
            if not call:
                # We must have received an INVITE here. Handle it, reply with
                # a 180 Ringing.
                callid = message.headers['call-id'][0]
                defaccept = defer.Deferred()
                defsetup = defer.Deferred()
                call = self._newCallObject(defsetup, callid=callid)
                call.startInboundCall(message)
                defaccept.addCallbacks(call.acceptCall, call.rejectCall)
                if message.headers.has_key('subject'):
                    subj = message.headers['subject'][0]
                else:
                    name,uri,params =  tpsip.parseAddress(message.headers['from'][0])
                    subj = "From: %s %s" %(name,uri)
                self.ui.incomingCall(subj, call, defaccept, defsetup)
            else:
                if message.method == 'BYE':
                    # Aw. Other end goes away :-(
                    self.ui.statusMessage("received BYE")
                    # Drop the call, send a 200.
                    call.recvBye(message)
                    call.teardownRTP()
                    self.ui.callDisconnected(call)
                    self._delCallObject(callid)
                elif message.method == 'INVITE':
                    # modify dialog
                    call.recvInvite(message)
                elif message.method == 'ACK':
                    call.recvAck(message)
                

        elif message.response:
            print "handling response", message.code
            if message.code in ( 100, 180, 181, 182 ):
                return
            elif message.code == 200:
                state = call.getState() 
                if state == 'SENT_INVITE':
                    self.ui.debugMessage(message.body)
                    call.sendAck(message, startRTP=1)
                elif state == 'CONNECTED':
                    self.ui.debugMessage('Got duplicate OK to our ACK')
                    call.sendAck(message)
                elif state == 'SENT_BYE':
                    call.teardownRTP()
                    self._delCallObject(callid)
                    self.ui.debugMessage("Hung up on call %s"%callid)
                    self.ui.statusMessage("idle")
                else:
                    self.ui.debugMessage('Got OK in unexpected state %s'%state)
            elif message.code - (message.code%100) == 400:
                self.ui.debugMessage(message.toString())
                self.ui.callDisconnected(call)
                pass
            elif message.code - (message.code%100) == 500:
                self.ui.debugMessage(message.toString())
                self.ui.callDisconnected(call)
                pass
            elif message.code - (message.code%100) == 600:
                self.ui.debugMessage(message.toString())
                self.ui.callDisconnected(call)
                pass
            else:
                self.ui.debugMessage(message.toString())


