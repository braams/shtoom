from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
class Echo(Protocol):
    def connectionMade(self):
        print "connectionMade"
        self.cnt = 1000
        self.counter = 0

    def connectionLost(self, reason):
        print "connectionLost", reason

    def dataReceived(self, data):
        self.counter += 1
        if self.counter > self.cnt:
            print '.'
            self.counter = 0
        self.transport.write(data)

factory = Factory()
factory.protocol = Echo
reactor.listenTCP(22000, factory, interface='127.0.0.1')
reactor.run()
