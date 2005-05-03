
# Copyright (C) 2004 Anthony Baxter
# $Id: tkshtoom.py,v 1.6 2004/03/01 13:44:03 anthony Exp $
#


def shutdown():
    try:
        import itimer
        itimer.setitimer(itimer.ITIMER_REAL, 0.0, 0.0)
    except:
        pass
    from twisted.internet import reactor
    reactor.stop()

def main(application):
    import sys
    from shtoom.ui.util import maybeInstallDBus
    maybeInstallDBus()

    from twisted.internet import reactor
    from twisted.internet import tksupport

    from shtoom.ui.tkui import ShtoomMainWindow
    UI = ShtoomMainWindow()
    tksupport.install(UI.getMain())
    UI.connectApplication(application)
    from shtoom import log
    log.startLogging(UI.getLogger(), setStdout=False)
    return UI
