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

# For testing purposes
# Force STUN to return the crappiest type of NAT
#import shtoom.stun
#shtoom.stun._ForceStunType = shtoom.stun.NatTypeSymmetric
# Force UPnP to not work
#import shtoom.upnp
#shtoom.upnp.UPNP_PORT = 1901

def main():
    from twisted.internet import defer
    from shtoom.upnp import getUPnP
    from shtoom.stun import getSTUN
    from shtoom.nat import getLocalIPAddress, getMapper
    ud = getUPnP()
    sd = getSTUN()
    ld = getLocalIPAddress()
    md = getMapper()
    dl = defer.DeferredList([ud, sd, ld, md])
    dl.addCallback(gotResults).addErrback(didntGetResults)

def didntGetResults(*res):
    print "FAILED with", res
    return res

def gotResults(natresults):
    from twisted.internet import reactor
    from shtoom.avail import audio, codecs, ui
    from shtoom import __version__
    import platform, twisted.copyright
    (ures, upnp), (sres, stun), (lres,locIP), (mres, mapper) = natresults
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
    print "Available user interfaces:", ', '.join(ui.listUI())
    print "Available codecs:", ', '.join(codecs.listCodecs())
    print "Local IP address:", locIP
    if upnp:
        manuf = upnp.upnpInfo.get('manufacturer', 'unknown')
        model = upnp.upnpInfo.get('friendlyName', 'unknown')
        print "UPnP discovered a %s (%s) device"%(model, manuf)
        print "UPnP controlURL:", upnp.controlURL
    else:
        print "No UPnP-capable device discovered"
    if sres:
        print "STUN says NAT type: %s"%(stun.name)
        if not upnp:
            if stun.blocked:
                print "You will be unable to make calls to the internet"
            elif not stun.useful:
                print "You will need to use an outbound proxy to make calls to the internet"
    else:
        print "STUN was unable to get a result. This is bad"
    print "And the mapper we'd use is: %r"%(mapper)
    reactor.stop()


if __name__ == "__main__":
    from twisted.internet import reactor
    import sys
    from shtoom import log
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        import shtoom.stun
        shtoom.stun.STUNVERBOSE = True
        log.startLogging(sys.stdout)
    reactor.callLater(0, main)
    reactor.run()
