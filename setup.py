
# Copyright (C) 2004 Anthony Baxter

from distutils.core import setup
try:
    import py2exe
except:
    py2exe = None

from shtoom import __version__ 

class DependencyFailed(Exception): pass
class VersionCheckFailed(DependencyFailed): pass

#import sys
#if sys.version < '2.3':
#    raise VersionCheckFailed, "Python 2.3 is required"

#try:
#    import twisted
#except ImportError:
#    raise DependencyFailed, "You need Twisted - http://www.twistedmatrix.com/"

#from twisted.copyright import version as tcversion
#if tcversion < '1.1.1':
#    raise VersionCheckFailed, "Twisted 1.1.1 or later is required"

if py2exe is not None:
    addnl = { 'console':['scripts/shtoomphone.py'], 
              'windows': [ { 'script':'script/shtoomphone.py',
		             'icon_resources' : [( 1, 'shtoom.ico')] } ] }
else:
    addnl = {}

setup(
    name = "shtoom",
    version = __version__,
    description = "Shtoom - SIP softphone",
    author = "Anthony Baxter",
    author_email = "anthony@interlink.com.au",
    url = 'http://sourceforge.net/projects/shtoom/',
    packages = ['shtoom', 'shtoom.multicast',
                'shtoom.ui', 'shtoom.ui.qtui',
                'shtoom.ui.gnomeui', 'shtoom.ui.qtui',
                'shtoom.ui.textui', 'shtoom.ui.tkui', 'shtoom.ui.wxui',
                # 'shtoom.ui.mfcui', 'shtoom.ui.macui',
                'shtoom.audio', 'shtoom.app', 'shtoom.doug' ],
    requires = ( 'twisted', 'python-2.3' ), 
    provides = ( 'shtoom-%s'%__version__, ), 
    scripts = ['scripts/shtoomphone.py', 'scripts/shtam.py', 'scripts/shmessage.py',
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
    ],
    **addnl
)
