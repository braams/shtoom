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

if t_i_dbus is None:
    def method(dbus_interface):
        return lambda x: x
    def signal(dbus_interface):
        return lambda x: x

