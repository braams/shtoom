# Copyright (C) 2004 Anthony Baxter
from shtoommainwindow import ShtoomMainWindow as ShtoomBaseWindow

from shtoom.ui.base import ShtoomBaseUI

import sys
from twisted.python import log
from qt import *

class ShtoomMainWindow(ShtoomBaseWindow, ShtoomBaseUI):

    sending = False
    audiosource = None
    cookie = None
    def __init__(self, *args, **kwargs):
        ShtoomBaseWindow.__init__(self, *args, **kwargs)
        from shtoom.ui.logo import logoGif
        self.pixmapLogo.setPixmap(QPixmap(QByteArray(logoGif)))

    def debugMessage(self, message):
        log.msg(message)

    def statusMessage(self, message):
        self.statusLabel.setText(message)

    def errorMessage(self, message, exception=None):
        log.msg("ERROR: %s"%message)

    def hangupButton_clicked(self):
        self.app.dropCall(self.cookie)
        self.callButton.setEnabled(True)
        self.hangupButton.setEnabled(False)
        self.cookie = None

    def register_clicked(self):
        self.app.register()

    def callButton_clicked(self):
        sipURL = str(self.addressComboBox.currentText())
        if not sipURL.startswith('sip:'):
            log.msg("Invalid SIP url %s"%(sipURL))
            return
        self.callButton.setEnabled(False)
        defer = self.app.placeCall(sipURL)
        defer.addCallbacks(self.callStarted, self.callFailed).addErrback(log.err)

    def callStarted(self, cookie):
        self.cookie = cookie
        self.hangupButton.setEnabled(True)
        self.statusMessage('Calling...')

    def callFailed(self, e):
        self.errorMessage("call failed", e)
        self.hangupButton.setEnabled(False)
        self.callButton.setEnabled(True)

    def callConnected(self, cookie):
        self.statusMessage('Call Connected')

    def callDisconnected(self, e):
        self.statusMessage('Call disconnected: %r'%(e))

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

    def filePrefs(self):
        from prefs import PreferencesDialog
        self.prefs =PreferencesDialog(self, self.app.getOptions())
        self.prefs.show()

    def preferences_save(self, options):
        print "save prefs", options
        self.app.updateOptions(options)
        self.prefs.hide()

    def preferences_discard(self):
        self.prefs.hide()

    def incomingCall(self, description, call, defresp):
        from shtoom.exceptions import CallRejected
        accept = QMessageBox.information(self, 'Shtoom',
                'Incoming Call: %s\nAnswer?'%description,
                'Yes', 'No', '', 0, 1)
        print "accept is", accept
        if accept == 0:
            self.cookie = call
            self.callButton.setEnabled(False)
            defresp.callback('yes')
        else:
            # BOGUS
            defresp.errback(CallRejected)

    def dtmfButtonHash_pressed(self):
        if self.cookie is not None:
            self.app.startDTMF(self.cookie, '#')

    def dtmfButtonHash_released(self):
        if self.cookie is not None:
            self.app.stopDTMF(self.cookie, '#')

    def dtmfButtonStar_pressed(self):
        if self.cookie is not None:
            self.app.startDTMF(self.cookie, '*')

    def dtmfButtonStar_released(self):
        if self.cookie is not None:
            self.app.stopDTMF(self.cookie, '*')

    def dtmfButton1_pressed(self):
        if self.cookie is not None:
            self.app.startDTMF(self.cookie, '1')

    def dtmfButton1_released(self):
        if self.cookie is not None:
            self.app.stopDTMF(self.cookie, '1')

    def dtmfButton2_pressed(self):
        if self.cookie is not None:
            self.app.startDTMF(self.cookie, '2')

    def dtmfButton2_released(self):
        if self.cookie is not None:
            self.app.stopDTMF(self.cookie, '2')

    def dtmfButton3_pressed(self):
        if self.cookie is not None:
            self.app.startDTMF(self.cookie, '3')

    def dtmfButton3_released(self):
        if self.cookie is not None:
            self.app.stopDTMF(self.cookie, '3')

    def dtmfButton4_pressed(self):
        if self.cookie is not None:
            self.app.startDTMF(self.cookie, '4')

    def dtmfButton4_released(self):
        if self.cookie is not None:
            self.app.stopDTMF(self.cookie, '4')

    def dtmfButton5_pressed(self):
        if self.cookie is not None:
            self.app.startDTMF(self.cookie, '5')

    def dtmfButton5_released(self):
        if self.cookie is not None:
            self.app.stopDTMF(self.cookie, '5')

    def dtmfButton6_pressed(self):
        if self.cookie is not None:
            self.app.startDTMF(self.cookie, '6')

    def dtmfButton6_released(self):
        if self.cookie is not None:
            self.app.stopDTMF(self.cookie, '6')

    def dtmfButton7_pressed(self):
        if self.cookie is not None:
            self.app.startDTMF(self.cookie, '7')

    def dtmfButton7_released(self):
        if self.cookie is not None:
            self.app.stopDTMF(self.cookie, '7')

    def dtmfButton8_pressed(self):
        if self.cookie is not None:
            self.app.startDTMF(self.cookie, '8')

    def dtmfButton8_released(self):
        if self.cookie is not None:
            self.app.stopDTMF(self.cookie, '8')

    def dtmfButton9_pressed(self):
        if self.cookie is not None:
            self.app.startDTMF(self.cookie, '9')

    def dtmfButton9_released(self):
        if self.cookie is not None:
            self.app.stopDTMF(self.cookie, '9')

    def dtmfButton0_pressed(self):
        if self.cookie is not None:
            self.app.startDTMF(self.cookie, '0')

    def dtmfButton0_released(self):
        if self.cookie is not None:
            self.app.stopDTMF(self.cookie, '0')

class Logger:
    def __init__(self, textwidget):
        self._t = textwidget
    def flush(self):
        pass
    def write(self, text):
        self._t.append(text)
