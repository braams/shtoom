# Copyright (C) 2003 Anthony Baxter
from shtoommainwindow import *

from shtoom.ui.base import ShtoomBaseUI

import sys
from twisted.python import log
from qt import *

class ShtoomMainWindow(ShtoomMainWindow, ShtoomBaseUI):
    
    sending = False
    audiosource = None
    connected = False

    def debugMessage(self, message):
        log.msg(message)

    def statusMessage(self, message):
        self.statusLabel.setText(message)

    def errorMessage(self, message, exception=None):
        log.msg("ERROR: %s"%message)

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
        self.connected, defer = self.sip.placeCall(sipURL)
        defer.addCallbacks(self.call_connected, self.call_failed)

    def call_connected(self, call):
        self.hangupButton.setEnabled(True)

    def call_failed(self, e):
        self.errorMessage("call failed", e)
        self.hangupButton.setEnabled(False)
        self.callButton.setEnabled(True)

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
