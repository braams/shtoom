# Copyright (C) 2003 Anthony Baxter

"""SIP client code."""

from interfaces import ISipPhone

from twisted.internet.protocol import DatagramProtocol, ConnectedDatagramProtocol
from twisted.internet import reactor
from twisted.protocols import sip as tpsip
from rtp import RTPProtocol

from twisted.python import log
import random

from shtoom import prefs


def genCallId():
    return 400000000 + random.randint(0,2000000)


class Call(object):
    """State machine for a phone call."""
    
    def __init__(self, to):
        self.cseq = random.randint(1000,5000)
        self.rtp = None
        self.url = tpsip.parseURL(to)
        self.setLocalIP((self.url.host, self.url.port or 5060))
        self.setCallID()
        self.state = 'NONE'

    def setCallID(self):
        self._callID = '%s@%s'%(genCallId(), self.getLocalSIPAddress()[0])

    def setState(self, state):
        self.state = state

    def getState(self):
        return self.state 

    def setLocalIP(self, (host,port)):
        """ Try and determine the local IP address to use. We do a connect_ex
            in the (faint?) hope that on a machine with multiple interfaces,
            we'll get the right one
        """
        # XXX Allow over-riding
        import prefs
        if prefs.localip is not None:
            self._localIP = prefs.localip
        else:
            # it is a hack! and won't work for NAT. oh well.
            protocol = ConnectedDatagramProtocol()
            port = reactor.connectUDP(host, port, protocol)
            self._localIP = protocol.transport.getHost()[1]
            port.stopListening()
        log.msg("using local IP address %s"%(self._localIP))

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

    def genInvite(self, toAddr):
        from multicast.SDP import SimpleSDP
        self.setLocalIP((self.url.host, self.url.port or 5060))
        invite = tpsip.Request('INVITE', str(self.url))
        invite.addHeader('via', 'SIP/2.0/UDP %s;rport'%(
                                    self.getLocalSIPAddress()[0]))
        invite.addHeader('cseq', '%s INVITE'%self.getCSeq(incr=1))
        invite.addHeader('to', str(self.url))
        invite.addHeader('content-type', 'application/sdp')
        invite.addHeader('from', '"%s" <sip:%s>;tag=%s'%(
                                    prefs.myname, prefs.myemail, prefs.mytag))
        invite.addHeader('call-id', self.getCallID())
        invite.addHeader('subject', 'sip%s'%(prefs.myemail))
        invite.addHeader('user-agent', 'Shtoom/0.0')
        invite.addHeader('contact', '"%s" <sip:%s;transport=udp>'%(
                                    prefs.myname, self.getLocalSIPAddress()[0]))
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
        return invite.toString()

    def genAck(self, okmessage, startRTP=0):
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

        url = tpsip.parseURL(to)
        ack = tpsip.Request('ACK', contact)
        ack.addHeader('via', 'SIP/2.0/UDP %s;rport'%self.getLocalSIPAddress()[0])
        ack.addHeader('cseq', '%s ACK'%self.getCSeq())
        ack.addHeader('to', to)
        ack.addHeader('from', '"%s" <sip:%s>;tag=%s'%(prefs.myname, prefs.myemail, prefs.mytag))
        ack.addHeader('call-id', self.getCallID())
        ack.addHeader('user-agent', 'Shtoom/0.1')
        ack.addHeader('content-length', 0)
        ack.creationFinished()
        self._sentAck = ack.toString(), (url.host, (url.port or 5060))
        if startRTP:
            self.rtp.startSendingAndReceiving((sdp.ipaddr,sdp.port))
        return self._sentAck

    def genBye(self):
        url = tpsip.parseURL(self.to)
        bye = tpsip.Request('BYE', self.contact)
        bye.addHeader('via', 'SIP/2.0/UDP %s;rport'%self.getLocalSIPAddress()[0])
        bye.addHeader('cseq', '%s BYE'%self.getCSeq(incr=1))
        bye.addHeader('to', self.to)
        bye.addHeader('from', '"%s" <sip:%s>;tag=%s'%(prefs.myname, prefs.myemail, prefs.mytag))
        bye.addHeader('call-id', self.getCallID())
        bye.addHeader('user-agent', 'Shtoom/0.1')
        bye.addHeader('content-length', 0)
        bye.creationFinished()
        self._sentBye = bye.toString(), (url.host, (url.port or 5060))
        return self._sentBye



class SipPhone(DatagramProtocol, object):
    """A SIP phone."""
    
    __implements__ = ISipPhone,

    def __init__(self, ui, *args, **kwargs):
        self.ui = ui
        self._calls = {}
        super(SipPhone, self, *args, **kwargs)

    def _newCallObject(self, to):
        call = Call(to)
        self._calls[call.getCallID()] = call
        return call

    def _getCallObject(self, callid):
        if type(callid) is list:
            callid = callid[0]
        if callid.startswith('<') and callid.endswith('>'):
            callid = callid[1:-1]
        return self._calls[callid] 

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

        Returns callid, a string
        """
        self.ui.debugMessage("placeCall starting")
        call = self._newCallObject(url)
        call.setupRTP()
        invite = call.genInvite(url)
        self.transport.write(invite, call.getRemoteSIPAddress())
        # Set up a callLater in case we don't get a response, for a retransmit
        call.setState('SENT_INVITE')
        return call.getCallID()

    def dropCall(self, callid):
        """Drop call identified by 'callid'."""
        call = self._getCallObject(callid)
        if not call:
            self.ui.debugMessage("no such call %s"%callid)
            return
        state = call.getState()
        if state == 'NONE':
            self.ui.debugMessage("no call to drop")
        elif state in ( 'SENT_ACK', 'SENT_INVITE'):
            bye, dest = call.genBye()
            self.transport.write(bye, dest)
            self.ui.debugMessage("sent a BYE message")
            call.setState('SENT_BYE')


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
        self.ui.debugMessage("got SIP response %s: %s"%(
                                        message.code, message.phrase))
        self.ui.statusMessage("%s: %s"%(message.code,message.phrase))
        self.ui.debugMessage("got SIP response\n %s"%( message.toString()))
        callid = message.headers['call-id']
        call = self._getCallObject(callid)
        if not call:
            self.ui.debugMessage("SIP response refers to unknown call %s"%(
                                                                    callid))
            return
        if message.code in ( 100, 180, 181, 182 ):
            return
        elif message.code == 200:
            state = call.getState() 
            if state == 'SENT_INVITE':
                self.ui.debugMessage(message.body)
                ack, dest = call.genAck(message, startRTP=1)
                self.transport.write(ack, dest)
                call.setState('SENT_ACK')
            elif state == 'SENT_ACK':
                self.ui.debugMessage('Got duplicate OK to our ACK')
                ack, dest = call.genAck(message)
                self.transport.write(ack, dest)
            elif state == 'SENT_BYE':
                call.teardownRTP()
                self._delCallObject(callid)
                self.ui.debugMessage("Hung up on call %s"%callid)
                self.ui.statusMessage("idle")
            else:
                self.ui.debugMessage('Got OK in unexpected state %s'%state)
        else:
            self.ui.debugMessage(message.toString())





