# Copyright (C) 2003 Anthony Baxter

"""SIP client code."""

from interfaces import ISipPhone

from twisted.internet.protocol import DatagramProtocol, ConnectedDatagramProtocol
from twisted.internet import defer
from twisted.internet import reactor
from twisted.protocols import sip as tpsip
from rtp import RTPProtocol

from twisted.python import log
import random, sys, socket

from shtoom import prefs


def genCallId():
    return 400000000 + random.randint(0,2000000)


class Call(object):
    """State machine for a phone call."""
    
    def __init__(self, transport, deferred, to=None, callid=None):
        self.transport = transport
        self.compDef = deferred
        self.state = 'NEW'
        self.cseq = random.randint(1000,5000)
        self.rtp = None
        if to:
            self.url = tpsip.parseURL(to)
            ip = self.setLocalIP(dest=(self.url.host, self.url.port or 5060))
        else:
            self.url = None
        if ip:
            self.setCallID(callid)
            self.state = 'NONE'

    def abortCall(self):
        # Bail out.
        self.state = 'ABORTED'

    def setCallID(self, callid):
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
            self._tag = ('%08x'%(random.randint(0, 2**32)))[:8]
        return self._tag

    def setLocalIP(self, dest):
        """ Try and determine the local IP address to use. We do a connect_ex
            in the (faint?) hope that on a machine with multiple interfaces,
            we'll get the right one
        """
        # XXX Allow over-riding
        host, port = dest
        import prefs
        if prefs.localip is not None:
            self._localIP = prefs.localip
        else:
            # it is a hack! and won't work for NAT. oh well.
            protocol = ConnectedDatagramProtocol()
            port = reactor.connectUDP(host, port, protocol)
            if protocol.transport:
                self._localIP = protocol.transport.getHost()[1]
                port.stopListening()
                log.msg("using local IP address %s"%(self._localIP))
            else:
                self.compDef.errback(ValueError("couldn't connect to %s"%(
                                            host)))
                self.abortCall()
                return None
        return self._localIP

    def getCSeq(self, incr=0):
        if incr:
            self.cseq += 1
        return self.cseq

    def getCallID(self):
        return self._callID

    def getLocalSIPAddress(self):
        return (self._localIP, prefs.localport or 5060)

    def getRemoteSIPAddress(self):
        return (self.url.host, (self.url.port or 5060))

    def setupRTP(self):
        self.rtp = RTPProtocol()
        self._lrtpPort, self._lrtcpPort = self.rtp.createRTPSocket()

    def teardownRTP(self):
        self.rtp.stopSendingAndReceiving()

    def recvInvite(self, invite):
        self._invite = invite
        trying = tpsip.Response(100)
        invite.addHeader('via', 'SIP/2.0/UDP %s;rport'%(
                                    self.getLocalSIPAddress()[0]))
        invite.addHeader('from', message.headers['from'])
        invite.addHeader('to', message.headers['to'])
        invite.addHeader('call-id', message.headers['call-id'])
        invite.addHeader('cseq', message.headers['cseq'])
        invite.addHeader('server', 'Shtoom/0.1')
        invite.addHeader('content-length', 0)
        

    def sendInvite(self, toAddr):
        from multicast.SDP import SimpleSDP, SDP
        self.setLocalIP(dest=(self.url.host, self.url.port or 5060))
        invite = tpsip.Request('INVITE', str(self.url))
        # XXX refactor all the common headers and the like
        invite.addHeader('via', 'SIP/2.0/UDP %s;rport'%(
                                    self.getLocalSIPAddress()[0]))
        invite.addHeader('cseq', '%s INVITE'%self.getCSeq(incr=1))
        invite.addHeader('to', str(self.url))
        invite.addHeader('content-type', 'application/sdp')
        invite.addHeader('from', '"%s" <sip:%s>;tag=%s'%(
                            prefs.username, prefs.email_address, self.getTag()))
        invite.addHeader('call-id', self.getCallID())
        invite.addHeader('subject', 'sip%s'%(prefs.email_address))
        invite.addHeader('user-agent', 'Shtoom/0.0')
        invite.addHeader('contact', '"%s" <sip:%s;transport=udp>'%(
                                prefs.username, self.getLocalSIPAddress()[0]))
        s = SimpleSDP()
        s.setPacketSize(160)
        s.setServerIP(self.getLocalSIPAddress()[0])
        s.setLocalPort(self._lrtpPort)
        s.addRtpMap('PCMU', 8000) # G711 ulaw
        #s.addRtpMap('GSM', 8000)
        #s.addRtpMap('DVI4', 8000)
        #s.addRtpMap('DVI4', 16000)
        #s.addRtpMap('speex', 8000, payload=110)
        #s.addRtpMap('speex', 16000, payload=111)
        sdp = s.show()
        invite.addHeader('content-length', len(sdp))
        invite.bodyDataReceived(sdp)
        invite.creationFinished()
        try:
            self.transport.write(invite.toString(), self.getRemoteSIPAddress())
        except (socket.error, socket.gaierror):
            e,v,t = sys.exc_info()
            self.compDef.errback(e(v))
            self.setState('ABORTED')
        else:
            self.setState('SENT_INVITE')

    def sendAck(self, okmessage, startRTP=0):
        from multicast.SDP import SDP
        sdp = SDP(okmessage.body)
        log.msg("RTP server:port is %s:%s"%(sdp.ipaddr, sdp.port))
        contact = okmessage.headers['contact']
        if type(contact) is list:
            contact = contact[0]
        if contact.startswith('<') and contact.endswith('>'):
            contact = contact[1:-1]
        self.contact = contact
        to = okmessage.headers['to']
        if type(to) is list:
            to = to[0]
        self.to = to

        # XXX Check the OK response's SDP, find what codec we 
        # should be using

        url = tpsip.parseURL(to)
        ack = tpsip.Request('ACK', contact)
        # XXX refactor all the common headers and the like
        ack.addHeader('via', 'SIP/2.0/UDP %s;rport'%self.getLocalSIPAddress()[0])
        ack.addHeader('cseq', '%s ACK'%self.getCSeq())
        ack.addHeader('to', to)
        ack.addHeader('from', '"%s" <sip:%s>;tag=%s'%(
                            prefs.username, prefs.email_address, self.getTag()))
        ack.addHeader('call-id', self.getCallID())
        ack.addHeader('user-agent', 'Shtoom/0.1')
        ack.addHeader('content-length', 0)
        ack.creationFinished()
        if startRTP:
            self.rtp.startSendingAndReceiving((sdp.ipaddr,sdp.port))
        if hasattr(self, 'compDef'):
            self.compDef.callback(self)
            del self.compDef
        self.transport.write(ack.toString(), (url.host, (url.port or 5060)))
        self.setState('SENT_ACK')

    def sendBye(self):
        url = tpsip.parseURL(self.to)
        bye = tpsip.Request('BYE', self.contact)
        # XXX refactor all the common headers and the like
        bye.addHeader('via', 'SIP/2.0/UDP %s;rport'%self.getLocalSIPAddress()[0])
        bye.addHeader('cseq', '%s BYE'%self.getCSeq(incr=1))
        bye.addHeader('to', self.to)
        bye.addHeader('from', '"%s" <sip:%s>;tag=%s'%(
                            prefs.username, prefs.email_address, self.getTag()))
        bye.addHeader('call-id', self.getCallID())
        bye.addHeader('user-agent', 'Shtoom/0.1')
        bye.addHeader('content-length', 0)
        bye.creationFinished()
        bye, dest = bye.toString(), (url.host, (url.port or 5060))
        self.transport.write(bye, dest)
        self.setState('SENT_BYE')

    def sendCancel(self):
        ''' Sends a CANCEL message to kill a call that's in the process of
            being established 
        '''
        raise NotImplementedError

    def recvInvite(self, message):
        pass


