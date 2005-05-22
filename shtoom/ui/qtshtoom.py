# Copyright (C) 2004 Anthony Baxter
# $Id: qtshtoom.py,v 1.9 2004/03/01 13:44:03 anthony Exp $
#


def main(application):
    import qt
    from twisted.internet import qtreactor
    app=qt.QApplication([])
    qtreactor.install(app)

    import sys
    from twisted.internet import reactor

    from shtoom.ui.qtui import ShtoomMainWindow
    UI = ShtoomMainWindow()
    UI.connectApplication(application)
    UI.show()

    from shtoom import log
    if application.getPref('stdout'):
        import sys
        log.startLogging(sys.stdout, setStdout=False)
    else:
        log.startLogging(UI.getLogger(), setStdout=False)

    reactor.addSystemEventTrigger('after', 'shutdown', app.quit )
    app.connect(app, qt.SIGNAL("lastWindowClosed()"), reactor.stop)

    return UI
