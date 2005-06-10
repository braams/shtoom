#!/usr/bin/env python

"""
This is a small client program that can be used to manipulate UPnP mappings
on your local UPnP-enabled firewall. It supports list, add and remove
operations.

For instance, if you wanted to expose your sshd to the world,
'upnpclient.py add TCP/22'
would do the trick. Additional options to control things like specifying a
different external port or a different internal IP than the one the client
is running on could be added easily if someone felt the need to do so.
"""

from twisted.internet import reactor, defer
import sys, os
# Hack for running from svn checkout
f = sys.path.pop(0)
if (f.endswith('scripts')
    and os.path.isdir(os.path.join(os.path.dirname(f), 'shtoom'))):
    sys.path.insert(0, os.path.dirname(f))
else:
    sys.path.append(f)

from shtoom.upnp import getUPnP


def usage():
    import sys
    print "Usage: %s command [args]"%(sys.argv[0])
    print "command should be one of:"
    print "\tlist -- show existing mappings"
    print "\tadd proto/port -- add a mapping for proto/port (e.g. udp/5060)"
    print "\tremove proto/port -- remove a mapping for proto/port"

mappingDesc = "%(NewInternalClient)s:%(NewInternalPort)s [%(NewPortMappingDescription)s]"

def gotList(mappings):
    mappings = [ ((x[0][0],int(x[0][1]),x[1])) for x in mappings.items()]
    mappings.sort()
    for prot,port,ddict in mappings:
        desc = mappingDesc%ddict
        print "%s/%d -> %s"%(prot,port,desc)
    reactor.stop()

def doList():
    d = getUPnP()
    d.addCallback(lambda x: x.getPortMappings())
    d.addCallback(gotList)
    d.addErrback(done)

def doneMapping(res):
    reactor.stop()

def gotMappingNowAdd(mappings, nprot, nport, desc):
    if (nprot,nport) in mappings or (nprot,str(nport)) in mappings:
        print "error: can't replace existing mapping for %s/%s"%(nprot,nport)
        ddict = mappings.get((nprot,nport)) or mappings.get((nprot,str(nport)))
        desc = mappingDesc%ddict
        print "existing mapping is to %s"%desc
        reactor.stop()
        sys.exit(1)
    d = getUPnP()
    d.addCallback(lambda x: x.addPortMapping(nport, nport, desc, proto=nprot))
    d.addCallback(doneMapping)

def getSpec(spec):
    prot, port = spec.split('/',2)
    prot = prot.upper()
    if prot not in ('UDP', 'TCP'):
        reactor.stop()
        raise ValueError("protocol should be TCP or UDP, not %s"%prot)
    try:
        port = int(port)
    except ValueError:
        reactor.stop()
        raise ValueError("could understand port %s (should be a number)"%port)
    return prot, port

def doAdd(spec, desc):
    prot, port = getSpec(spec)
    d = getUPnP()
    d.addCallback(lambda x: x.getPortMappings())
    d.addCallback(gotMappingNowAdd, prot, port, desc)
    d.addErrback(done)

def gotMappingNowRemove(mappings, nprot, nport):
    if not ((nprot,nport) in mappings or (nprot,str(nport)) in mappings):
        print "error: no existing mapping for %s/%s"%(nprot,nport)
        reactor.stop()
        sys.exit(1)
    d = getUPnP()
    d.addCallback(lambda x: x.deletePortMapping(nport, proto=nprot))
    d.addCallback(doneMapping)

def doRemove(spec):
    prot, port = getSpec(spec)
    d = getUPnP()
    d.addCallback(lambda x: x.getPortMappings())
    d.addCallback(gotMappingNowRemove, prot, port)
    d.addErrback(done)

def done(x):
    reactor.stop()

def main():
    import sys
    if len(sys.argv) < 2 or sys.argv[1] in ( '--help', '-h', 'help' ):
        usage()
        return
    if sys.argv[1] not in ( 'list', 'add', 'remove' ):
        print "error: command %s not recognised"%(sys.argv[1])
        sys.exit(1)
    cmds = { 'list': doList, 'add': doAdd, 'remove': doRemove }
    reactor.callLater(0, cmds[sys.argv[1]], *sys.argv[2:])
    reactor.run()



if __name__ == "__main__":
    main()
