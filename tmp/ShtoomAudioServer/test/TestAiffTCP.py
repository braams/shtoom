from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import math
import struct

import aifc
audioFile = aifc.open('test.aiff', 'r')
audio = audioFile.readframes(audioFile.getnframes())
class AiffProducer(Protocol):
    def connectionMade(self):
        print self
        self.transport.write(audio)

factory = Factory()
factory.protocol = AiffProducer
reactor.listenTCP(22000, factory, interface='127.0.0.1')
reactor.run()
