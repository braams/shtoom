# Copyright (C) 2004 Anthony Baxter
# $Id: qtshtoom.py,v 1.8 2004/01/14 14:44:54 anthonybaxter Exp $
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
    import qt
    from twisted.internet import qtreactor
    app=qt.QApplication([])
    qtreactor.install(app)

    import sys
    from twisted.internet import reactor
    from twisted.python import log

    from shtoom.ui.qtui import ShtoomMainWindow
    UI = ShtoomMainWindow()
    UI.connectApplication(application)
    UI.show()
    log.startLogging(UI.getLogger())
    #log.startLogging(sys.stdout)

    reactor.addSystemEventTrigger('after', 'shutdown', app.quit )
    app.connect(app, qt.SIGNAL("lastWindowClosed()"), shutdown)

    return UI

if __name__ == "__main__":
    main()
