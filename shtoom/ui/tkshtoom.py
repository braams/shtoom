
# Copyright (C) 2004 Anthony Baxter
# $Id: tkshtoom.py,v 1.5 2004/03/01 13:15:28 anthony Exp $
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
    from twisted.internet import reactor
    from twisted.python import log
    from twisted.internet import tksupport

    from shtoom.ui.tkui import ShtoomMainWindow
    UI = ShtoomMainWindow()
    tksupport.install(UI.getMain())
    UI.connectApplication(application)
    print "UI done"
    log.startLogging(UI.getLogger())
    return UI



if __name__ == "__main__":
    main()
