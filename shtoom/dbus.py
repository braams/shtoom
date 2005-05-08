try:
    import t_i_dbus as t_i_dbus
    modver = 1
except:
    try:
        import twisted.ipc.dbus as t_i_dbus
        modver = 2
    except:
        t_i_dbus = None

if t_i_dbus is not None:
    if modver == 1:
        from t_i_dbus import *
    elif modver == 2:
        from twisted.ipc.dbus import *

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


if t_i_dbus is None:
    def method(dbus_interface):
        return lambda x: x
    def signal(dbus_interface):
        return lambda x: x
