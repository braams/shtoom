
# Copyright (C) 2004 Anthony Baxter

from distutils.core import setup

from shtoom import Version

# patch distutils if it can't cope with the "classifiers" keyword.
# this just makes it ignore it.
import sys
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None

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
