# Copyright (C) 2004 Anthony Baxter

from twisted.internet.protocol import DatagramProtocol
from twisted.python import log

# Placeholder until I get time to integrate old rtcp code into new
# codebase

class RTCPProtocol(DatagramProtocol):
    def datagramReceived(self, datagram, addr):
        print "got RTCP from", addr
    def sendDatagram(self, packet):
        self.transport.write(packet)
