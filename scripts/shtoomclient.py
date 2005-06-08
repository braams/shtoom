#!/usr/bin/env python
# Hack hack hack.

import sys, os
f = sys.path.pop(0)
if f.endswith('scripts') and os.path.isdir(os.path.join(os.path.dirname(f),
                                                        'shtoom')):
    sys.path.insert(0, os.path.dirname(f))
else:
    sys.path.append(f)


import shtoom.dbus

def gotsignal(*args):
    print "client: got a signal", args

def start(args):
    bus = shtoom.dbus.SessionBus()
    remote_object = bus.get_object("net.shtoom.ShtoomPhone", "/ShtoomPhone")
    #remote_object.connect_to_signal('hello', gotsignal, interface='net.shtoom.ShtoomPhone')
    def cb(result):
        print "shtoomclient: returned", result
        reactor.stop()
    if args[0].startswith('sip:'):
        d = remote_object.call(args[0],
                            dbus_interface = "net.shtoom.ShtoomPhone")
    elif args[0] == 'hangup':
        d = remote_object.hangup(None,
                            dbus_interface = "net.shtoom.ShtoomPhone")
    else:
        print "unknown argument %s"%(args[0])
        reactor.stop()
    d.addCallback(cb)

if __name__ == "__main__":
    import sys
    from twisted.internet import gtk2reactor
    gtk2reactor.install()
    import pygtk
    import gtk

    from twisted.internet import reactor
    reactor.callLater(0, start, sys.argv[1:])
    reactor.run()
