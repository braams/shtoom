#!/usr/bin/env python

import os, fnmatch, shutil

def getMatchingFiles(root, pattern):
    """ Returns a list of all files under directory 'root' that
        match pattern 'pattern'
    """
    pyfiles = []
    for path, dirnames, filenames in os.walk(root):
        if '.svn' in dirnames:
            dirnames.remove('.svn')
        py = fnmatch.filter(filenames, pattern)
        py = [ os.path.join(path, x) for x in py ]
        pyfiles.extend(py)
    return pyfiles

def main(target):
    if not os.path.isdir(target):
        raise ValueError('%s is not an existing directory!'%(target))
    if os.path.exists('./shtoom.pot'):
        srcdir = '.'
    elif os.path.exists('i18n/shtoom.pot'):
        srcdir = 'i18n'
    pofiles = getMatchingFiles(srcdir, '*.po')
    for po in pofiles:
        os.system('msgfmt %s'%(po))
    mofiles = getMatchingFiles(srcdir, '*.mo')
    for mo in mofiles:
        lang, ext = os.path.basename(mo).split('.')
        langdir = os.path.join(target, lang)
        if not os.path.isdir(langdir):
            print "making %s"%(langdir)
            os.mkdir(langdir)
        lcdir = os.path.join(langdir, 'LC_MESSAGES')
        if not os.path.isdir(lcdir):
            print "making %s"%(lcdir)
            os.mkdir(lcdir)
        dest = os.path.join(lcdir, 'shtoom.mo')
        print "copying %s -> %s"%(mo, dest)
        shutil.copy(mo, dest)


if __name__ == "__main__":
    import sys
    main(sys.argv[1])
