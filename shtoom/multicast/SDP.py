# -*- test-case-name: shtoom.test.test_sdp -*-#
# Copyright (C) 2004 Anthony Baxter
#
rtpPTDict = {
    0: ('PCMU',8000,1),
    3: ('GSM',8000,1),
    4: ('G723',8000,1),
    5: ('DVI4',8000,1),
    6: ('DVI4',16000,1),
    7: ('LPC',8000,1),
    8: ('PCMA',8000,1),
    9: ('G722',8000,1),
    10: ('L16',44100,2),
    11: ('L16',44100,1),
    12: ('QCELP',8000,1),
    13: ('CN',8000,1),
    15: ('G728',8000,1),
    16: ('DVI4',11025,1),
    17: ('DVI4',22050,1),
    18: ('G729',8000,1),
    19: ('xCN',8000,1),
}

# XXX todo - rtpmaps should be ordereddicts or somesuch.

for key,value in rtpPTDict.items():
    rtpPTDict[value] = key
del key,value

BadAnnounce = "Bad Announcement"

class Announcement:
    def __init__(self,text):
        lines = text.split('\n')
        self._d = {}
        self._a = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            elif line[1] != '=':
                raise BadAnnounce,"bad line %s"%(line)
            elif line[0] == 'a':
                subkey, val = line[2:].split(':',1)
                self._a.setdefault(subkey, []).append(val)
            # Handle other subtype entries
            self._d.setdefault(line[0], []).append(line[2:])

    def get(self,typechar,optional=0):
        return self._d.get(typechar)

    def getA(self, subkey):
        return self._a.get(subkey)

class SDP:
    def __init__(self,text=None,sdrcompat=0):
        self._SDRcompat = sdrcompat
        self._id = None
        if text:
            self.text = text
            self.splitText()
            self.assertSanity()
        else:
            # new SDP
            pass

    def name(self):
        return self._sessionName

    def info(self):
        return self._sessionInfo

    def version(self):
        return self._o_version

    def id(self):
        if not self._id:
            self._id = (self._o_username, self._o_sessid, self._o_nettype,
                self._o_addrtype, self._o_addr)
        return self._id

    def splitText(self):
        "split the announcement into fields and handle them"
        ann = Announcement(self.text)
        self._version = ann.get("v")
        self.parseO(ann.get("o"))
        self._sessionName = ann.get("s")
        self._sessionInfo = self.parseI(ann.get("i",optional=1))
        self._uri = ann.get("u",optional=1)
        self._email = ann.get("e",optional=1)
        self._phone = ann.get("p",optional=1)
        # bloody SDR gets e and p in the wrong order.
        if not self._email and self._SDRcompat:
            self._email = ann.get("e",optional=1)
        self._sessionC = self.parseC(ann.get("c",optional=1))
        self._sessionB = self.parseB(ann.get("b",optional=1))
        self._sessionM = self.parseM(ann.get("m",optional=1))
        self._ann = ann
        media = self.get('a', 'rtpmap')
        if media is None:
            self.rtpmap = []
        else:
            self.rtpmap = [(int(x.split()[0]),x) for x in media]

    def get(self, typechar, option=None):
        if option is None:
            return self._ann.get(typechar)
        elif typechar is 'a':
            return self._ann.getA(option)
        else:
            raise ValueError, "only know about suboptions for 'a' so far"

    def parseM(self,value):
        if value:
            els = value[0].split()
            self.media,port,self.transport = els[:3]
            self.formats = [ int(x) for x in els[3:] ]
            self.port = int(port)

    def parseB(self,value):
        pass
    def parseC(self,value):
        pass
    def parseI(self,value):
        if value:
            return value[0]
    def parseO(self,value):
        if value:
            value = value[0]
            l = value.split()
            if len(l) != 6:
                raise BadAnnounce,"wrong # fields in o=`%s'"%value
            ( self._o_username, self._o_sessid, self._o_version,
                self._o_nettype, self._o_addrtype, self._o_addr ) = tuple(l)
            self.ipaddr = self._o_addr

    def assertSanity(self):
        pass

class SimpleSDP:
    """ a much simpler SDP class. For building announcements for RTSP.
      assumes a single audio stream, given type """
    def __init__(self):
        self.serverIP = None
        self.localPort = None
        self.rtpmap = []
        self.packetsize = 160
        self.media = 'audio'
        self.transport = 'RTP/AVP'
    def setMedia(self, media):
        self.media = media
    def setTransport(self, transport):
        self.transport = transport
    def setPacketSize(self,l):
        self.packetsize = l
    def setServerIP(self, l):
        self.serverIP = l
    def setLocalPort(self, l):
        self.localPort = l

    def clearRtpMap(self):
        self.rtpmap = []
    def addRtpMap(self, encname, clockrate, encparams=None, payload=None):
        if self.media == 'audio' and encparams is None:
            # default to a single channel
            encparams = 1
        if self.media != 'audio' and payload is None:
            raise ValueError, "Don't know payloads for %s"%(self.media)
        p = rtpPTDict.get((encname.upper(),clockrate,encparams))
        if payload is None:
            if p is None:
                raise ValueError, "Don't know payload for %s/%s/%s"%(
                    encname.upper(),clockrate,encparams)
            payload = p
        if p is not None and payload != p:
            raise ValueError, "attempt to set payload to %s, should be %s"%(
                                payload, p)
        self.rtpmap.append((payload,"%d %s/%d%s%s"%(
                                          payload, encname, clockrate,
                                          ((encparams and '/') or ""),
                                           encparams or "")))
    def show(self):
        from time import time
        out = []
        out.append("v=0")
        sess = int(time()%1000 * 100)
        out.append("o=root %d %d IN IP4 %s"%(sess, sess, self.serverIP))
        out.append("s=session")
        #out.append("i=<No author> <No copyright>")
        out.append("c=IN IP4 %s"%(self.serverIP))
        out.append("t=0 0")
        payloads = ' '.join([ str(x[0]) for x in self.rtpmap ])
        out.append("m=%s %s %s %s"%(self.media, self.localPort,
                                    self.transport,payloads))
        #out.append("a=control:streamid=0")
        for payload,mapentry in self.rtpmap:
            out.append("a=rtpmap:%s"%(mapentry))
        #out.append('a=AvgPacketSize:integer;%d'%self.packetsize)
        #out.append('a=MaxPacketSize:integer;%d'%self.packetsize)
        out.append('')
        s = '\r\n'.join(out)
        return s

    def intersect(self, other):
        from twisted.python.util import OrderedDict
        map1 = self.rtpmap
        d1 = {}
        for code,e in map1:
            d1[rtpmap2canonical(code,e)] = e
        map2 = other.rtpmap
        outmap = []
        # XXX quadratic - make rtpmap an ordereddict
        for code, e in map2:
            # Damnit. Handle Cisco CN on PT 19!
            if d1.has_key(rtpmap2canonical(code,e)):
                outmap.append((code,e))
        print map1, map2, outmap
        self.rtpmap = outmap

def ntp2delta(ticks):
    return (ticks - 220898800)


def rtpmap2canonical(code, entry):
    if code < 96:
        return code
    else:
        ocode,desc = entry.split(' ',1)
        desc = desc.split('/')
        if len(desc) == 2:
            desc.append('1') # default channels
        name,rate,channels = desc
        return (name.lower(),rate,channels)
