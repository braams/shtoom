# -*- test-case-name: shtoom.test.test_new_sdp -*-#
# Copyright (C) 2004 Anthony Baxter
# Copyright (C) 2004 Jamey Hicks
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

def get(obj,typechar,optional=0):
    return obj._d.get(typechar)

def getA(obj, subkey):
    return obj._a.get(subkey)

def parse_generic(obj, k, text):
    obj._d.setdefault(k, []).append(text)

def unparse_generic(obj, k):
    if obj._d.has_key(k):
        return obj._d[k]
    else:
        return []

def parse_singleton(obj, k, text):
    obj._d[k] = text

def unparse_singleton(obj, k):
    if obj._d.has_key(k):
        return [obj._d[k]]
    else:
        return []

def parse_o(obj, o, value):
    if value:
        l = value.split()
        if len(l) != 6:
            raise BadAnnounce,"wrong # fields in o=`%s'"%value
        ( obj._o_username, obj._o_sessid, obj._o_version,
            obj._o_nettype, obj._o_addrfamily, obj._o_ipaddr ) = tuple(l)

def unparse_o(obj, o):
    return ['%s %s %s %s %s %s' % ( obj._o_username, obj._o_sessid, obj._o_version,
                                    obj._o_nettype, obj._o_addrfamily, obj._o_ipaddr )]

def parse_a(obj, a, text):
    words = text.split(':')
    if len(words) > 1:
        attr, attrvalue = words
    else:
        attr, attrvalue = text, None
    obj._a.setdefault(attr, []).append(attrvalue)
    if attr == 'rtpmap':
        payload,info = attrvalue.split(' ')
        obj.rtpmap.append((int(payload),attrvalue))
        
def unparse_a(obj, k):
    out = []
    for (a,vs) in obj._a.items():
        for v in vs:
            if v:
                out.append('%s:%s' % (a, v))
            else:
                out.append(a)
    return out

def parse_c(obj, c, text):
    words = text.split(' ')
    (obj.nettype, obj.addrfamily, obj.ipaddr) = words

def unparse_c(obj, c):
    return ['%s %s %s' % (obj.nettype, obj.addrfamily, obj.ipaddr)]

def parse_m(obj, m, value):
    if value:
        els = value.split()
        (obj.media, port, obj.transport) = els[:3]
        obj.formats = els[3:]
        obj.port = int(port)

def unparse_m(obj, m):
    return ['%s %s %s %s' % (obj.media, str(obj.port), obj.transport, ' '.join(obj.formats))]

parsers = [
    ('v', 1, parse_singleton, unparse_singleton),
    ('o', 1, parse_o, unparse_o),
    ('s', 1, parse_singleton, unparse_singleton),
    ('i', 0, parse_generic, unparse_generic),
    ('u', 0, parse_generic, unparse_generic),
    ('e', 0, parse_generic, unparse_generic),
    ('p', 0, parse_generic, unparse_generic),
    ('c', 0, parse_c, unparse_c),
    ('b', 0, parse_generic, unparse_generic),
    ('t', 0, parse_singleton, unparse_singleton),
    ('r', 0, parse_generic, unparse_generic),
    ('k', 0, parse_generic, unparse_generic),
    ('a', 0, parse_a, unparse_a)
    ]

mdparsers = [
    ('m', 0, parse_m, unparse_m),
    ('i', 0, parse_generic, unparse_generic),
    ('c', 0, parse_generic, unparse_generic),
    ('b', 0, parse_generic, unparse_generic),
    ('k', 0, parse_generic, unparse_generic),
    ('a', 0, parse_a, unparse_a)
]

parser = {}
unparser = {}
mdparser = {}
mdunparser = {}
for (key, required, parseFcn, unparseFcn) in parsers:
    parser[key] = parseFcn
    unparser[key] = unparseFcn
