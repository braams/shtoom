# Copyright (C) 2004 Anthony Baxter

# This file will eventually contain all of the horrors of import magic
# for codecs


from shtoom.avail import _removeImport

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
