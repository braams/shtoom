# Twisted, the Framework of Your Internet
# Copyright (C) 2001 Matthew W. Lefkowitz
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from wxPython.wx import *

from twisted.internet import wxreactor
wxreactor.install()
from twisted.internet import reactor

from wxshtoomframe import ShtoomMainFrame

class ShtoomMainFrameImpl(ShtoomMainFrame):
    MENU_PREFS = 101
    MENU_EXIT = 102
    MENU_HELP_CONTENTS = 103

    def __init__(self, *args, **kwds):
        ShtoomMainFrame.__init__(self, *args, **kwds)
        EVT_MENU(self, self.MENU_EXIT, self.DoExit)

    def DoExit(self, event):
        self.Close(True)
        reactor.stop()

class ShtoomApplication(wxApp):
    def OnInit(self):
        frame = ShtoomMainFrameImpl(NULL, -1, "Hello, world")
        frame.Show(true)
        self.SetTopWindow(frame)
        return true


def demo():
    app = ShtoomApplication(0)
    reactor.registerWxApp(app)
    reactor.run(0)


if __name__ == '__main__':
    demo()
