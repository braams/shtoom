"""wxWidget/wxWindow interface"""

from shtoom.ui.wxui import *
from wxPython.wx import *
from twisted.internet import reactor

class AppProxy:
    def __init__(self, shtoomapp=None, wxapp=None):
        self.wxapp = wxapp
        self.shtoomapp = shtoomapp

    def setWxApp(self, wxapp):
        self.wxapp = wxapp

    def setShtoomApp(self, shtoomapp):
        self.shtoomapp = shtoomapp

# Main Thread:
#  reactor.eventloop - WxProxy instance
# 
# Child Thread:
#  wxapp.eventloop - ShtoomProxy instance

# placeCall
# CT User clicks "call" button -> 
# CT calls ShtoomProxy.placeCall ->
# MT calls WxProxy.placeCall ->
# MT calls shtoom.app.placeCall, gets a deferred ->
# MT calls deferred.addCallbacks(WxProxy.callOk, WxProxy.callFailed)
# ....
# MT wxProxy.Call?? ->
# CT wxapp.Call?? 

# TODO: MT log handling

class WxProxy(AppProxy):
    # Methods to forward onto the wx app
    # We may need to put these on the wx event loop if things aren't
    # thread safe
    def connectApplication(self, *args):
        self.wxapp.frame.connectApplication(*args)
    def resourceUsage(self, *args):
        self.wxapp.frame.resourceUsage(*args)
    def debugMessage(self, *args):
        self.wxapp.frame.debugMessage(*args)
    def statusMessage(self, *args):
        self.wxapp.frame.statusMessage(*args)
    def errorMessage(self, *args):
        self.wxapp.frame.errorMessage(*args)
    def incomingCall(self, *args):
        self.wxapp.frame.incomingCall(*args)
    def callStarted(self, *args):
        self.wxapp.frame.callStarted(*args)
    def callConnected(self, *args):
        self.wxapp.frame.callConnected(*args)
    def callFailed(self, *args):
        self.wxapp.frame.callFailed(*args)

    # Proxies for deferred callbacks + others
    def placeCall(self, sipURL):
        print "wx proxy calling placeCall to ", sipURL, self.shtoomapp
        deferred = self.shtoomapp.placeCall(sipURL)
        print "wx proxy got deferred"
        deferred.addCallbacks(self.callConnected, self.callFailed).addErrback(log.err)
        print "wx proxy returning"

    def dropCall(self, cookie):
        self.shtoomapp.dropCall(cookie)

class ShtoomProxy(AppProxy):
    # Methods to forward onto the shtoom application from the wxapp
    # getOptions, register, placeCall, dropCall, 
    def placeCall(self, sipURL):
        # From the wx thread: call into the main thread a function
        # which sets up the deferred calls on the WxAppProxy method.
        print "shtoom proxy calling placeCall"
        reactor.callFromThread(self.shtoomapp.placeCall, sipURL)

    def dropCall(self, cookie):
        reactor.callFromThread(self.shtoomapp.dropCall, cookie)
    

class WxShtoomApplication(wxApp):
    def OnInit(self):
        wxImage_AddHandler(wxGIFHandler())
        self.frame = ShtoomMainFrameImpl(NULL, -1, "Shtoom")
        self.frame.Show(true)
        self.SetTopWindow(self.frame)
        return true

def main(shtoomapp):
    from twisted.python import log, threadable

    # wxreactor sucks generally.
    # wxsupport sucks on windows. 
    # lets give threading a go

    threadable.init(1)
    wxapp = WxShtoomApplication()
    wxproxy = WxProxy(shtoomapp, wxapp)
    appproxy = ShtoomProxy(wxproxy)
    wxapp.frame.connectApplication(appproxy)
    log.startLogging(wxapp.frame.getLogger(), setStdout=False)

    reactor.callInThread(wxapp.MainLoop)

    return wxproxy

if __name__ == "__main__":
    main()

