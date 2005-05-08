def maybeInstallDBus():
    import shtoom.dbus
    if shtoom.dbus.isAvailable():
        try:
            from twisted.internet import glib2reactor
            glib2reactor.install()
        except:
            try:
                from twisted.internet import gtk2reactor
                gtk2reactor.install()
            except:
                shtoom.dbus._setUnavailable()
