# b/w compat for old old code that vendors shift

import dbus, dbus_bindings


class Bus(dbus.Bus):

    TYPE_SESSION    = dbus_bindings.BUS_SESSION
    TYPE_SYSTEM     = dbus_bindings.BUS_SYSTEM
    TYPE_ACTIVATION = dbus_bindings.BUS_ACTIVATION


    def __init__(self, bus_type=TYPE_SESSION, glib_mainloop=True):
        self._connection = dbus_bindings.bus_get(bus_type)

        self._connection.add_filter(self._signal_func)
        self._match_rule_to_receivers = {}
        if (glib_mainloop):
            self._connection.setup_with_g_main()

    def get_service(self, service_name="org.freedesktop.Broadcast"):
        """Get one of the RemoteServices connected to this Bus. service_name
        is just a string of the form 'com.widgetcorp.MyService'
        """
        return RemoteService(self, service_name)
    def get_object(self, named_service, object_path):
        return RemoteService(self, named_service).get_object(object_path)

    # Aaaargh. All this is needed because to get the service name (like :1.20)
    # you need to ask the dbus daemon for the name, which is an async operation.

    def add_signal_receiver(self, handler_function, signal_name=None, interface=None, service=None, path=None):
        d = self._get_match_rule(signal_name, interface, service, path)
        d.addCallback(lambda x, h=handler_function:
                                self._cb_add_signal_receiver(x, h))

    def _cb_add_signal_receiver(self, match_rule, handler_function):
        receivers = self._match_rule_to_receivers.setdefault(match_rule, [])
        self._match_rule_to_receivers[match_rule].append(handler_function)
        dbus_bindings.bus_add_match(self._connection, match_rule)

    def remove_signal_receiver(self, handler_function, signal_name=None, interface=None, service=None, path=None):
        d = self._get_match_rule(signal_name, interface, service, path)
        d.addCallback(lambda x, h=handler_function:
                                self._cb_add_signal_receiver(x, h))

    def _cb_remove_signal_receiver(self, match_rule, handler_function):
        receivers =  self._match_rule_to_receivers.get(match_rule)
        if receivers:
            if handler_function in receivers:
                receivers.remove(handler_function)
                # if there's none left, remove the binding
                if not receivers:
                    dbus_bindings.bus_remove_match(self._connection,match_rule)

    def _get_match_rule(self, signal_name, interface, service, path):
        from twisted.internet import defer
        match_rule = "type='signal'"
        match_rule2 = ''
        if (interface):
            match_rule = match_rule + ",interface='%s'" % (interface)
        if (path):
            match_rule2 += ",path='%s'" % (path)
        if (signal_name):
            match_rule2 += ",member='%s'" % (signal_name)
        if (service):
            if (service[0] != ':' and service != "org.freedesktop.DBus"):
                bus_service = self.get_service("org.freedesktop.DBus")
                bus_object = bus_service.get_object('/org/freedesktop/DBus',
                                                     'org.freedesktop.DBus')
                d = bus_object.GetServiceOwner(service)
                d.addCallback(lambda x, m=match_rule, m2=match_rule2:
                        m + (",sender='%s'"%(x)) + m2)
                return d
            else:
                match_rule += ",sender='%s'"%(service)
                match_rule += match_rule2
        return defer.succeed(match_rule)

    def _signal_func(self, connection, message):
        if (message.get_type() != dbus_bindings.MESSAGE_TYPE_SIGNAL):
            return dbus_bindings.HANDLER_RESULT_NOT_YET_HANDLED

        interface = message.get_interface()
        service   = message.get_sender()
        path      = message.get_path()
        member    = message.get_member()
        args = [interface, member, service, path, message]
        d = self._get_match_rule(member, interface, service, path)
        d.addCallback(lambda x, a=args: self._cb_signal_func(x, a))

    def _cb_signal_func(self, match_rule, args):
        if (self._match_rule_to_receivers.has_key(match_rule)):
            receivers = self._match_rule_to_receivers[match_rule]
            for receiver in receivers:
                receiver(*args)



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

class ActivationBus(Bus):
    """The bus that activated this process (if
    this process was launched by DBus activation)
    """
    def __init__(self):
        Bus.__init__(self, Bus.TYPE_ACTIVATION)




