
from shtoom.lwc import Interface, implements, registerAdapter, Faceted
from shtoom.lwc import providedBy, implementedBy, declareImplements
from shtoom.lwc import arguments, AdapterRegistry, IAdapterRegistry
from twisted.trial import unittest
from twisted.python import context

import sys

class LWCTests(unittest.TestCase):

    def test_lwc(self):
        ## Basic implements testing
        class IFoo(Interface):
            pass

        class Foo(object):
            implements(IFoo)

        assert IFoo in providedBy(Foo)
        f = Foo()
        assert IFoo(f) is f

        ## Adaption testing
        class IBar(Interface):
            pass

        class Bar(object):
            implements(IBar)
            def __init__(self, original=None):
                pass

        registerAdapter(Bar, Foo, IBar)

        b = Bar()
        assert IBar in implementedBy(b)

        fooBar = IBar(b)
        self.assert_(type(fooBar) is Bar)
        self.assert_(IBar in implementedBy(fooBar))

        # "Bar" was a factory because it took a single argument and
        # returned an implementor
        # The adapter factory doesn't have to be a class
        b2 = Bar()
        def fooToBar(obj):
            return b2

        # Only for testing purposes do we overwrite an old registration
        registerAdapter(fooToBar, Foo, IBar, overwrite=True)
        self.assert_(IBar(f) is b2)

        # "Faceted" lets us install components on an instance-by-instance
        # basis
        class Pluggable(Faceted):
            pass

        p = Pluggable()
        p[IFoo] = f
        p[IBar] = b

        self.assert_(IFoo(p) is f)
        self.assert_(IBar(p) is b)

        # Faceted can have adapter factories registered against them,
        # and "remembers" the output
        class IBaz(Interface):
            pass

        def pluggableToBaz(obj):
            return 1

        registerAdapter(pluggableToBaz, Pluggable, IBaz)

        self.assert_(IBaz not in p)
        self.assert_(IBaz(p) == 1)
        self.assert_(IBaz in p)

        ## Interface-to-interface adaption, a rarer use case
        class IString(Interface):
            pass

        class IFile(Interface):
            pass

        class Stringlike(object):
            implements(IString)

        def stringToFile(s):
            import StringIO
            return StringIO.StringIO(s)

        registerAdapter(stringToFile, IString, IFile)

        self.assert_(hasattr(IFile(Stringlike()), 'read'))

        registerAdapter(stringToFile, str, IFile)

        self.assert_(hasattr(IFile("Hello"), 'read'))

        ## Declare that str implements IFoo
        declareImplements(str, IFoo)

        foo = "Foo"

        self.assert_(IFoo in implementedBy(foo))

        ## Register an interface-to-interface adapter for IFoo to IBar
        registerAdapter(fooToBar, IFoo, IBar)

        ## Now we can adapt strings to IBar
        self.assert_(IBar("Foo") is b2)

        if sys.version_info >= (2,4):
            from shtoom.test.py24tests import decoratedLWCTest
            takesABar = decoratedLWCTest(IBar, b2)
            self.assert_(takesABar("This is not a bar, but can be adapted."))

        ## We have context-sensitive adapter registries
        newRegistry = AdapterRegistry()
        newRegistry.registerAdapter(lambda x: 1, str, IBar)

        def tryToAdaptToIBar(something):
            return IBar(something)

        result = context.call({IAdapterRegistry: newRegistry},
                                        tryToAdaptToIBar, "A string")
        self.assert_(result == 1)
