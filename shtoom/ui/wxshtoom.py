"""wxWidget/wxWindow interface"""

from shtoom.ui.wxui import *
from wxPython.wx import *

class ShtoomApplication(wxApp):
    def OnInit(self):
        self.frame = ShtoomMainFrameImpl(NULL, -1, "Shtoom")
        self.frame.Show(true)
        self.SetTopWindow(self.frame)
        return true

def main(application):
    from twisted.python import log
    from twisted.internet import wxsupport

    # wxreactor can't handle it captain.
    #from twisted.internet import wxreactor
    #wxreactor.install()

    wxImage_AddHandler(wxGIFHandler())
    UI = ShtoomApplication()
    UI.frame.connectApplication(application)
    log.startLogging(UI.frame.getLogger(), setStdout=False)
    wxsupport.install(UI)

    #from twisted.internet import reactor
    #reactor.registerWxApp(UI)

    return UI.frame

if __name__ == "__main__":
    main()

