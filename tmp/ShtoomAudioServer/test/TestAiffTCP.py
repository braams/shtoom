from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import math
import struct
import tempfile

import aifc
audioFile = aifc.open('test.aiff', 'r')
audio = audioFile.readframes(audioFile.getnframes())
class AiffProducer(Protocol):
    def connectionMade(self):
        sh, self.filename = tempfile.mkstemp('.aiff', dir='.')
        print '-> ', self.filename
        self.aiff = aifc.open(self.filename, 'wb')
        self.aiff.setnchannels(1)
        self.aiff.setsampwidth(2)
        self.aiff.setframerate(8000)
        self.transport.write(audio)

    def dataReceived(self, data):
        self.aiff.writeframes(data)

    def connectionLost(self, reason):
        print '<- ', self.filename
        self.aiff.close()

factory = Factory()
factory.protocol = AiffProducer
reactor.listenTCP(22000, factory, interface='127.0.0.1')
reactor.run()
