

from shtoommain import *

import sys
from twisted.python import log
from qt import *

from twisted.internet import reactor

class ShtoomMainWindow(PySipMainWindow):
    
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
        self.StatusLabel.setText(message)

    def callButton_clicked(self):
        if self.connected:
            self.sip.dropCall(self.connected)
            self.pushButton3.setText("Call")
            self.connected = False
        else:
            from shtoom.rtp import RTPProtocol
            sipURL = str(self.sipURL.text())
            if not sipURL.startswith('sip:'):
                log.msg("Invalid SIP url %s"%(sipURL))
                return
            self.pushButton3.setText("Hang up")
            self.connected = self.sip.placeCall(sipURL)

    def stopRTP(self):
        log.msg("User requested stop of RTP")
        # cancel callback
        self.RTP.whenDone(None)
        self.RTP.stopSending()
        self.rtpDone()

    def startRTP(self):
        from shtoom.rtp import RTPProtocol
        host, port = str(self.rtpHostTextLine.text()), str(self.rtpPortTextLine.text())
        port = int(port)
        self.RTP = RTPProtocol()
        # Create the local sockets
        lrtp, lrtcp = self.RTP.createRTPSocket()
        log.msg("local RTP/RTCP ports %s/%s"%(lrtp, lrtcp))
        self.StatusLabel.setText("sending")
        log.msg("User requested start of RTP")
        self.RTP.whenDone(self.rtpDone)
        print self.audiosource, type(self.audiosource)
        if self.audiosource:
            self.RTP.startSending((host,port), open(self.audiosource))
        else:
            self.RTP.startSending((host,port))
        self.sending = True

    def setAudioSource(self, fn):
        self.audiosource = fn

    def rtpDone(self):
        log.msg("finished sending RTP audio")
        self.sending = False
        self.StatusLabel.setText("idle")
        del self.RTP

    def getLogger(self):
        l = Logger(self.logMessages)
        return l

    def clear_logMessages(self):
        self.logMessages.clear()

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
