import sys, inspect, sets


_nope = object()


class AdaptationError(TypeError):
    pass


class MetaInterface(type):
    def __call__(self, other, default=_nope):
        return adapt(other, self, default)


class Interface(object):
    __metaclass__ = MetaInterface


class IAdapterRegistry(Interface):
    pass


class AdapterRegistry(object):
    def __init__(self):
        self.registry = {}
        self.implementedByCache = {}

    def registerAdapter(self, adapter, original, interface, overwrite=False):
        registry = self.registry
        if not overwrite:
            assert (interface, original) not in registry
        registry[(interface, original)] = adapter

    def getAdapter(self, interface, other, default=_nope):
        registry = self.registry
        adapterFactory = registry.get((interface, type(other)), _nope)
        if adapterFactory is not _nope:
            return adapterFactory(other)
        for otherInterface in implementedBy(other):
            adapterFactory = registry.get((interface, otherInterface), _nope)
            if adapterFactory is not _nope:
                return adapterFactory(other)
        if default is not _nope:
            return default
        raise AdaptationError("Cannot adapt %r to %r." % (other, self))

    def declareImplements(self, cls, interface):
        """Declare that a class implements an interface,
        without using frame hacks. Useful for declaring that
        built-in types declare interfaces.
        """
        self.implementedByCache[cls] = self.implementedByCache.get(cls, ()) + (interface, )

    def implementedBy(self, other):
        return self.providedBy(type(other))


    def providedBy(self, cls):
        cached = self.implementedByCache.get(cls)
        if cached is not None:
            return cached
        implements = sets.Set()
        for cls in inspect.getmro(cls):
            impl = cls.__dict__.get('__implements__')
            if impl is not None:
                implements.update(impl)

        cacheable = list(implements)
        self.implementedByCache[cls] = cacheable
        return cacheable


theRegistry = AdapterRegistry()


try:
    from twisted.python import context
except ImportError:
    def checkContext(callable):
        return callable
else:
    def checkContext(callable):
        def decorate(*args, **kw):
            registry = context.get(IAdapterRegistry)
            if registry is not None:
                return getattr(registry, callable.__name__)(*args, **kw)
            return callable(*args, **kw)
        return decorate


getAdapter = checkContext(theRegistry.getAdapter)
registerAdapter = checkContext(theRegistry.registerAdapter)
declareImplements = checkContext(theRegistry.declareImplements)
implementedBy = checkContext(theRegistry.implementedBy)
providedBy = checkContext(theRegistry.providedBy)


def adapt(obj, protocol, default=_nope):
    ## First case: other implements self directly
    if protocol in implementedBy(obj):
        return obj

    ## Second case: other knows how to make itself implement self
    conform = getattr(obj, '__conform__', _nope)
    if conform is not _nope:
        adapter = conform(protocol, _nope)
        if adapter is not _nope:
            return adapter

    ## Third case: There is an adapter factory registered globally
    factoryCreated = getAdapter(protocol, obj, _nope)
    if factoryCreated is not _nope:
        return factoryCreated

    ## Fourth case: The class knows how to adapt some things
    adapt = getattr(obj, '__adapt__', _nope)
    if adapt is not _nope:
        adapter = adapt(obj, _nope)
        if adapter is not _nope:
            return adapter
    if default is not _nope:
        return default
    raise AdaptationError("Cannot adapt %r to %r." % (obj, protocol))


class Adapter(object):
    def __init__(self, original):
        self.original = original


def implements(*inter):
    loc = sys._getframe(1).f_locals
    loc['__implements__'] = loc.get('__implements__', ()) + inter


class Faceted(dict):
    def __conform__(self, interface, nope):
        facet = self.get(interface, nope)
        if facet is not nope:
            return facet
        factoryCreated = getAdapter(interface, self, nope)
        if factoryCreated is not nope:
            self[interface] = factoryCreated
            return factoryCreated
        return nope


def arguments(*adaptArgs, **adaptKw):
    def decorate(func):
        def doAdaption(*args, **kw):
            args = list(args)
            for (index, (protocol, value)) in enumerate(zip(adaptArgs, args)):
                args[index] = adapt(value, protocol)
            for adaptKey, adaptValue in adaptKw.items():
                kw[adaptKey] = adapt(kw[adaptKey], adaptValue)
            return func(*args, **kw)
        return doAdaption
    # XXX set func_name?
    return decorate
