
# Timer test. How many loops/sec does the wx timer loop
# get? On this linux P4M, it's around 60K/sec

from wxPython.wx import wxApp, wxTimer

from time import time

class TestTimer(wxTimer):
    def __init__(self):
        wxTimer.__init__(self)
        self.Start(1)
        self.count = 0
        self.startTime = time()

    def Notify(self):
        delta = time() - self.startTime
        if delta >= 1.0 and delta < 2.0:
            self.count += 1
        if delta >= 2.0:
            print "wxTimer got %s in 1s"%self.count
            self.startTime = time()
            self.count = 0


class ShtoomApplication(wxApp):
    def OnInit(self):
        from shtoom.ui.wxui import *
        self.frame = ShtoomMainFrameImpl(NULL, -1, "Shtoom")
        self.frame.Show(true)
        self.SetTopWindow(self.frame)
        return true

class DummyApp(wxApp):
    def OnInit(self):
        return True

d = ShtoomApplication()
t = TestTimer()
d.MainLoop()
