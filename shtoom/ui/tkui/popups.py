
from Tkinter import Toplevel, Tk


class Popup(Toplevel):
    deferred = None
    parent = None

    def __init__(self, parent):
        Toplevel.__init__(self)
        self.initial_focus = self
        self.parent = parent
        self.body()
        self.title('popup window')
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.showWindow()

    def body(self):
        pass

    def cancel(self):
        self.hideWindow()
        if self.deferred:
            d, self.deferred = self.deferred, None
            d.callback(None)

    def selected(self, option):
        self.hideWindow()
        if self.deferred:
            d, self.deferred = self.deferred, None
            d.callback(option)

    def showWindow(self):
        self.transient(self.parent)
        self.geometry("+%d+%d" % (self.parent.winfo_rootx()+50,
                                  self.parent.winfo_rooty()+50))

    def hideWindow(self):
        Toplevel.destroy(self)

    

class Dialog(Popup):

    def __init__(self, parent, deferred, message, buttons):
        self.message = message
        self.buttons = buttons
        self.deferred = deferred
        Popup.__init__(self, parent)

    def body(self):
        from Tkinter import NW, E, Frame, Label, Button
        self.top = Frame(self)
        self.top.grid(row=1,column=1,sticky=E)
        self.label = Label(self.top, text=self.message, justify='center')
        self.label.grid(row=1, column=1, padx=5, pady=5, 
                                    columnspan=len(self.buttons),sticky=NW)
        for n, b in enumerate(self.buttons):
            b = Button(self.top, text=b, command=lambda b=b: self.selected(b))
            b.grid(row=2, column=n, sticky=NW, pady=5, padx=5)
            if self.initial_focus == self:
                self.initial_focus = b
            b.focus_set()

class MovingDialog(Dialog):
    "A Dialog that slides in on the bottom right"
    # XXX Tk doesn't seem to want to allow the geometry to go off-screen :-(
    finalOffset = 10

    def showWindow(self):
        self._x, self._y = self.winfo_width(), self.winfo_height()
        if self._x == 1 or self._y == 1:
            # sometimes we're called before being laid out, argh
            self._x = self._y = None
        # screen size
        self._sx = self.parent.winfo_screenwidth()
        self._sy = self.parent.winfo_screenheight()
        print "screen",(self._sx, self._sy)
        print "window",(self._x, self._y)
        # final positions
        if self._x is not None:
            self._fx = self._sx - self._x - self.finalOffset
            self._fy = self._sy - self._y - self.finalOffset
            print "final",(self._fx, self._fy)
            print "move",(self._sx, self._fy)
            self.geometry("+%d+%d" % (self._sx, self._fy))
        else:
            self.geometry("+%d+%d" % (self._sx, self._sy))
        reactor.callLater(0.02, self._moveWindow)

    def _moveWindow(self):
        if self._x is None:
            x, y = self.winfo_rootx(), self.winfo_rooty()
            self._x, self._y = self.winfo_width(), self.winfo_height()
            self._fx = self._sx - self._x - self.finalOffset
            self._fy = self._sy - self._y - self.finalOffset
            print "final",(self._fx, self._fy)
            newx = self._sx
            newy = self._fy
        else:
            x, y = self.winfo_rootx(), self.winfo_rooty()
            newx, newy = x - 2, y
        print "window/geom", (self._x, self._y),(x,y)
        if newx < self._fx:
            newx = self._fx
        self.geometry("+%d+%d" % (newx, newy))
        if newx >= self._fx:
            print "move",(newx, newy)
            reactor.callLater(0.02, self._moveWindow)
            


    def hideWindow(self):
        Toplevel.destroy(self)



if __name__ == "__main__":
    from twisted.internet.task import LoopingCall
    from twisted.internet import defer
    from twisted.internet import tksupport, reactor

    def mainWindow():
        global main
        main = Tk(className='shtoom')
        tksupport.install(main)

    def optionClicked(option):
        print "got option", option
        reactor.stop()

    def popupWindow():
        d = defer.Deferred()
        popup = Dialog(main, d, 'hello world', ('OK', 'Cancel'))
        d.addCallback(optionClicked)

    def ping():
        print "ping"
    
    p = LoopingCall(ping)
    p.start(0.5)
    reactor.callLater(0, mainWindow)
    reactor.callLater(1, popupWindow)
    reactor.run()