class RemoteService(dbus.RemoteService):
    def get_object(self, object_path, interface=None):
        return ProxyObject(self, object_path, interface)

class ProxyObject(dbus.RemoteObject):
    def connect_to_signal(self,
                          signal_name,
                          handler_function,
                          interface=None):
        if interface is None and self._interface is not None:
            interface = self._interface
        # XXX should error if no self._interface and no interface
        bus = self._service.get_bus()
        service = self._service.get_service_name()
        bus.add_signal_receiver(handler_function,
                                signal_name=signal_name,
                                interface=interface,
                                service=service,
                                path=self._object_path)

    def __getattr__(self, member):
        if member == '__call__':
            return object.__call__
        elif member.startswith('__') and member.endswith('__'):
            raise AttributeError(member)
        else:
            return ProxyMethod(self._service.get_bus().get_connection(),
                                self._service.get_service_name(),
                                self._object_path, self._interface, member)

class ProxyMethod(dbus.RemoteMethod):
    def __call__(self, *args, **keywords):
        from twisted.internet import reactor, gtk2reactor
        if not isinstance(reactor, gtk2reactor.Gtk2Reactor):
            raise RuntimeError("dbus only works with Gtk2Reactor, not %r"%(reactor))
        dbus_interface = self._interface
        if (keywords.has_key('dbus_interface')):
            dbus_interface = keywords['dbus_interface']

        message = dbus_bindings.MethodCall(self._object_path, dbus_interface,
                                           self._method_name)
        message.set_destination(self._service_name)

        # Add the arguments to the function
        iter = message.get_iter()
        for arg in args:
            iter.append(arg)

        retval, pc = self._connection.send_with_reply(message, 5000)
        # goddam the old API is uuugly
        return _PendingCall(pc).deferred

class _PendingCall:
    def __init__(self, pc):
        from twisted.internet import defer, task
        self.deferred = defer.Deferred()
        self.pc = pc
        self.lc = task.LoopingCall(self._checkPC)
        self.lc.start(0.020)

    def _checkPC(self):
        try:
            if self.deferred is None:
                # twisted bug
                return
            if not self.pc.get_completed():
                return
            self.lc.stop()
            d, self.deferred = self.deferred, None
            pc, self.pc = self.pc, None
            reply = pc.get_reply().get_args_list()
            if len(reply) == 0:
                ret = None
            elif len(reply) == 1:
                ret = reply[0]
            else:
                ret = reply
            d.callback(ret)

        except:
            import sys
            e,v,t = sys.exc_info()

import dbus_bindings, inspect

def method(iface):
    def decorator(func, iface=iface):
        func._dbus_is_method = True
        func._dbus_interface = iface
        return func
    return decorator

class Object(dbus.Object):
    def __init__(self, object_path, service, dbus_methods=[]):
        dbus.Object.__init__(self, object_path, service, dbus_methods)
        for methodname, method in self.__class__.__dict__.items():
            if methodname.startswith('_'):
                continue
            if hasattr(method, '_dbus_is_method'):
                self._method_name_to_method[methodname] = getattr(self, methodname)

    def _message_cb(self, connection, message):
        target_method_name = message.get_member()
        target_method = self._method_name_to_method[target_method_name]
        args = message.get_args_list()
        reply = _dispatch_dbus_method_call(target_method, args, message)
        self._connection.send(reply)

def _dispatch_dbus_method_call(target_method, argument_list, message):
    """Calls method_to_call using argument_list, but handles
    exceptions, etc, and generates a reply to the DBus Message message
    """
    try:
        retval = target_method(*argument_list)
    except Exception, e:
        if e.__module__ == '__main__':
            # FIXME: is it right to use .__name__ here?
            error_name = e.__class__.__name__
        else:
            error_name = e.__module__ + '.' + str(e.__class__.__name__)
            error_contents = str(e)
            reply = dbus_bindings.Error(message, error_name, error_contents)
    else:
        reply = dbus_bindings.MethodReturn(message)
        if retval != None:
            iter = reply.get_iter()
            iter.append(retval)
    return reply



from dbus import Service
