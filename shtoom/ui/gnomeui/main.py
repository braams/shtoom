"""Gnome interface to shtoom."""

import gtk
import gtk.glade

from twisted.python import util, log
from twisted.internet import reactor, defer

from shtoom.ui.base import ShtoomBaseUI
from popups import PopupNotice


class ShtoomWindow(ShtoomBaseUI):

    def __init__(self):
        self.cookie = False
        self.xml = gtk.glade.XML(util.sibpath(__file__, "shtoom.glade"))
        self.xml.signal_autoconnect(self)
        self.xml.get_widget("callwindow").connect("destroy",
                                                lambda w: reactor.stop())
        self.address = self.xml.get_widget("address")
        #self.address.set_value_in_list(False, False)
        self.callButton = self.xml.get_widget("call")
        self.dtmfwindow = self.xml.get_widget("dtmfWindow")
        self.debugwindow = self.xml.get_widget("debugWindow")
        self.hangupButton = self.xml.get_widget("hangup")
        self.hangupButton.set_sensitive(0)
        self.status = self.xml.get_widget("statusbar")
        self.acceptDialog = self.xml.get_widget("acceptdialog")
        self.incoming = []

        debug = self.xml.get_widget("debuglog")
        self.logger = DebugTextView(debug.get_buffer())
        #h = self.xml.get_widget('hbox2')
        #h.hide()

    def getLogger(self):
        return self.logger

    def setaddress(self,sipurl):
        self.address.set_text(sipurl)

    # GUI callbacks
    def on_call_clicked(self, w):
        self.statusMessage("Calling...")
        sipURL = self.address.get_text()
        sipURL = self.addrlookup.lookup(sipURL)
        self.address.set_text(sipURL)
        # Add the item to self.address.list ... argh gtk docs SUCK
        self.hangupButton.set_sensitive(1)
        self.callButton.set_sensitive(0)
        self.address.set_sensitive(0)
        deferred = self.app.placeCall(sipURL)
        deferred.addCallbacks(self.callConnected, self.callFailed
                                                        ).addErrback(log.err)
    def on_hangup_clicked(self, w):
        self.app.dropCall(self.cookie)
        self.callButton.set_sensitive(1)
        self.address.set_sensitive(1)
        self.hangupButton.set_sensitive(0)
        self.statusMessage("")
        self.cookie = None

    def on_register_clicked(self, w):
        self.app.register()

    def on_acceptdialog_response(self, widget, code):
        self.incoming[0].approved(code == gtk.RESPONSE_OK)

    def on_copy_activate(self, widget):
        self.address.copy_clipboard()

    def on_cut_activate(self, widget):
        self.address.cut_clipboard()

    def on_paste_activate(self, widget):
        self.address.paste_clipboard()

    def on_clear_activate(self, widget):
        self.address.set_text("")

    def on_preferences_activate(self, widget):
        #self.statusMessage("Editing Preferences with Gnome UI not supported yet.")
        from prefs import PreferencesDialog
        p = PreferencesDialog(self.xml.get_widget("callwindow"), self, self.app.getOptions())
        p.show()

    def on_debugmenu_activate(self, widget):
        self.debugwindow.show_all()

    def on_debugmenu_close(self, widget):
        self.debugwindow.hide_all()

    def on_dtmfmenu_activate(self, widget):
        self.dtmfwindow.show_all()

    def on_dtmfmenu_close(self, widget):
        self.dtmfwindow.hide_all()

    def on_lookup_clicked(self, w):
        from addressedit import AddressBook
        self.addressedit = AddressBook(self)
        self.addressedit.show()

    def on_quit_activate(self, widget):
        reactor.stop()

    def on_about_activate(self, widget):
        self.xml.get_widget("about").show()

    # event callbacks
    def callConnected(self, cookie):
        self.statusMessage("Call Connected")

    def callDisconnected(self, cookie, reason):
        self.cookie = None
        self.hangupButton.set_sensitive(0)
        self.address.set_sensitive(1)
        self.callButton.set_sensitive(1)
        print "closed: ", reason

    def callStarted(self, cookie):
        self.cookie = cookie
        self.hangupButton.set_sensitive(1)

    def callFailed(self, reason):
        self.statusMessage("Call failed: %s" % reason.value)
        self.hangupButton.set_sensitive(0)
        self.callButton.set_sensitive(1)
        self.address.set_sensitive(1)

    def incomingCall(self, description, cookie):
        # XXX multiple incoming calls won't work
        p = PopupNotice()
        d = p.popup('Accept call from %s?'%description, buttons=('Yes', 'No'),
                    #timeout = 30000)
                    timeout = 4000)
        self.incoming.append(p)
        d.addCallback(lambda x: self._cbAcceptDone(x, cookie))
        if len(self.incoming) == 1:
            self.incoming[0].start()
        return d

    def _cbAcceptDone(self, result, cookie):
        """Called when user accepts/denies call."""
        from shtoom.exceptions import CallRejected, CallNotAnswered
        del self.incoming[0]
        if result == "Yes":
            self.cookie = self.cookie
            self.callButton.set_sensitive(0)
            self.hangupButton.set_sensitive(1)
            self.address.set_sensitive(0)
            return cookie
        elif result == "No":
            raise CallRejected("no thanks")
        else:
            raise CallRejected("timed out")
        if self.incoming:
            self.incoming[0].start()
        return result

    def debugMessage(self, msg):
        log.msg(msg, system='ui')

    def statusMessage(self, msg):
        self.status.push(0,msg)

    def on_dtmfButton0_pressed(self, widget):
        if self.cookie:
            self.app.startDTMF(self.cookie, '0')
    def on_dtmfButton0_released(self, widget):
        if self.cookie:
            self.app.stopDTMF(self.cookie, '0')

    def on_dtmfButton1_pressed(self, widget):
        if self.cookie:
            self.app.startDTMF(self.cookie, '1')
    def on_dtmfButton1_released(self, widget):
        if self.cookie:
            self.app.stopDTMF(self.cookie, '1')

    def on_dtmfButton2_pressed(self, widget):
        if self.cookie:
            self.app.startDTMF(self.cookie, '2')
    def on_dtmfButton2_released(self, widget):
        if self.cookie:
            self.app.stopDTMF(self.cookie, '2')

    def on_dtmfButton3_pressed(self, widget):
        if self.cookie:
            self.app.startDTMF(self.cookie, '3')
    def on_dtmfButton3_released(self, widget):
        if self.cookie:
            self.app.stopDTMF(self.cookie, '3')

    def on_dtmfButton4_pressed(self, widget):
        if self.cookie:
            self.app.startDTMF(self.cookie, '4')
    def on_dtmfButton4_released(self, widget):
        if self.cookie:
            self.app.stopDTMF(self.cookie, '4')

    def on_dtmfButton5_pressed(self, widget):
        if self.cookie:
            self.app.startDTMF(self.cookie, '5')
    def on_dtmfButton5_released(self, widget):
        if self.cookie:
            self.app.stopDTMF(self.cookie, '5')

    def on_dtmfButton6_pressed(self, widget):
        if self.cookie:
            self.app.startDTMF(self.cookie, '6')
    def on_dtmfButton6_released(self, widget):
        if self.cookie:
            self.app.stopDTMF(self.cookie, '6')

    def on_dtmfButton7_pressed(self, widget):
        if self.cookie:
            self.app.startDTMF(self.cookie, '7')
    def on_dtmfButton7_released(self, widget):
        if self.cookie:
            self.app.stopDTMF(self.cookie, '7')

    def on_dtmfButton8_pressed(self, widget):
        if self.cookie:
            self.app.startDTMF(self.cookie, '8')
    def on_dtmfButton8_released(self, widget):
        if self.cookie:
            self.app.stopDTMF(self.cookie, '8')

    def on_dtmfButton9_pressed(self, widget):
        if self.cookie:
            self.app.startDTMF(self.cookie, '9')
    def on_dtmfButton9_released(self, widget):
        if self.cookie:
            self.app.stopDTMF(self.cookie, '9')

    def on_dtmfButtonHash_pressed(self, widget):
        if self.cookie:
            self.app.startDTMF(self.cookie, '#')
    def on_dtmfButtonHash_released(self, widget):
        if self.cookie:
            self.app.stopDTMF(self.cookie, '#')

    def on_dtmfButtonStar_pressed(self, widget):
        if self.cookie:
            self.app.startDTMF(self.cookie, '*')
    def on_dtmfButtonStar_released(self, widget):
        if self.cookie:
            self.app.stopDTMF(self.cookie, '*')

    def save_preferences(self, options):
        self.app.updateOptions(options)


class DebugTextView:
    MAXLINES = 1000
    DELETECHUNK = 100

    def __init__(self, widget):
        self.buffer = widget
        self.scroll = None

    def set_visible(self, scroll):
        self.scroll = scroll
        if scroll:
            adj = self.scroll.get_vadjustment()
            adj.set_value(adj.upper)

    def write(self, text):
        b = self.buffer
        b.insert(b.get_end_iter(), text)
        lines = b.get_line_count()
        if lines > self.MAXLINES:
            b.delete(b.get_start_iter(),
                     b.get_iter_at_line_offset(self.DELETECHUNK,0))
        if self.scroll is not None:
            adj = self.scroll.get_vadjustment()
            adj.set_value(adj.upper)


    def flush(self):
        pass


