# Copyright (C) 2004 Anthony Baxter
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
        defer.addCallbacks(self.callConnected, self.callDisconnected).addErrback(log.err)

    def callConnected(self, call):
        self.hangupButton.setEnabled(True)

    def callDisconnected(self, e):
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

    def incomingCall(self, description, call, defresp, defsetup):
        accept = QMessageBox.information(self, 'Shtoom',
                'Incoming Call: %s\nAnswer?'%description,
                'Yes', 'No', '', 0, 1)
        print "accept is", accept
        if accept == 0:
            self.connected = call
            self.callButton.setEnabled(False)
            defsetup.addCallbacks(self.callConnected, self.callDisconnected).addErrback(log.err)
            defresp.callback('yes')
        else:
            # BOGUS
            defresp.errback('no')


class Logger:
    def __init__(self, textwidget):
        self._t = textwidget
    def flush(self):
        pass
    def write(self, text):
        self._t.append(text)
