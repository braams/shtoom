import os, gettext

_installedDomain = None
_installDir = None

def install(domain='shtoom'):
    # A hunting we will go, a hunting we will go, la de da de da
    global _installedDomain, _installDir

    if _installedDomain == domain:
        return

    d = _findLocaleDir(domain)
    if d is None:
        gettext.bindtextdomain(domain)
        gettext.textdomain(domain)
        gettext.install(domain)
    else:
        #print "found localedir", d
        _installDir = d
        gettext.bindtextdomain(domain, d)
        gettext.textdomain(domain)
        gettext.install(domain, d)
    _installedDomain = domain

def getLocaleDir():
    return _installDir

def _findLocaleDir(domain):
    import gettext, sys

    # try default location first
    f = gettext.find(domain)
    if f:
        return None

    # next try cwd
    f = gettext.find(domain, 'locale')
    if f:
        return 'locale'

    # next try python prefix
    pydir = os.path.join(sys.prefix, 'share', 'locale')
    f = gettext.find(domain, pydir)
    if f:
        return pydir

    # next try shtoom installation prefix
    import shtoom
    # -5 is prefix , lib, pythonN.N, site-packages, shtoom, __init__.pyc
    prefix = os.path.sep.join(shtoom.__file__.split(os.path.sep)[:-5])
    prefixdir  = os.path.join(prefix, 'share', 'locale')
    f = gettext.find(domain, pydir)
    if f:
        return prefixdir

    # Next try alongside 'shtoom' (running from srcdir?)
    srcdir = os.path.join(os.path.split(shtoom.__file__)[0], 'locale')
    f = gettext.find(domain, srcdir)
    if f:
        return srcdir

    # Try python installation prefix
    pydir = os.path.join(sys.prefix, 'share', 'locale')
    f = gettext.find(domain, pydir)
    if f:
        return pydir

    # just wing it
    return None
