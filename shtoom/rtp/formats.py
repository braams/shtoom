# Copyright (C) 2004 Anthony Baxter
"This module contains the logic and classes for format negotiation"

class PTMarker:
    "A marker of a particular payload type"
    media = None

    def __init__(self, name, pt=None, clock=8000, params=1):
        self.name = name
        self.pt = pt
        self.clock = clock
        self.params = params

    def __repr__(self):
        if self.pt is None:
            pt = 'dynamic'
        else:
            pt = str(self.pt)
        cname = self.__class__.__name__
        return "<%s %s(%s)/%s/%s at %x>"%(cname, self.name, pt, 
                                          self.clock, self.params, id(self))

class AudioPTMarker(PTMarker):
    "An audio payload type"
    media = 'audio'

class VideoPTMarker(PTMarker):
    "A video payload type"
    media = 'video'

PT_PCMU =       AudioPTMarker('PCMU',  clock=8000,  params=1, pt=0)
PT_GSM =        AudioPTMarker('GSM',   clock=8000,  params=1, pt=3)
PT_G723 =       AudioPTMarker('G723',  clock=8000,  params=1, pt=4)
PT_DVI4 =       AudioPTMarker('DVI4',  clock=8000,  params=1, pt=5)
PT_DVI4_16K =   AudioPTMarker('DVI4',  clock=16000, params=1, pt=6)
PT_LPC =        AudioPTMarker('LPC',   clock=8000,  params=1, pt=7)
PT_PCMA =       AudioPTMarker('PCMA',  clock=8000,  params=1, pt=8)
PT_G722 =       AudioPTMarker('G722',  clock=8000,  params=1, pt=9)
PT_L16_STEREO = AudioPTMarker('L16',   clock=44100, params=2, pt=10)
PT_L16 =        AudioPTMarker('L16',   clock=44100, params=1, pt=11)
PT_QCELP =      AudioPTMarker('QCELP', clock=8000,  params=1, pt=12)
PT_CN =         AudioPTMarker('CN',    clock=8000,  params=1, pt=13)
PT_G728 =       AudioPTMarker('G728',  clock=8000,  params=1, pt=15)
PT_DVI4_11K =   AudioPTMarker('DVI4',  clock=11025, params=1, pt=16)
PT_DVI4_22K =   AudioPTMarker('DVI4',  clock=22050, params=1, pt=17)
PT_G729 =       AudioPTMarker('G729',  clock=8000,  params=1, pt=18)
PT_xCN =        AudioPTMarker('xCN',   clock=8000,  params=1, pt=19)
PT_SPEEX =      AudioPTMarker('speex', clock=8000,  params=1)
PT_SPEEX_16K =  AudioPTMarker('speex', clock=16000,  params=1)
PT_NTE =        PTMarker('telephone-event', clock=8000, params=None)
PT_RAW =        AudioPTMarker('RAW_L16', clock=8000, params=1)

# ...


class SDPGenerator:
    "Responsible for generating SDP for the RTPProtocol"

    def getSDP(self, rtp, extrartp=None):
        from shtoom.sdp import SDP, MediaDescription
        from shtoom.avail import gsm, speex, dvi4
        if extrartp:
            raise ValueError("can't handle multiple RTP streams in a call yet")
        s = SDP()
        addr = rtp.getVisibleAddress()
        s.setServerIP(addr[0])
        md = MediaDescription() # defaults to type 'audio'
        s.addMediaDescription(md)
        md.setServerIP(addr[0])
        md.setLocalPort(addr[1])
        if gsm is not None:
            md.addRtpMap(PT_GSM)
        md.addRtpMap(PT_PCMU)
        if speex is not None:
            md.addRtpMap(PT_SPEEX)
            #md.addRtpMap(PT_SPEEX_16K)
        if dvi4 is not None:
            md.addRtpMap(PT_DVI4)
            #s.addRtpMap(PT_DVI4_16K)
        md.addRtpMap(PT_CN)
        md.addRtpMap(PT_NTE)
        return s

RTPDict = {}
all = globals()
for key,val in all.items():
    if isinstance(val, PTMarker):
        # By name
        RTPDict[key] = val
        # By object
        if val.pt is not None:
            RTPDict[val] = val.pt
        # By PT
        if val.pt is not None:
            RTPDict[val.pt] = val
        # By name/clock/param
        RTPDict[(val.name.lower(),val.clock,val.params or 1)] = val

del all, key, val

