# Copyright (C) 2004 Anthony Baxter
# $Id: qtshtoom.py,v 1.9 2004/03/01 13:44:03 anthony Exp $
#


def shutdown():

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
    log.startLogging(UI.getLogger(), setStdout=False)
    #log.startLogging(sys.stdout)

    reactor.addSystemEventTrigger('after', 'shutdown', app.quit )
    app.connect(app, qt.SIGNAL("lastWindowClosed()"), reactor.stop)

    return UI

if __name__ == "__main__":
    main()
