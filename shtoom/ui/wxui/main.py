from wxPython.wx import *
from wxshtoomframe import ShtoomMainFrame
from wxlogframe import LogFrame
from shtoom.ui.base import ShtoomBaseUI
from twisted.python import log
from twisted.internet import reactor, defer
from prefs import PreferencesDialog
import thread
import os

# Implements the ShtoomMainFrame class as generated by
# wxglade. Call me paranoid but I'm not sticking this code
# in a generated file - no matter how bug free and fantastic
# wxglade is at generating code.

# TODO: Hookup the DTMF code for the number buttons

class ShtoomMainFrameImpl(ShtoomMainFrame, ShtoomBaseUI):
    # Control IDs
    MENU_PREFS = 101
    MENU_EXIT = 102
    MENU_HELP_CONTENTS = 103
    MENU_REGISTER = 104
    MENU_ERRORLOG = 105

    COMBO_ADDRESS = 150

    BUTT_ADVANCED = 201
    BUTT_CALL = 202
    BUTT_LOOKUP = 203
    BUTT_0 = 210
    BUTT_1 = 211
    BUTT_2 = 212
    BUTT_3 = 213
    BUTT_4 = 214
    BUTT_5 = 215
    BUTT_6 = 216
    BUTT_7 = 217
    BUTT_8 = 218
    BUTT_9 = 219
    BUTT_STAR = 220
    BUTT_HASH = 212

    def __init__(self, *args, **kwds):
        ShtoomMainFrame.__init__(self, *args, **kwds)
        EVT_MENU(self, self.MENU_EXIT, self.DoExit)
        EVT_MENU(self, self.MENU_PREFS, self.DoPreferences)
        EVT_MENU(self, self.MENU_REGISTER, self.DoRegister)
        EVT_MENU(self, self.MENU_ERRORLOG, self.DoErrorLog)
        EVT_BUTTON(self, self.BUTT_ADVANCED, self.OnAdvanced)
        EVT_BUTTON(self, self.BUTT_CALL, self.OnCall)
        EVT_TEXT_ENTER(self, self.COMBO_ADDRESS, self.PlaceCall)
        EVT_CLOSE(self, self.DoClose)

        # Advanced mode - whether to display the dtmf buttons or not
        self.advanced_mode = True
        # Call mode - whether the call button places a call or hangs up
        self.call_mode = True

        # Setup combobox values from previous address history
        self.combo_address.Clear()
        self.address_history = []
        self.loadHistory()
        if self.address_history:
            self.combo_address.Append("")
            [self.combo_address.Append(v) for v in self.address_history]

        sizex, sizey = self.GetSize()
        self.minx = sizex

        # Initialise the status bar
        self.SetStatusText('Not connected')

        # Startup without the "advanced" functionality showing
        # This also restricts the resizing of the window
        self.OnAdvanced(None)

        # Hookup the error log
        # Calculate initial pos for the message log window
        posx, posy = self.GetPosition()
        self.errorlog = LogFrameImpl(self, -1, "Message Log",
            pos=(posx+sizex+5,posy))
        wxLog_SetActiveTarget(wxLogTextCtrl(self.errorlog.text_errorlog))

        self.logger = Logger()

    def statusMessage(self, message):
        self.SetStatusText(message)

    def debugMessage(self, message):
        wxLogMessage(message)

    def errorMessage(self, message):
        wxLogMessage("ERROR: %s"%message)

    def updateCallButton(self, do_call):
        if do_call:
            self.call_mode = True
            self.button_call.SetLabel("Call")
        else:
            self.call_mode = False
            self.button_call.SetLabel("Hangup")

    def OnCall(self, event):
        if self.call_mode:
            self.PlaceCall(event)
        else:
            self.HangupCall(event)

    def getCurrentAddress(self):
        return self.combo_address.GetValue()

    def PlaceCall(self, event):
        sipURL = self.getCurrentAddress()
        if not sipURL.startswith('sip'):
            dlg = wxMessageDialog(self,
                '%s is a invalid address. The address must begin with "sip".'%sipURL,
                "Address error", wxOK)
            dlg.ShowModal()
            return
        # have hang up and call buttons toggle
        self.updateCallButton(do_call=False)
        self.app.placeCall(sipURL)

    def callStarted(self, cookie):
        self.cookie = cookie
        self.updateCallButton(do_call=False)

    def callConnected(self, cookie):
        self.updateCallButton(do_call=False)
        self.SetStatusText("Call connected")
        # Save the address we connected to. We'll use this to
        # pre-populate the address combo on startup
        address = self.getCurrentAddress()
        if address not in self.address_history:
            self.address_history.append(address)

    def callDisconnected(self, cookie, message=""):
        status = "Call disconnected"
        if message:
            status = "%s: %r"%(status, message)
        self.SetStatusText(status)
        self.updateCallButton(do_call=True)
        self.cookie = None

    def callFailed(self, cookie, message=""):
        status = "Call failed"
        if message:
            status = "%s: %r"%(status, message)
        self.SetStatusText(status)
        self.updateCallButton(do_call=True)
        self.cookie = None

    def HangupCall(self, event):
        self.app.dropCall(self.cookie)
        self.updateCallButton(do_call=True)
        self.SetStatusText('Not connected')
        self.cookie = False

    def incomingCall(self, description, cookie):
        from shtoom.exceptions import CallRejected
        dlg = wxMessageDialog(self, 'Incoming Call: %s\nAnswer?'%description,
            "Shtoom Call", wxYES_NO|wxICON_QUESTION)
        accept = dlg.ShowModal()
        if accept == wxID_YES:
            self.cookie = cookie
            self.updateCallButton(do_call=False)
            self.SetStatusText('Connected to %s'%description)
            self.app.answerIncomingCall(cookie)
        else:
            self.app.answerIncomingCall(CallRejected('no thanks', cookie))

    def DoErrorLog(self, event):
        self.errorlog.Show(True)

    def DoRegister(self, event):
        dlg = wxMessageDialog(self,
            'Re-register by entering new details in the identity preferences.\nContinue registering?',
            "Register", wxYES_NO|wxICON_QUESTION)
        accept = dlg.ShowModal()
        if accept == wxID_YES:
            self.app.register()

    def DoPreferences(self, event):
        dlg = PreferencesDialog(main=self, opts=self.app.getOptions())
        val = dlg.ShowModal()
        if val == wxID_OK:
            dlg.savePreferences(self.app)

    def getHistoryFilename(self):
        try:
            saveDir = os.path.expanduser('~%s'%os.getlogin())
        except:
            saveDir = os.getcwd()
        return os.path.join(saveDir, ".shtoom_history")

    def saveHistory(self):
        if self.address_history:
            hfile = self.getHistoryFilename()
            if not os.access(hfile, os.R_OK|os.W_OK):
                return
            hfp = open(hfile, 'w')
            [hfp.write('%s\n'%h) for h in self.address_history]
            hfp.close()

    def loadHistory(self):
        hfile = self.getHistoryFilename()
        if not os.access(hfile, os.R_OK|os.W_OK):
            return
        hfp = open(hfile, 'r')
        while 1:
            l = hfp.readline()
            if not l: break
            l = l.strip()
            self.address_history.append(l)
        hfp.close()

    def DoClose(self, event):
        # Write out the current address history
        self.saveHistory()
        # TODO: Move this into the proxy app
        reactor.callFromThread(reactor.stop)
        self.logger.disable()
        self.Destroy()

    def DoExit(self, event):
        self.Close(True)

    def UpdateHeight(self, newheight):
        curwidth, curheight = self.GetSize()
        self.SetSizeHints(self.minx, newheight, self.minx*2, newheight)
        self.SetSize((curwidth, newheight))
        self.Show(1)

    def debugSize(self):
        print "size=",self.GetSize()

    def OnAdvanced(self, event):
        # Hide the extended interface. Basically the last slot in the
        # frames sizer. Modifies the advanced button label. Fixes up window
        # sizes
        sizer = self.GetSizer()

        awidth,aheight = self.advanced.GetSize()
        fwidth,fheight = self.GetSize()

        if self.advanced_mode:
            self.advanced_mode = False
            self.advanced.Show(0)
            sizer.Show(self.advanced, 0)
            self.advheight = aheight
            newheight = fheight-aheight
            self.button_advanced.SetLabel('+')
            self.button_advanced.SetToolTipString("Display extra controls")
        else:
            self.advanced_mode = 1
            self.advanced.Show(1)
            sizer.Show(self.advanced, 1)
            newheight = fheight+self.advheight
            self.button_advanced.SetLabel('-')
            self.button_advanced.SetToolTipString("Hide extra controls")
        #self.Layout()
        #sizer.Layout()
        #sizer.Fit(self)
        #sizer.SetSizeHints(self)
        self.UpdateHeight(newheight)

    def getLogger(self):
        return self.logger


class LogFrameImpl(LogFrame):
    BUTT_CLEAR = 101
    BUTT_CLOSE = 102

    def __init__(self, *args, **kwargs):
        LogFrame.__init__(self, *args, **kwargs)
        EVT_BUTTON(self, self.BUTT_CLEAR, self.OnClear)
        EVT_BUTTON(self, self.BUTT_CLOSE, self.OnClose)
        EVT_CLOSE(self, self.OnClose)

    def OnClear(self, event):
        self.text_errorlog.Clear()

    def OnClose(self, event):
        self.Hide()

class Logger:
    def __init__(self):
        # Disable logging during shutdown
        self.enabled = 1

    def disable(self):
        self.enabled = 0

    def flush(self):
        pass

    def write(self, text):
        if self.enabled:
            wxLogMessage(text)
