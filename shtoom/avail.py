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
    import pyspeex as speex
except ImportError:
    speex = None
    _removeImport('pyspeex')

# XXX Haven't implemented speex yet, so disabling it
speex = None

try:
    from audioop import ulaw2lin, lin2ulaw
    mulaw = ulaw2lin
except ImportError:
    mulaw = None

try:
    from audioop import alaw2lin, lin2alaw
    alaw = alaw2lin
except ImportError:
    alaw = None

dvi4 = None # always, until it's implemented
ilbc = None # always, until it's implemented
