#!/usr/bin/env python

# Copyright (C) 2004 Anthony Baxter

# Hack hack hack.
import sys, os
f = sys.path.pop(0)
if f.endswith('scripts') and os.path.isdir(os.path.join(os.path.dirname(f),
                                                        'shtoom')):
    sys.path.insert(0, os.path.dirname(f))
else:
    sys.path.append(f)

def main():
    from twisted.internet import defer
    from shtoom.upnp import getUPnP
    from shtoom.stun import getSTUN
    from shtoom.nat import getLocalIPAddress
    ud = getUPnP()
    sd = getSTUN()
    ld = getLocalIPAddress()
    dl = defer.DeferredList([ud, sd, ld])
    dl.addCallback(gotResults)


def gotResults(natresults):
    from twisted.internet import reactor
    from shtoom.avail import audio, codecs
    from shtoom import __version__
    import platform, twisted.copyright
    (ures, upnp), (sres, stun), (lres,locIP) = natresults
    print "Shtoom, version %s"%(__version__)
    print "Using python version", platform.python_version()
    print "Using twisted version", twisted.copyright.version
    print "Running on", platform.system(), platform.machine(),
    ver = platform.uname()
    if ver[2]:
        print ver[2]
    else:
        ver = platform.win32_ver()
        print ver
    print "Available audio interfaces:", ', '.join(audio.listAudio())
    print "Available codecs:", ', '.join(codecs.listCodecs())
    print "Local IP address:", locIP
    if ures:
        manuf = upnp.upnpInfo.get('manufacturer', 'unknown')
        model = upnp.upnpInfo.get('friendlyName', 'unknown')
        print "UPnP discovered a %s (%s) device"%(model, manuf)
        print "UPnP controlURL:", upnp.controlURL
    else:
        print "No UPnP-capable device discovered"
    if sres:
        print "STUN says NAT type: %s"%(stun.name)
        if not ures:
            if stun.blocked:
                print "You will be unable to make calls to the internet"
            elif not stun.useful:
                print "You will need to use an outbound proxy to make calls to the internet"
    else:
        print "STUN was unable to get a result. This is bad"
    reactor.stop()


if __name__ == "__main__":
    from twisted.internet import reactor
    import sys
    from twisted.python import log
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        log.startLogging(sys.stdout)
    reactor.callLater(0, main)
    reactor.run()
