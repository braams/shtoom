#!/usr/bin/env python

# Copyright (C) 2003 Anthony Baxter



def tryTextInterface():
    import sys
    from shtoom.ui.textshtoom import main
    main()
    sys.exit()

def tryQtInterface():
    import sys
    try:
        import qt
    except ImportError:
        qt = None
    if qt is not None:
        from shtoom.ui.qtshtoom import main
        main()
        sys.exit()

def tryTkInterface():
    import sys
    try:
        import Tkinter
    except ImportError:
        Tkinter = None
    if Tkinter is not None:
        from shtoom.ui.tkshtoom import main
        main()
        sys.exit()

def tryGnomeInterface():
    import sys
    try:
        import pygtk
        pygtk.require("2.0")
    except ImportError:
        pass
    try:
        import gtk
    except ImportError:
        gtk = None
    if gtk is not None:
        from shtoom.ui.gnomeshtoom import main
        main()
        sys.exit()


def findUserInterface():
    from shtoom import prefs
    if prefs.ui:
        if prefs.ui.lower() == 'qt':
            tryQtInterface()
        elif prefs.ui.lower()[:2] == 'tk':
            tryTkInterface()
        elif prefs.ui.lower() == "gnome":
            tryGnomeInterface()
        elif prefs.ui.lower() == "text":
            tryTextInterface()
    tryQtInterface()
    tryGnomeInterface()
    tryTkInterface()
    tryTextInterface()
    # Other interfaces here
    print "Error: Couldn't load _any_ userinterfaces"

def main():
    import sys
    from shtoom.opts import parseOptions
    parseOptions()
    findUserInterface()

if __name__ == "__main__":
    main()
