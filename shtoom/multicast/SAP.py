#
#
# Copyright (c) 2004 Anthony Baxter.
#

class SAP:
    def __init__(self,pack):
        self.dismantlePacket(pack)

    # in a perfect world, there'd be a much nicer parser for this...
    def dismantlePacket(self,pack):
        import struct
        misc,self.authlen,self.hash,self.source = \
                                        struct.unpack("!bbHI",pack[:8])
        self._miscHeaders(misc)
        endauth = 8+self.authlen
        self.auth = pack[8:endauth]
        endauth = endauth + self._encryptHeaders(pack,endauth,self.e)
        self.text = pack[endauth:]

    def _miscHeaders(self,misc):
        self.v  = (misc & 0xe0) >> 5
        self.mt = (misc & 0x1c) >> 2
        self.e =  (misc & 0x02) >> 1
        self.c =  (misc & 0x01)

    def _encryptHeaders(self,pack,offset,e):
        import struct
        if e:
            self.key,self.timeout,prand = struct.unpack("!III",
                                                pack[offset:offset+3])
            self.p = (prand & (1<<31))>>31
            self.rand = int(prand ^ (1<<31))
            return 3
        else:
            self.key,self.timeout,self.p,self.rand = 0,0,0,0
            return 0

    def SDP(self,sdrcompat=0):
        from Multicast.SDP import SDP
        if self.e:
            self.decrypt()
        if self.c:
            self.decompress()
        return SDP(self.text,sdrcompat)

    def decrypt(self):
        raise "sorry","Don't know how to handle decryption"

    def decompress(self):
        raise "sorry","Don't know how to handle decompression"


SAPADDR = ["sap.mcast.net", "224.2.127.255"]
SCOPES = [ ( "local" , ("239.255",16) ),
           ( "admin" , ("239.192",14) ),
           ( "regional" , None ),
           ( "global" , None ) ]

SAPPORT = 9875

def ntp2delta(ticks):
    return (ticks - 220898800)