class SipPhone(DatagramProtocol, object):
    """A SIP phone."""
    
    __implements__ = ISipPhone,

    def __init__(self, ui, *args, **kwargs):
        self.ui = ui
        self._calls = {}
        super(SipPhone, self, *args, **kwargs)

    def _newCallObject(self, deferred, to=None, callid=None):
        call = Call(self.transport, deferred, to=to, callid=callid)
        if call.getState() != 'ABORTED':
            self._calls[call.getCallID()] = call
            return call

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
        
    def placeCall(self, url):
        """Place a call.

        url should be a string, an address of the person we are calling,
        e.g. 'sip:foo@example.com'.

        Returns a Call object and a Deferred
        """
        self.ui.debugMessage("placeCall starting")
        _d = defer.Deferred()
        call = self._newCallObject(_d, to=url)
        if call is None:
            return '', _d
        call.setupRTP()
        invite = call.sendInvite(url)
        # Set up a callLater in case we don't get a response, for a retransmit
        # Set up a timeout for the call completion
        return call, _d

    def dropCall(self, call):
        """Drop call """
        # XXX return a deferred.
        state = call.getState()
        if state == 'NONE':
            self.ui.debugMessage("no call to drop")
        elif state in ( 'SENT_ACK', ):
            call.sendBye()
        elif state in ( 'SENT_INVITE', ):
            call.sendCancel()
            call.setState('SENT_CANCEL')

    def startDTMF(self, digit):
        """Start sending DTMF digit 'digit'
        """
        self.ui.debugMessage("startDTMF not implemented yet!")

    def stopDTMF(self):
        """Stop sending DTMF digit 'digit'
        """
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
                                                    callid, self.calls.keys()))
            return
        if message.request and message.method.lower() != 'invite' and not call:
            self.ui.debugMessage("SIP request refers to unknown call %s %r"%(
                                                    callid, self.calls.keys()))
            return
        if message.request:
            print "handling request", message.method
            if not call:
                # We must have received an INVITE here. Handle it, reply with
                # a 200 OK, including an SDP message body
                callid = message.headers['call-id']
                defaccept = defer.Deferred()
                defsetup = defer.Deferred()
                call = self._newCallObject(defsetup, callid=callid)
                trying, dest = call.recvInvite(message)
                self.transport.write(trying, dest)
                defaccept.addCallbacks(self.acceptCall, self.rejectCall)
                self.ui.incomingCall(message.headers['subject'], callid, 
                                                        defaccept, defsetup)
                # Send back a TRYING response
            else:
                if message.method == 'BYE':
                    # Aw. Other end goes away :-(
                    # Drop the call, send a 200.
                    pass
                

        elif message.response:
            print "handling response", message.code
            if message.code in ( 100, 180, 181, 182 ):
                return
            elif message.code == 200:
                state = call.getState() 
                if state == 'SENT_INVITE':
                    self.ui.debugMessage(message.body)
                    call.sendAck(message, startRTP=1)
                elif state == 'SENT_ACK':
                    self.ui.debugMessage('Got duplicate OK to our ACK')
                    call.sendAck(message)
                elif state == 'SENT_BYE':
                    call.teardownRTP()
                    self._delCallObject(callid)
                    self.ui.debugMessage("Hung up on call %s"%callid)
                    self.ui.statusMessage("idle")
                else:
                    self.ui.debugMessage('Got OK in unexpected state %s'%state)
            else:
                self.ui.debugMessage(message.toString())


