from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import math
import struct
rdev = open('/dev/urandom', 'rb')
class PrintSender(DatagramProtocol):
    def startProtocol(self):
        host, port = "127.0.0.1", 22001
        self.transport.connect(host, port)
        fourhundred = [int(32767 * math.sin(x*(math.pi/10))) for x in range(100)]
        self.data = struct.pack('100h', *fourhundred)
        self.startLoop()

    def startLoop(self):
        reactor.callLater((1.0 / 90.0), self.startLoop)
        self.transport.write(self.data)
    
    def datagramReceived(self, data, (host, port)):
        pass

reactor.listenUDP(22000, PrintSender())
reactor.run()
