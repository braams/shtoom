from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import math
import struct
class SineProducer(Protocol):
    def connectionMade(self):
        fourhundred = [int(32767 * math.sin(x*(math.pi/10))) for x in range(100)]
        self.data = struct.pack('100h', *fourhundred)
        self.startLoop()

    def startLoop(self):
        reactor.callLater((1.0 / 90.0), self.startLoop)
        print 'writing'
        self.transport.write(self.data)

factory = Factory()
factory.protocol = SineProducer
reactor.listenTCP(22000, factory, interface='127.0.0.1')
reactor.run()
