#!/usr/bin/env python

# Copyright (C) 2004 Anthony Baxter

def tryTextInterface(application):
    import sys
    from shtoom.ui.textshtoom import main
    return main(application)

def tryQtInterface(application):
    import sys
    try:
        import qt
    except ImportError:
        qt = None
    if qt is not None:
        from shtoom.ui.qtshtoom import main
        return main(application)

def tryWxInterface(application):
    import sys
    try:
        import wx
    except ImportError:
        wx = None
    if wx is not None:
        from shtoom.ui.wxshtoom import main
        return main(application)


def tryTkInterface(application):
    import sys
    try:
        import Tkinter
    except ImportError:
        Tkinter = None
    if Tkinter is not None:
        from shtoom.ui.tkshtoom import main
        return main(application)

def tryGnomeInterface(application):
    import sys
    try:
        import pygtk
        pygtk.require("2.0")
    except ImportError:
        pass
    try:
        import gtk
        import gtk.glade
    except ImportError:
        gtk = None
    if gtk is not None:
        from shtoom.ui.gnomeshtoom import main
        return main(application)

def findUserInterface(application, prefui):
    ui = None
    if prefui:
        if prefui.lower() == 'qt':
            ui = tryQtInterface(application)
        elif prefui.lower()[:2] == 'tk':
            ui = tryTkInterface(application)
        elif prefui.lower() == "gnome":
            ui = tryGnomeInterface(application)
        elif prefui.lower() == "wx":
            ui = tryWxInterface(application)
        elif prefui.lower() == "text":
            ui = tryTextInterface(application)
    if ui is not None:
        return ui
    for attempt in ( tryQtInterface, tryGnomeInterface, tryWxInterface, 
                    tryTkInterface, tryTextInterface, ):
        ui = attempt(application)
        if ui is not None:
            return ui
    # Other interfaces here
    raise RuntimeError,  "Couldn't load _any_ userinterfaces"
