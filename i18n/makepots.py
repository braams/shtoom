#!/usr/bin/env python

import os, fnmatch

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

def main():
    pyfiles = []
    for srcdir in ('scripts', 'shtoom'):
        for wd in '.', '..':
            t = os.path.join(wd, srcdir)
            if os.path.isdir(t):
                pyfiles.extend(getMatchingFiles(t, '*.py'))
                break
    print "found %d python files" %(len(pyfiles))
    if os.path.isdir(t):
        gladepath = os.path.join(t, 'ui/gnomeui/shtoom.glade')
    print "found glade file %s"%(gladepath)
    if os.path.isdir('i18n'):
        outdir = 'i18n'
    else:
        outdir = '.'
    os.system('intltool-extract -t gettext/glade %s'%gladepath)
    os.system('xgettext -o %s/glade.pot --keyword="N_" %s'%(outdir,gladepath))
    os.system('xgettext -o %s/python.pot --keyword="__tr" %s'%(outdir,
                                                        ' '.join(pyfiles)))
    os.system('msgcomm --more-than=0 -o %s/shtoom.pot %s/python.pot %s/glade.pot'%(outdir,outdir,outdir))
    pofiles = getMatchingFiles(outdir, '*.po')
    print "found %d existing po files"%(len(pofiles))
    for po in pofiles:
        os.system('msgmerge -U %s shtoom.pot'%(po,))
    os.remove('%s/glade.pot'%(outdir))
    os.remove('%s/python.pot'%(outdir))

if __name__ == "__main__":
    main()
