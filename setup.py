#!/usr/bin/env python

# Copyright (C) 2004 Anthony Baxter

from distutils.core import setup
try:
    import py2exe
except:
    py2exe = None

from shtoom import __version__

class DependencyFailed(Exception): pass
class VersionCheckFailed(DependencyFailed): pass

import sys
if sys.version < '2.3':
    raise VersionCheckFailed("Python 2.3 or later is required")

try:
    import twisted
except ImportError:
    raise DependencyFailed("You need Twisted - http://www.twistedmatrix.com/")

from twisted.copyright import version as tcversion
if not tcversion.startswith('SVN') and tcversion < '1.3':
    raise VersionCheckFailed("Twisted 1.3 or later is required")

#try:
#    import zope.interface
#except ImportError:
#    raise DependencyFailed("You need to install zope.interface - http://zope.org/Products/ZopeInterface")

if py2exe is not None:
    addnl = { 'console':['scripts/shtoomphone.py'],
              'windows': [ { 'script':'script/shtoomphone.py',
                             'icon_resources' : [( 1, 'shtoom.ico')] } ] }
else:
    addnl = {}

setup(
    name = "shtoom",
    version = __version__,
    description = "Shtoom - SIP stack (including a softphone)",
    author = "Anthony Baxter",
    author_email = "anthony@interlink.com.au",
    url = 'http://shtoom.divmod.org/',
    packages = ['shtoom', 'shtoom.address', 'shtoom.multicast', 'shtoom.avail',
                'shtoom.ui', 'shtoom.rtp', 'shtoom.ui.qtui',
                'shtoom.ui.gnomeui', 'shtoom.ui.qtui',
                'shtoom.ui.textui', 'shtoom.ui.tkui', 'shtoom.ui.wxui',
                # 'shtoom.ui.mfcui', 'shtoom.ui.macui',
                'shtoom.audio', 'shtoom.app', 'shtoom.doug', 'shtoom.compat' ],
    scripts = ['scripts/shtoomphone.py', 'scripts/shtam.py',
               'scripts/shmessage.py', 'scripts/shecho.py',
              ],
    package_data = {'': ['*.glade','*.gladep','*.gif', '*.png']},
    classifiers = [
       'Development Status :: 3 - Alpha',
       'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
       'Operating System :: POSIX',
       'Operating System :: Microsoft :: Windows',
       'Operating System :: MacOS :: MacOS X',
       'Programming Language :: Python',
       'Topic :: Internet',
       'Topic :: Communications :: Internet Phone',
    ],
    **addnl
)

if sys.version_info < (2, 4):
    print "You'll need to install the .glade file from shtoom/ui/gnomeui by hand :-("
