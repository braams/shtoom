#
#
# Copyright (c) 1998 Anthony Baxter.
#


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
            if line[1] != '=':
                print "ERROR bad line %s"%(line)
                continue

            if line[0] == 'a':
                subkey, val = line[2:].split(':',1)
                self._a.setdefault(subkey, []).append(val)
            self._d.setdefault(line[0], []).append(line[2:])

        print self._d.keys(), self._a.keys()

    def get(self,typechar,optional=0):
        return self._d.get(typechar)

    def getA(self, subkey):
        return self._a.get(typechar)

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

    def parseM(self,value):
        print "m=", value
        if value:
            audio,port,type,first,last = value[0].split()
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

    def assertSanity(self):
	pass

class SimpleSDP:
    """ a much simpler SDP class. For building announcements for RTSP.
      assumes a single audio stream, given type """
    def __init__(self):
	self.length = None
    def setLength(self,l):
	self.length = l
    def setPacketSize(self,l):
	self.packetsize = l
    def setBitRate(self,l):
	self.bitrate = l
    def setServerIP(self, l):
	self.serverIP = l
    def setLocalPort(self, l):
	self.localPort = l

    def show(self):
	out = []
	out.append("v=0")
	out.append("o=- 0 0 IN IP4 %s"%self.serverIP)
	out.append("s=<No title>")
	out.append("i=<No author> <No copyright>")
	out.append("t=0 0")
	out.append("m=audio %s RTP/AVP 0 97 3"%(self.localPort))
        out.append("c=IN IP4 %s"%(self.serverIP))
	out.append("a=control:streamid=0")
	out.append("a=rtpmap:0 L8/8000/1")
	out.append('a=AvgPacketSize:integer;%d'%self.packetsize)
	out.append('a=MaxPacketSize:integer;%d'%self.packetsize)
	out.append('')
	s = '\n'.join(out)
	return s
	
def ntp2delta(ticks):
    return (ticks - 220898800)
