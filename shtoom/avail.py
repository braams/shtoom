# This file will eventually contain all of the horrors of import magic


def _removeImport(mod):
    # Prior to 2.4, you could end up with broken crap in sys.modules
    import sys
    if sys.version_info < (2,4):
        if mod in sys.modules:
            del sys.modules[mod]

try:
    import gsm
except ImportError:
    gsm = None
    _removeImport('gsm')

try:
    import speex
except ImportError:
    speex = None
    _removeImport('speex')

dvi4 = None # always, until it's implemented

