
# Copyright (C) 2004 Anthony Baxter
# $Id: tkshtoom.py,v 1.3 2004/01/10 14:54:53 anthonybaxter Exp $
#


def shutdown():
    try:
        import itimer
        itimer.setitimer(itimer.ITIMER_REAL, 0.0, 0.0)
    except:
        pass
    from twisted.internet import reactor
    reactor.stop()

def main():
    import sys
    from twisted.internet import reactor
    from twisted.python import log
    from twisted.internet import tksupport

    from shtoom.ui.tkui import ShtoomMainWindow
    UI = ShtoomMainWindow()
    tksupport.install(UI.getMain())
    UI.connectSIP()
    log.startLogging(sys.stdout)

    #reactor.addSystemEventTrigger('after', 'shutdown', app.quit )
    #app.connect(app, qt.SIGNAL("lastWindowClosed()"), shutdown)

    reactor.run()

    UI.resourceUsage()

if __name__ == "__main__":
    main()
