from twisted.internet import reactor, defer
from twisted.internet.protocol import DatagramProtocol
from twisted.python import log
import struct, sys, StringIO

TftpOpcodes = {
    0x0001: 'RRQ',
    0x0002: 'WRQ',
    0x0003: 'DATA',
    0x0004: 'ACK',
    0x0005: 'ERROR',
}

class TftpError(Exception): pass
class UnknownTftpError(TftpError): pass
class NoSuchFileTftpError(TftpError): pass
class PermissionTftpError(TftpError): pass
class SpaceTftpError(TftpError): pass
class IllegalOpTftpError(TftpError): pass
class UnknownTIDTftpError(TftpError): pass
class FileExistsTftpError(TftpError): pass
class NoSuchUserTftpError(TftpError): pass


TftpErrors = {
    0: UnknownTftpError,
    1: NoSuchFileTftpError,
    2: PermissionTftpError,
    3: SpaceTftpError,
    4: IllegalOpTftpError,
    5: UnknownTIDTftpError,
    6: FileExistsTftpError,
    7: NoSuchUserTftpError,
}


for k,v in TftpOpcodes.items():
    TftpOpcodes[v] = k
del k, v

print TftpOpcodes
print TftpOpcodes[3]

class TftpProtocol(DatagramProtocol, object):


    fp = None

    def datagramReceived(self, dgram, address):
        opcode, = struct.unpack('!h', dgram[:2])
        opcode = TftpOpcodes.get(opcode,'UNKNOWN(%d)'%opcode)
        rhost,rport = address
        print "got opcode %s from %s:%s"%(opcode, rhost, rport)
        if opcode == 'DATA':
            block, = struct.unpack('!h', dgram[2:4])
            if block != self.blockcount:
                print "error, expecting block %d, got %d"%(self.blockcount,block)
                return
            else:
                data = dgram[4:]
                self.fp.write(data)
                self.transport.write(
                    struct.pack('!hh', TftpOpcodes['ACK'], self.blockcount),
                    (rhost, rport))
                if data:
                    self.fp.write(data)
                if len(data) != 512:
                    # We're done.
                    self.fp.close()
                    self.retdef.callback(self.fp)
                else:
                    self.blockcount += 1
        elif opcode == 'ERROR':
            code, = struct.unpack('!h', dgram[2:4])
            msg = dgram[4:-1]
            self.transport.write(
                struct.pack('!hh', TftpOpcodes['ACK'], self.blockcount),
                (rhost, rport))
            e = TftpErrors.get(code, UnknownTftpError)
            self.retdef.errback(e(msg))

    def fetch(self, remfile, fp=None):
        if fp is not None:
            self.fp = fp
        else:
            self.fp = StringIO.StringIO()
        remhost, rempath = remfile.split(':',1)
        resdef = reactor.resolve(remhost)
        self.retdef = defer.Deferred()
        resdef.addCallbacks(lambda x: self._sendRRQ(x,rempath),
                            self.retdef.errback)
        return self.retdef

    def _sendRRQ(self, remotehost, remotefile):
        self.remotehost = remotehost
        self.blockcount = 1
        dgram = struct.pack('!h', TftpOpcodes['RRQ'])+remotefile+'\0'+'octet\0'
        self.transport.write(dgram, (remotehost, 69))

def testdone(r):
    print "test done, got", r
    reactor.stop()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: %s host:path/to/file outfile"
        sys.exit(0)
    tftpClient = TftpProtocol()
    log.startLogging(sys.stdout)
    reactor.listenUDP(0, tftpClient)
    fp = open(sys.argv[2], 'w')
    retdef = tftpClient.fetch(sys.argv[1], fp)
    retdef.addCallbacks(testdone, log.msg)
    reactor.run()
