"""Gnome interface."""

def shutdown():
    try:
        import itimer
        itimer.setitimer(itimer.ITIMER_REAL, 0.0, 0.0)
    except:
        pass
    from twisted.internet import reactor
    reactor.stop()

def main(application):
    import gnome
    global gnomeProgram
    gnomeProgram = gnome.init("Shtoom", "Whatever Version")

    from twisted.internet import gtk2reactor
    gtk2reactor.install()

    from twisted.python import log
    from shtoom.ui.gnomeui.main import ShtoomWindow
    UI = ShtoomWindow()
    UI.connectApplication(application)
    log.startLogging(UI.getLogger(), setStdout=False)
    return UI