for (key, required, parseFcn, unparseFcn) in mdparsers:
    mdparser[key] = parseFcn
    mdunparser[key] = unparseFcn
del key,required,parseFcn,unparseFcn

class MediaDescription:
    def __init__(self, text=None):
        self.media = None
        self.nettype = 'IN'
        self.addrfamily = 'IP4'
        self.ipaddr = None
        self.port = None
        self.transport = None
        self.formats = []
        self._d = {}
        self._a = {}
        self.rtpmap = []
        self.media = 'audio'
        self.transport = 'RTP/AVP'
        self.keyManagement = None
        if text:
            parse_m(self, 'm', text)
   
    def setMedia(self, media):
        self.media = media
    def setTransport(self, transport):
        self.transport = transport
    def setServerIP(self, l):
        self.ipaddr = l
    def setLocalPort(self, l):
        self.port = l

    def setKeyManagement(self, km):
        parse_a('keymgmt', keyManagement)

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
        rtpmap = "%d %s/%d%s%s"%(payload, encname, clockrate,
                                 ((encparams and '/') or ""),
                                 encparams or "")
        self.rtpmap.append((int(payload),rtpmap))
        self._a.setdefault('rtpmap', []).append(rtpmap)
        self.formats.append(str(payload))

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
            if d1.has_key(rtpmap2canonical(code,e)):
                outmap.append((code,e))
        self.rtpmap = outmap
        self._a['rtpmap'] = [ e for (code, e) in outmap ]

class SDP:
    def __init__(self,text=None):
        from time import time
        self._id = None
        self._d = {'v': '0', 't': '0 0', 's': 'shtoom'}
        self._a = {}
        self.mediaDescriptions = []
        self._o_username = 'root'
        self._o_sessid = self._o_version = str(int(time()%1000 * 100))
        self._o_nettype = self.nettype = 'IN'
        self._o_addrfamily = self.addrfamily = 'IP4'
        self._o_ipaddr = self.ipaddr = None
        self.port = None
        if text:
            self.parse(text)
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
            self._id = (self._o_username, self._o_sessid, self.nettype, self.addrfamily, self.ipaddr)
        return self._id

    def parse(self, text):
        lines = text.split('\r\n')
        md = None
        for line in lines:
            elts = line.split('=')
            if len(elts) != 2:
                continue
            (k,v) = elts
            if k == 'm':
                md = MediaDescription(v)
                self.mediaDescriptions.append(md)
            elif md:
                mdparser[k](md, k, v)
            else:
                parser[k](self, k, v)

    def get(self, typechar, option=None):
        if option is None:
            return self._ann.get(typechar)
        elif typechar is 'a':
            return self._ann.getA(option)
        else:
            raise ValueError, "only know about suboptions for 'a' so far"

    def setServerIP(self, l):
        self._o_ipaddr = self.ipaddr = l

    def addMediaDescription(self, md):
        self.mediaDescriptions.append(md)
    def removeMediaDescription(self, md):
        self.mediaDescriptions.remove(md)
    def getMediaDescription(self, media):
        for md in self.mediaDescriptions:
            if md.media == media:
                return md
        return None
    def hasMediaDescriptions(self):
        return len(self.mediaDescriptions)

    def show(self):
        out = []
        for (k, req, p, u) in parsers:
            for l in u(self, k):
                out.append('%s=%s' % (k, l))
        for md in self.mediaDescriptions:
            for (k, req, p, u) in mdparsers:
                for l in u(md, k):
                    out.append('%s=%s' % (k, l))
        out.append('')
        s = '\r\n'.join(out)
        return s

    def intersect(self, other):
        mds = self.mediaDescriptions
        self.mediaDescriptions = []
        for md in mds:
            omd = None
            for o in other.mediaDescriptions:
                if md.media == o.media:
                    omd = o
                    break
            if omd:
                md.intersect(omd)
                self.mediaDescriptions.append(md)

    def assertSanity(self):
        pass

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
