# Copyright (C) 2004 Anthony Baxter
# $Id: textshtoom.py,v 1.4 2004/02/17 06:29:27 anthony Exp $
#

from twisted.internet import stdio


def shutdown():
    from twisted.internet import reactor
    reactor.stop()

def main(application):
    import sys
    from twisted.internet import reactor
    from twisted.python import log

    from shtoom.ui.textui import ShtoomMain
    UI = ShtoomMain()
    UI.connectApplication(application)
    stdio.StandardIO(UI)
    #log.startLogging(UI.getLogger())
    log.startLogging(sys.stdout)
    return UI

