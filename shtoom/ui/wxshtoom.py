"""wxWidget/wxWindow interface"""

from shtoom.ui.wxui import *

def shutdown():
    try:
        import itimer
        itimer.setitimer(itimer.ITIMER_REAL, 0.0, 0.0)
    except:
        pass
    from twisted.internet import reactor
    reactor.stop()

class ShtoomApplication(wxApp):
    def OnInit(self):
        self.frame = ShtoomMainFrameImpl(NULL, -1, "Shtoom")
        self.frame.Show(true)
        self.SetTopWindow(self.frame)
        return true

    # Proxy ShtoomBaseUI methods to top frame
    # It'd probably be much easier just to pass back the frame
    def connectApplication(self, *args):
        self.frame.connectApplication(*args)
    def resourceUsage(self, *args):
        self.frame.resourceUsage(*args)
    def debugMessage(self, *args):
        self.frame.debugMessage(*args)
    def statusMessage(self, *args):
        self.frame.statusMessage(*args)
    def errorMessage(self, *args):
        self.frame.errorMessage(*args)
    def incomingCall(self, *args):
        self.frame.incomingCall(*args)
    def callStarted(self, *args):
        self.frame.callStarted(*args)

def main(application):

    # wxreactor can't handle it captain.
    #from twisted.internet import wxreactor
    #wxreactor.install()
    
    UI = ShtoomApplication()
    UI.connectApplication(application)
    from twisted.internet import wxsupport
    wxsupport.install(UI)

    #from twisted.internet import reactor
    #reactor.registerWxApp(UI)

    return UI.frame

if __name__ == "__main__":
    main()

