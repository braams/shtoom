"""Gnome interface to shtoom."""

import gtk
import gtk.glade

from twisted.python import util, log
from twisted.internet import reactor

from shtoom.ui.base import ShtoomBaseUI


class ShtoomWindow(ShtoomBaseUI):

    def __init__(self):
        self.connected = False
        self.xml = gtk.glade.XML(util.sibpath(__file__, "shtoom.glade"))
        self.xml.signal_autoconnect(self)
        self.xml.get_widget("callwindow").connect("destroy", lambda w: reactor.stop())
        self.address = self.xml.get_widget("address")
        self.callButton = self.xml.get_widget("call")
        self.hangupButton = self.xml.get_widget("hangup")
        self.status = self.xml.get_widget("appbar").get_children()[0]
        
    def on_call_clicked(self, w):
        self.statusMessage("Calling...")
        sipURL = self.address.get_text()
        if not sipURL.startswith('sip:'):
            sipURL = "sip:" + sipURL
            self.address.prepend_text("sip:")
        self.callButton.set_sensitive(0)
        self.address.set_sensitive(0)
        self.connected, deferred = self.sip.placeCall(sipURL)
        deferred.addCallbacks(self.callConnected, self.callFailed)

    def callConnected(self, call):
        self.hangupButton.set_sensitive(1)

    def callFailed(self, reason):
        self.statusMessage("Call failed: %s" % reason.value)
        self.hangupButton.set_sensitive(0)
        self.callButton.set_sensitive(1)
        self.address.set_sensitive(1)
    
    def on_hangup_clicked(self, w):
        self.sip.dropCall(self.connected)
        self.callButton.set_sensitive(1)
        self.address.set_sensitive(1)
        self.hangupButton.set_sensitive(0)
        self.statusMessage("")
        self.connected = False

    def incomingCall(self, description, call, defresp, defsetup):
        import tkMessageBox
        answer = tkMessageBox.askyesno("Shtoom", "Incoming Call: %s\nAnswer?"%description)
        if answer:
            self.connected = call
            self.callButton.set_sensitive(0)
            self.address.set_sensitive(0)
            defsetup.addCallbacks(self.callConnected, self.callFailed)
            defresp.callback('yes')
        else:
            defresp.errback('no')

    def debugMessage(self, msg):
        log.msg(msg)

    def statusMessage(self, msg):
        self.status.set_text(msg)
