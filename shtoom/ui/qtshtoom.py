# Copyright (C) 2004 Anthony Baxter
# $Id: qtshtoom.py,v 1.6 2004/01/10 14:36:37 anthonybaxter Exp $
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
    import qt
    from twisted.internet import qtreactor
    app=qt.QApplication([])
    qtreactor.install(app)

    import sys
    from twisted.internet import reactor
    from twisted.python import log

    from shtoom.ui.qtui import ShtoomMainWindow
    UI = ShtoomMainWindow()
    UI.connectSIP()
    UI.show()
    log.startLogging(UI.getLogger())
    #log.startLogging(sys.stdout)
    
    reactor.addSystemEventTrigger('after', 'shutdown', app.quit )
    app.connect(app, qt.SIGNAL("lastWindowClosed()"), shutdown)

    reactor.run()

    UI.resourceUsage()

if __name__ == "__main__":
    main()
