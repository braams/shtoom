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
    from twisted.internet import gtk2reactor
    gtk2reactor.install()

    import sys
    from twisted.internet import reactor
    from twisted.python import log

    from shtoom.ui.gnomeui.main import ShtoomWindow
    UI = ShtoomWindow()
    UI.connectApplication(application)
    return UI


if __name__ == "__main__":
    main()
