
# Copyright (C) 2004 Anthony Baxter

from distutils.core import setup
try:
    import py2exe
except:
    pass

from shtoom import Version

class DependencyFailed(Exception): pass
class VersionCheckFailed(DependencyFailed): pass

import sys
if sys.version < '2.3':
    raise VersionCheckFailed, "Python 2.3 is required"

try:
    import twisted
except ImportError:
    raise DependencyFailed, "You need Twisted - http://www.twistedmatrix.com/"

from twisted.copyright import version as tcversion
if tcversion < '1.1.1':
    raise VersionCheckFailed, "Twisted 1.1.1 or later is required"

setup(
    name = "shtoom",
    version = Version,
    description = "Shtoom - SIP softphone",
    author = "Anthony Baxter",
    author_email = "anthony@interlink.com.au",
    url = 'http://sourceforge.net/projects/shtoom/',
    packages = ['shtoom', 'shtoom/multicast',
                'shtoom/ui', 'shtoom/ui/qtui',
                'shtoom/ui/gnomeui', 'shtoom/ui/qtui',
                'shtoom/ui/textui', 'shtoom/ui/tkui',
                # 'shtoom/ui/mfcui', 'shtoom/ui/macui',
                'shtoom/audio', ],
    scripts = ['shtoom.py'
               # 'shtam.py', 'shtoomcu.py'
              ],
    classifiers = [
       'Development Status :: 3 - Alpha',
       'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
       'Operating System :: POSIX',
       'Operating System :: Microsoft :: Windows',
       'Operating System :: MacOS :: MacOS X',
       'Programming Language :: Python',
       'Topic :: Internet',
       'Topic :: Communications :: Internet Phone',
    ]

)
