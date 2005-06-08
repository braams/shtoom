

import dbus, dbus_bindings

if dbus.version != (0,40,0):
    raise ImportError("bad dbus version %r (need (0,40,0))"%(dbus.version,))

from twisted.internet import defer

class Bus(dbus.Bus):

    def get_session():
        """Static method that returns the session bus"""
        return SessionBus()

    get_session = staticmethod(get_session)

    def get_system():
        """Static method that returns the system bus"""
        return SystemBus()

    get_system = staticmethod(get_system)

    def get_starter():
        """Static method that returns the starter bus"""
        return StarterBus()

    get_starter = staticmethod(get_starter)

    def get_object(self, named_service, object_path):
        return ProxyObject(self, named_service, object_path)


class SystemBus(Bus):
    """The system-wide message bus
    """
    def __init__(self):
        Bus.__init__(self, Bus.TYPE_SYSTEM)

class SessionBus(Bus):
    """The session (current login) message bus
    """
    def __init__(self):
        Bus.__init__(self, Bus.TYPE_SESSION)

class StarterBus(Bus):
    """The bus that activated this process (if
    this process was launched by DBus activation)
    """
    def __init__(self):
        Bus.__init__(self, Bus.TYPE_STARTER)

class ProxyObject(dbus.ProxyObject):
    def __getattr__(self, member, **keywords):
        if member == '__call__':
            return object.__call__
        elif member.startswith('__') and member.endswith('__'):
            raise AttributeError(member)
        else:
            iface = None
            if (keywords.has_key('dbus_interface')):
                iface = keywords['dbus_interface']

            return ProxyMethod(self._bus.get_connection(),
                                self._named_service,
                                self._object_path, iface, member)



class ProxyMethod(dbus.ProxyMethod):

    def __call__(self, *args, **keywords):
        from twisted.internet import reactor, gtk2reactor
        if not isinstance(reactor, gtk2reactor.Gtk2Reactor):
            raise RuntimeError("dbus only works with Gtk2Reactor, not %r"%(reactor))
        dbus_interface = self._dbus_interface
        if (keywords.has_key('dbus_interface')):
            dbus_interface = keywords['dbus_interface']

        message = dbus_bindings.MethodCall(self._object_path, dbus_interface,
                                           self._method_name)
        message.set_destination(self._named_service)

        # Add the arguments to the function
        iter = message.get_iter(True)
        for arg in args:
            iter.append(arg)
        d = defer.Deferred()

        result = self._connection.send_with_reply_handlers(message, -1,
                                                           d.callback,
                                                           d.errback)
        return d

# Add any other symbols exported and not overridden
from dbus import Interface, Service, ObjectType, Object, ObjectPath, ByteArray
from dbus import MissingErrorHandlerException, MissingReplyHandlerException
from dbus import ValidationException, UnknownMethodException
from dbus import init_gthreads, method, signal
