# Copyright (C) 2004 Anthony Baxter

import baseaudio
import traceback
from twisted.python import log
from twisted.internet.protocol import Protocol, Factory

SHTOOM_PORT = 22000

factory = None

class TCPAudioProtocol(Protocol):
    def connectionMade(self):
        log.msg("TCPAudioProtocol.connectionMade")
        self.factory.device.connection = self
        self.readbuffer = ''

    def dataReceived(self, data):
        if self.readbuffer is not None:
            self.readbuffer += data

    def write(self, data):
        self.transport.write(data)

    def open(self):
        self.readbuffer = ''

    def _close(self):
        self.readbuffer = None

    def read(self, bytes=None):
        if bytes is None:
            bytes = len(self.readbuffer)
        rval, self.readbuffer = self.readbuffer[:bytes], self.readbuffer[bytes:]
        return rval


class TCPAudioFactory(Factory):
    protocol = TCPAudioProtocol


class TCPAudioDevice(baseaudio.AudioDevice):

    def __init__(self, port=SHTOOM_PORT):
        self.connection = None
        self.factory = factory = TCPAudioFactory()
        factory.device = self
        from twisted.internet import reactor
        self.connector = reactor.listenTCP(port, factory, interface='127.0.0.1')

    def openDev(self, port=SHTOOM_PORT):
        log.msg("TCPAudioDevice opening")
        if self.connection is not None:
            self.connection.open()

    def read(self):
#        print 'read'
        if self.connection is None:
            log.msg("read: no connection yet")
            return ''
        return self.connection.read(320)

    def write(self, data):
#        print 'write'
        if self.connection is None:
            log.msg("write: no connection yet")
        else:
            self.connection.write(data)

    def close(self):
        log.msg("TCPAudioProtocol closing")
        if self.connection is not None:
            self.connection.close()
        #self.connector.disconnect()

    def selectDefaultFormat(self, ptlist):
        #print 'ptlist = ', ptlist
        pass

Device = TCPAudioDevice
