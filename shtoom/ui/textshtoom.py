# Copyright (C) 2004 Anthony Baxter
# $Id: textshtoom.py,v 1.2 2004/01/10 14:36:37 anthonybaxter Exp $
#

from twisted.internet import stdio


def shutdown():
    from twisted.internet import reactor
    reactor.stop()

def main():
    import sys
    from twisted.internet import reactor
    from twisted.python import log

    from shtoom.ui.textui import ShtoomMain
    UI = ShtoomMain()
    UI.connectSIP()
    stdio.StandardIO(UI)
    #log.startLogging(UI.getLogger())
    log.startLogging(sys.stdout)
    reactor.run()
    UI.resourceUsage()

if __name__ == "__main__":
    main()
