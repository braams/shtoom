# Copyright (C) 2005 Anthony Baxter

# This file will eventually contain all of the horrors of import magic
# for UI toolkits

def cleanup(*names):
    import sys
    for name in names:
        if sys.modules.get(name):
            del sys.modules[name]

def getTextInterface(fail=False):
    from shtoom.ui.textshtoom import main
    return main

def getQtInterface(fail=False):
    try:
        import qt
    except (ImportError, SystemError):
        cleanup('qt')
        qt = None
        if fail:
            raise
    if qt is not None:
        from shtoom.ui.qtshtoom import main
        return main

def getWxInterface(fail=False):
    try:
        import wx
        import wxPython.wx
    except:
        cleanup('wx', 'wxPython', 'wxPython.wx')
        wx = None
        if fail:
            raise
    if wx is not None:
        from shtoom.ui.wxshtoom import main
        return main


def getTkInterface(fail=False):
    import sys
    try:
        import Tkinter
    except ImportError:
        cleanup('Tkinter', '_tkinter')
        Tkinter = None
        if fail:
            raise
    if Tkinter is not None:
        from shtoom.ui.tkshtoom import main
        return main

def getGnomeInterface(fail=False):
    try:
        import pygtk
        pygtk.require("2.0")
        import gnome.ui
        import gtk
        import gtk.glade
    except ImportError:
        cleanup('pygtk', 'gnome', 'gtk', 'gtk.glade', 'gnome.ui')
        if fail:
            raise
        gtk = None
    if gtk is not None:
        from shtoom.ui.gnomeshtoom import main
        return main

def listUI():
    uis = [ 'text', 'qt', 'wx', 'tk', 'gnome' ]

    uis = [ (x,globals()['get%sInterface'%(x.capitalize())](fail=False)) 
                                                        for x in uis ]
    uis = [ x[0] for x in uis if x[1] is not None ]
    return uis
