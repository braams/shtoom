

import dbus
if not hasattr(dbus, 'version'):
    from t_i_dbus_023 import *
    DBUS_API = (0,23,0)
elif dbus.version == (0,40,0):
    from t_i_dbus_033 import *
    DBUS_API = dbus.version
else:
    raise ImportError("bad dbus version %r (need (0,40,0))"%(dbus.version,))
