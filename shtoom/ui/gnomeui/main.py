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
        self.hangupButton.set_sensitive(0)
        self.status = self.xml.get_widget("appbar").get_children()[0]
        self.acceptDialog = self.xml.get_widget("acceptdialog")

    # GUI callbacks
    def on_call_clicked(self, w):
        self.statusMessage("Calling...")
        sipURL = self.address.get_text()
        if not sipURL.startswith('sip:'):
            sipURL = "sip:" + sipURL
            self.address.prepend_text("sip:")
        self.hangupButton.set_sensitive(1)
        self.callButton.set_sensitive(0)
        self.address.set_sensitive(0)
        self.connected, deferred = self.sip.placeCall(sipURL)
        deferred.addCallbacks(self.callConnected, self.callFailed)
    
    def on_hangup_clicked(self, w):
        self.sip.dropCall(self.connected)
        self.callButton.set_sensitive(1)
        self.address.set_sensitive(1)
        self.hangupButton.set_sensitive(0)
        self.statusMessage("")
        self.connected = False
        
    def on_acceptdialog_response(self, widget, code):
        self.incoming.approved(code == gtk.RESPONSE_OK)
        del self.incoming

    def on_copy_activate(self, widget):
        self.address.copy_clipboard()

    def on_cut_activate(self, widget):
        self.address.cut_clipboard()

    def on_paste_activate(self, widget):
        self.address.paste_clipboard()

    def on_clear_activate(self, widget):
        self.address.set_text("")
    
    def on_preferences_activate(self, widget):
        self.statusMessage("Preferences are not supported yet.")

    def on_quit_activate(self, widget):
        reactor.stop()

    def on_about_activate(self, widget):
        self.xml.get_widget("about").show()
    
    # event callbacks
    def callConnected(self, call):
        self.hangupButton.set_sensitive(1)

    def callFailed(self, reason):
        self.statusMessage("Call failed: %s" % reason.value)
        self.hangupButton.set_sensitive(0)
        self.callButton.set_sensitive(1)
        self.address.set_sensitive(1)

    def incomingCall(self, description, call, defresp, defsetup):
        # XXX multiple incoming calls won't work
        self.incoming = Incoming(self, description, call, defresp, defsetup)  

    def debugMessage(self, msg):
        log.msg(msg)

    def statusMessage(self, msg):
        self.status.set_text(msg)


class Incoming:

    def __init__(self, main, description, call, deferredResponse, deferredSetup):
        main.xml.get_widget("acceptlabel").set_text("Accept call from %s?" % call)
        self.main = main
        self.description = description
        self.call = call
        self.deferredResponse = deferredResponse
        self.deferredSetup = deferredSetup
        self.main.acceptDialog.show()

    def approved(self, answer):
        if answer:
            self.main.connected = self.call
            self.main.callButton.set_sensitive(0)
            self.main.address.set_sensitive(0)
            self.deferredResponse.addCallbacks(self.main.callConnected, self.main.callFailed)
            self.deferredSetup.callback('yes')
        else:
            # XXX no string exceptions!
            self.deferredSetup.errback('no')
        del self.main.incoming
        del self.main
