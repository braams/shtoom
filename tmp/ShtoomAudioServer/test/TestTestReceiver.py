from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
class PrintSender(DatagramProtocol):
    def startProtocol(self):
        print self.transport
        host, port = "127.0.0.1", 21000
        self.transport.connect(host, port)
        self._cbConnected((host, port))

    def _cbConnected(self, (host, port)):
        self.transport.write("hello")

    def datagramReceived(self, data, (host, port)):
        print "received %r from %s:%d" % (data, host, port)

reactor.listenUDP(0, PrintSender())
reactor.run()
