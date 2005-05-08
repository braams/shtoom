# Copyright (C) 2004 Anthony Baxter
# $Id: textshtoom.py,v 1.4 2004/02/17 06:29:27 anthony Exp $
#

from twisted.internet import stdio


def shutdown():
    from twisted.internet import reactor
    reactor.stop()

def main(application):
    import sys

    try:
        import dbus
    except:
        dbus = None
    if dbus:
        try:
            from twisted.internet import glib2reactor
            glib2reactor.install()
        except:
            try:
                from twisted.internet import gtk2reactor
                gtk2reactor.install()
            except:
                pass

    from twisted.internet import reactor
    from __main__ import app

    from shtoom.ui.textui import ShtoomMain
    UI = ShtoomMain()
    UI.connectApplication(application)
    stdio.StandardIO(UI)
    if not app.getPref('logfile'):
        from shtoom import log
        log.startLogging(sys.stdout, setStdout=False)
    return UI
