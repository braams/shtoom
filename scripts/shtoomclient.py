#!/usr/bin/env python

import t_i_dbus

def gotsignal(*args):
    print "client: got a signal", args
    
def start(args):
    bus = t_i_dbus.SessionBus()
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


