from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
class Print(DatagramProtocol):
    def datagramReceived(self, data, (host, port)):
        print "received %r from %s:%d" % (data, host, port)

reactor.listenUDP(22000, Print())
reactor.run()
