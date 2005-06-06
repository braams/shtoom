try:
    import twisted.ipc.dbus as t_i_dbus
    from twisted.ipc.dbus import *
except:
    try:
        import t_i_dbus
        from t_i_dbus import *
    except:
        try:
            from shtoom.compat.t_i_dbus import *
            from shtoom.compat import t_i_dbus
        except:
            t_i_dbus = None

def isAvailable():
    return t_i_dbus is not None

def _setUnavailable():
    # We're not running under the gtk or glib reactors, so kill the dbus
    # support
    global t_i_dbus, method, signal
    t_i_dbus = None
    def method(dbus_interface):
        return lambda x: x
    def signal(dbus_interface):
        return lambda x: x

def installDbusReactor():
    try:
        from twisted.internet import glib2reactor
        glib2reactor.install()
        return True
    except:
        try:
            from twisted.internet import gtk2reactor
            gtk2reactor.install()
            return True
        except:
            return False



if t_i_dbus is None:
    def method(dbus_interface):
        return lambda x: x
    def signal(dbus_interface):
        return lambda x: x
