"""Gnome interface."""

def shutdown():
    from twisted.internet import reactor
    reactor.stop()

def main(application):
    import gnome
    global gnomeProgram
    gnomeProgram = gnome.init("Shtoom", "Whatever Version")

    from twisted.internet import gtk2reactor
    gtk2reactor.install()

    from shtoom.ui.gnomeui.main import ShtoomWindow

    UI = ShtoomWindow()
    UI.connectApplication(application)

    from shtoom import log
    if application.getPref('stdout'):
        import sys
        log.startLogging(sys.stdout, setStdout=False)
    else:
        log.startLogging(UI.getLogger(), setStdout=False)

    return UI
