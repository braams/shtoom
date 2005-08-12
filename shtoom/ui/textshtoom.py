# Copyright (C) 2004 Anthony Baxter
# $Id: textshtoom.py,v 1.4 2004/02/17 06:29:27 anthony Exp $
#

from twisted.internet import stdio

def shutdown():
    from twisted.internet import reactor
    reactor.stop()

def main(application):
    import sys

    from shtoom.ui.util import maybeInstallDBus
    maybeInstallDBus()

    from twisted.internet import reactor
    from __main__ import app

    from shtoom.ui.textui import ShtoomMain
    UI = ShtoomMain()
    UI.connectApplication(application)
    # see twisted.conch.stdio for an example of readline-y sort of things.
    stdio.StandardIO(UI)
    if not app.getPref('logfile'):
        from shtoom import log
        log.startLogging(sys.stdout, setStdout=False)
    return UI
