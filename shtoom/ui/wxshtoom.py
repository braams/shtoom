"""wxWidget/wxWindow interface"""

from shtoom.ui.wxui import *
from wxPython.wx import *
from twisted.internet import reactor
import thread

class WxInjector(wxTimer):
    def __init__(self, evtlist, interval=200):
        wxTimer.__init__(self)
        self.evtlist = evtlist
        self.interval = interval

        # Schedule ourselves to be called
        self.Start(interval)

    def Notify(self):
        # Read any events off the event list and really call them
        while self.evtlist:
            call, args = self.evtlist.pop()
            call(*args)

        # Reschedule to be be called again
        self.Start(self.interval)


class AppProxy:
    def __init__(self, shtoomapp=None, wxapp=None):
        self.wxapp = wxapp
        self.shtoomapp = shtoomapp

    def setWxApp(self, wxapp):
        self.wxapp = wxapp

    def setShtoomApp(self, shtoomapp):
        self.shtoomapp = shtoomapp


class WxProxy(AppProxy):
    # Methods to forward onto the wx app
    # This is used from within the twisted thread

    threadedUI = True

    def __init__(self, *args, **kwargs):
        AppProxy.__init__(self, *args, **kwargs)
        self.evtlist = []

    def call(self, method, *args):
        self.evtlist.append((method, args))

    def startUI(self):
        WxInjector(self.evtlist)
        self.wxapp.MainLoop()

    def connectApplication(self, *args):
        self.call(self.wxapp.frame.connectApplication, *args)
    def resourceUsage(self, *args):
        self.call(self.wxapp.frame.resourceUsage, *args)
    def debugMessage(self, *args):
        self.call(self.wxapp.frame.debugMessage, *args)
    def statusMessage(self, *args):
        self.call(self.wxapp.frame.statusMessage, *args)
    def errorMessage(self, *args):
        self.call(self.wxapp.frame.errorMessage, *args)
    def callStarted(self, *args):
        self.call(self.wxapp.frame.callStarted, *args)
    def callConnected(self, *args):
        self.call(self.wxapp.frame.callConnected, *args)
    def callDisconnected(self, *args):
        self.call(self.wxapp.frame.callDisconnected, *args)
    def callFailed(self, *args):
        self.call(self.wxapp.frame.callFailed, *args)

    def incomingCall(self, *args):
        d = defer.Deferred()
        self.incomingDeferred = d
        self.call(self.wxapp.frame.incomingCall, *args)
        return d

    def answerIncomingCall(self, result):
        d, self.incomingDeferred = self.incomingDeferred, None
        d.callback(result)

    # Proxies for deferred callbacks + others
    def placeCall(self, sipURL):
        deferred = self.shtoomapp.placeCall(sipURL)
        deferred.addCallbacks(self.callConnected, self.callFailed).addErrback(log.err)

    def dropCall(self, cookie):
        self.shtoomapp.dropCall(cookie)

    def register(self):
        self.shtoomapp.register()

    def getOptions(self):
        return self.shtoomapp.getOptions()

    def updateOptions(self, opts):
        return self.shtoomapp.updateOptions(opts)


class ShtoomProxy(AppProxy):
    # Methods to forward onto the shtoom application from the wxapp
    # getOptions, register, placeCall, dropCall,

    # TODO: callFromThread isn't applicable here - these are called from
    # the main thread. The twisted event loop (list) is thread safe anyway

    def placeCall(self, sipURL):
        # From the wx thread: call into the main thread a function
        # which sets up the deferred calls on the WxAppProxy method.
        reactor.callFromThread(self.shtoomapp.placeCall, sipURL)

    def dropCall(self, cookie):
        reactor.callFromThread(self.shtoomapp.dropCall, cookie)

    def register(self):
        reactor.callFromThread(self.shtoomapp.register)

    def getOptions(self):
        return self.shtoomapp.getOptions()

    def updateOptions(self, opts):
        reactor.callFromThread(self.shtoomapp.updateOptions, opts)

    def answerIncomingCall(self, result):
        reactor.callFromThread(self.shtoomapp.answerIncomingCall, result)


class WxShtoomApplication(wxApp):
    def OnInit(self):
        wxImage_AddHandler(wxGIFHandler())
        self.frame = ShtoomMainFrameImpl(NULL, -1, "Shtoom")
        self.frame.Show(true)
        self.SetTopWindow(self.frame)
        return true


def main(shtoomapp):
    from twisted.python import threadable

    # wxreactor sucks generally.
    # wxsupport sucks on windows.
    # lets give threading a go

    threadable.init(1)
    wxapp = WxShtoomApplication()
    wxproxy = WxProxy(shtoomapp, wxapp)
    appproxy = ShtoomProxy(wxproxy)
    wxapp.frame.connectApplication(appproxy)

    from shtoom import log
    import sys
    # TODO: This style of logging isn't thread safe. Need to plugin
    # the logging into the WxInjector. i.e. the logger targets the
    # WxInjector.evtlist
    #log.startLogging(wxapp.frame.getLogger(), setStdout=False)
    log.startLogging(sys.stdout)

    return wxproxy
