
from shtoommainwindow import *

import sys
from twisted.python import log
from qt import *

from twisted.internet import reactor

class ShtoomMainWindow(ShtoomMainWindow):
    
    sending = False
    audiosource = None
    connected = False

    def connectSIP(self):
        from shtoom import sip
        p = sip.SipPhone(self)
        self.sip = p
        self.sipListener = reactor.listenUDP(5060, p)
        log.msg('sip listener installed')

    def debugMessage(self, message):
        log.msg(message)

    def statusMessage(self, message):
        self.statusLabel.setText(message)

    def hangupButton_clicked(self):
        self.sip.dropCall(self.connected)
        self.callButton.setEnabled(True)
        self.hangupButton.setEnabled(False)
        self.connected = False

    def callButton_clicked(self):
        sipURL = str(self.addressComboBox.currentText())
        if not sipURL.startswith('sip:'):
            log.msg("Invalid SIP url %s"%(sipURL))
            return
        self.callButton.setEnabled(False)
        self.hangupButton.setEnabled(True)
        self.connected = self.sip.placeCall(sipURL)

    def setAudioSource(self, fn):
        self.audiosource = fn

    def getLogger(self):
        l = Logger(self.debuggingTextEdit)
        return l

    def clearButton_clicked(self):
        self.debuggingTextEdit.clear()

    def fileOpen(self):
        if self.audiosource:
            fn = self.audiosource
        else:
            fn = QString.null
        fn = QFileDialog.getOpenFileName(fn, QString.null, self)
        self.audiosource = str(fn)

    def filePrint(self):
        from preferencesdialog import PreferencesDialog
        p =PreferencesDialog()
        p.show()

class Logger:
    def __init__(self, textwidget):
        self._t = textwidget
    def flush(self): 
        pass
    def write(self, text):
        self._t.append(text)
