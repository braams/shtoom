#!/usr/bin/env python

# Copyright (C) 2004 Anthony Baxter

from shtoom.avail import ui

def findUserInterface(application, prefui):
    if prefui:
        if prefui.lower() == 'qt':
            main = ui.getQtInterface(fail=True)
        elif prefui.lower()[:2] == 'tk':
            main = ui.getTkInterface(fail=True)
        elif prefui.lower() == "gnome":
            main = ui.getGnomeInterface(fail=True)
        elif prefui.lower() == "wx":
            main = ui.getWxInterface(fail=True)
        elif prefui.lower() == "text":
            main = ui.getTextInterface(fail=True)
        else:
            raise ValueError('ui %s not known'%(prefui))
        return main(application)
    for attempt in ( ui.getGnomeInterface, ui.getQtInterface,
                     ui.getWxInterface, ui.getTkInterface,
                     ui.getTextInterface, ):
        main = attempt(fail=False)
        if main is not None:
            return main(application)
    # Other interfaces here
    raise RuntimeError,  "Couldn't load _any_ userinterfaces"
