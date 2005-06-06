
from Tkinter import *
from twisted.python import log

from shtoom.ui.base import ShtoomBaseUI
from shtoom.exceptions import CallRejected

from addressedit import AddressBook

#class AuthDialog(Dialog):
#
#    def __init__(self, prompt, parent):
#
#        Dialog.__init(self, parent, 'Authentication Required')

from shtoom.ui.logo import b64logo

class ShtoomMainWindow(ShtoomBaseUI):
    def __init__(self):
        self.cookie = None
        self._muted = False
        self._connected = False

        self.main = Tk(className='shtoom')

        # Setup the menu bar
        self._menu = Menu(self.main)
        self.main.config(menu=self._menu)
        filemenu = Menu(self._menu)
        filemenu.add_command(label=_("Exit"), command = self.shutdown)
        self._menu.add_cascade(label=_("File"), menu=filemenu)

        editmenu = Menu(self._menu)
        editmenu.add_command(label=_("Preferences"), command = self.prefmenuitem_selected)
        self._menu.add_cascade(label=_("Edit"), menu=editmenu)

        helpmenu = Menu(self._menu)
        helpmenu.add_command(label=_("About"))
        self._menu.add_cascade(label=_("Help"), menu=helpmenu)

        # also do hangup, shutdown reactor, &c
        self.main.protocol("WM_DELETE_WINDOW", self.shutdown)
        self._top1 = Frame(self.main)
        self._top1.grid(row=1, column=1, sticky=NW)
        self._label1 = Label(self._top1, text=_('Address')+':')
        self._label1.grid(row=1,column=1, sticky=W)
        self._urlentry = Entry(self._top1, width=60)
        self._urlentry.grid(row=1, column=2, columnspan=4, sticky=W)
        self._urlentry.bind('<Return>', self.callButton_clicked)
        self._urlentry.focus_set()
        self._addrButton = Button(self._top1, text="...", command=self.addrButton_clicked)

        self._addrButton.grid(row=1, column=6, sticky=E)
        self._img = PhotoImage(data=b64logo)
        self._logo = Label(self._top1, image=self._img)
        self._logo.grid(row=1, column=7, rowspan=2, sticky=NE)

        self._top3 = Frame(self._top1)
        self._callButton = Button(self._top3, text=_("Call"),
                                  command=self.callButton_clicked)
        self._callButton.grid(row=1, column=1, sticky=NW)
        self._hangupButton = Button(self._top3, text=_("Hang Up"),
                                    command=self.hangupButton_clicked,
                                    state=DISABLED)
        self._hangupButton.grid(row=1, column=2, sticky=NW)
        self._registerButton = Button(self._top3, text=_("Register"),
                                  command=self.registerButton_clicked)
        self._registerButton.grid(row=1, column=3, sticky=NW)
        self._muteButton = Checkbutton(self._top3, text=_("Mute"),
                                  variable=self._muted,
                                  command=self.muteButton_clicked)
        self._muteButton.grid(row=1, column=4, sticky=W)
        self._top3.grid(row=2,column=1,columnspan=2, sticky=NW)
        self._statusF = Frame(self._top1)
        self._statusL = Label(self._statusF, text='%s:'%(_("Status"),))
        self._statusL.grid(column=1,row=1,sticky=W)
        self._statusW = Label(self._statusF, text="")
        self._statusW.grid(column=2,row=1,sticky=W)
        self._statusF.grid(row=2, column=4, columnspan=4, sticky=W)

        self._top2 = Frame(self.main)
        self._buttonF = Frame(self._top2)
        self._dtmfbuttons = {}
        for row, dtmfs in enumerate(( ( '1', '2', '3' ),
                                      ( '4', '5', '6' ),
                                      ( '7', '8', '9' ),
                                      ( '*', '0', '#' ))):
            for col, dtmf in enumerate(dtmfs):
                button = Button(self._buttonF, text=dtmf, padx=4, pady=2)
                button.bind('<1>', lambda e, d=dtmf: self.startDTMF(d) )
                button.bind('<ButtonRelease-1>', lambda e, d=dtmf: self.stopDTMF(d) )
                button.grid(row=row+1, column=col+1, sticky=NW)
                self._dtmfbuttons[dtmf] = button
        self._buttonF.grid(row=1,column=1, sticky=NW)
        self._debugText = Text(self._top2, width=72, height=7, wrap='char')
        self._debugText.grid(row=1,column=2, sticky='nsew')
        for b in ( '1', '2', '3',  '4', '5', '6' ,  '7', '8', '9', '0', ):
            self._debugText.bind('<KeyPress-KP_%s>'%b,     lambda e, b=b: self.startDTMF(b))
            self._debugText.bind('<KeyRelease-KP_%s>'%b,   lambda e, b=b: self.stopDTMF(b))
        self._debugText.bind('<KeyPress-KP_Multiply>', lambda e, b=b: self.startDTMF('*'))
        self._debugText.bind('<KeyRelease-KP_Multiply>',lambda e, b=b: self.stopDTMF('*'))
        self._debugText.bind('<KeyPress-KP_Enter>',    lambda e, b=b: self.startDTMF('#'))
        self._debugText.bind('<KeyRelease-KP_Enter>',   lambda e, b=b: self.stopDTMF('#'))
        self._top2.grid(row=3,column=1, columnspan=6,sticky='nsew')
        self.main.grid()


    def startDTMF(self, key):
        if self.cookie:
            self.app.startDTMF(self.cookie, key)
        else:
            print "discarding", key

    def stopDTMF(self, key):
        if self.cookie:
            self.app.stopDTMF(self.cookie, key)

    def getMain(self):
        return self.main

    def debugMessage(self, msg):
        self._debugText.insert('end', msg+'\n')
        self._debugText.yview('end')

    def statusMessage(self, msg):
        self._statusW.configure(text=msg)

    def errorMessage(self, message, exc=None):
        log.msg("%s: %s"%(_('ERROR'), message), system='ui')

    def callButton_clicked(self, evt=None):
        sipURL = self._urlentry.get()
        sipURL = self.addrlookup.lookup(sipURL)
        self.doCall(sipURL)

    def doCall(self, sipURL):
        self._urlentry.delete(0,END)
        self._urlentry.insert(0,sipURL)
        self._callButton.config(state=DISABLED)
        deferred = self.app.placeCall(sipURL)
        deferred.addCallbacks(self.callStarted, self.callFailed).addErrback(log.err)

    def registerButton_clicked(self, evt=None):
        self.app.register()

    def callConnected(self, cookie):
        self.statusMessage(_("Call Connected"))
        self._connected = True
        if self._muted:
            self.app.muteCall(self.cookie)

    def callDisconnected(self, cookie, message):
        status = _("Call Disconnected")
        self._connected = False
        if message:
            lines = message.split('\n')
            message = message[0]
            if len(message) > 30:
                message = message[:30]
            status = "%s: %r"%(status, message)
        self.statusMessage(status)
        self._hangupButton.config(state=DISABLED)
        self._callButton.config(state=NORMAL)
        self.cookie = None

    def callStarted(self, cookie):
        self.cookie = cookie
        self._hangupButton.config(state=NORMAL)

    def callFailed(self, e, message=None):
        self.statusMessage("%s %s"%(_("Call Failed"), e.getErrorMessage()))
        self._connected = False
        self._hangupButton.config(state=DISABLED)
        self._callButton.config(state=NORMAL)
        self.cookie = None

    def hangupButton_clicked(self):
        self.app.dropCall(self.cookie)
        self._callButton.config(state=NORMAL)
        self._hangupButton.config(state=DISABLED)
        self.cookie = False

    def muteButton_clicked(self):
        self._muted = not self._muted
        if self._connected:
            if self._muted:
                self.app.muteCall(self.cookie)
            else:
                self.app.unmuteCall(self.cookie)


    def shutdown(self):
        # XXX Hang up any calls
        from twisted.internet import reactor
        reactor.stop()
        self.main.quit()

    def getAuth(self, method, realm):
        from popups import AuthDialog
        from twisted.internet import defer

        d = defer.Deferred()
        auth = AuthDialog(self.main, d, method, realm)
        return d

    def incomingCall(self, description, cookie):
        return self.popupIncoming(description, cookie)

    def popupIncoming(self, description, cookie):
        import popups
        from twisted.internet import defer
        d = defer.Deferred()
        popup = popups.Dialog(self.main, d,
                              "Incoming Call: %s\nAnswer?"%description,
                              ("Yes", "No"),)
        d.addCallback(lambda x: self._cb_popupIncoming(x, cookie))
        return d

    def _cb_popupIncoming(self, answer, cookie):
        if answer == 'Yes':
            self.cookie = cookie
            self._callButton.config(state=DISABLED)
            return cookie
        else:
            return CallRejected('no thanks', cookie)

    def addrButton_clicked(self):
        dlg = AddressBook(self.main,self)

    def prefmenuitem_selected(self):
        from prefs import PreferencesDialog
        self._p = PreferencesDialog(self.main, self, self.app.getOptions())

    def updateOptions(self, od):
        self.app.updateOptions(od)

    def getLogger(self):
        return Logger(self._debugText)

    def ipcCommand(self, command, args):
        if command == 'call':
            if self.cookie is None:
                sipURL = args
                self.doCall(sipURL)
                return _('Calling')
            else:
                return _('Already on a call')
        elif command == 'hangup':
            if self.cookie is not None:
                self.hangupButton_clicked()
                return _('Hung up call')
            else:
                return _('No active call')
        elif command == 'accept':
            return _('Not implemented')
        elif command == 'reject':
            return _('Not implemented')
        elif command == 'quit':
            self.shutdown()
        else:
            log.msg('IPC got unknown message %s (args %r)'%(command, args))

class Logger:
    def __init__(self, textwidget):
        self._t = textwidget
    def flush(self):
        pass
    def write(self, text):
        self._t.insert('end', text+'\n')
        self._t.yview('end')
