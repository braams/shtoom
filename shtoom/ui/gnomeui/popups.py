
# Based on code originally by Glyph


import sys

OUT = 1
IN = 2

class PopupNotice:
    def __init__(self):
        self.w = None
        self.deferred = None

    def popup(self, text, buttons=('OK',), timeout=5000):
        import gtk, gtk.gdk
        from twisted.internet import defer
        self.deferred = defer.Deferred()
        self.win = gtk.Window(gtk.WINDOW_POPUP)
        frame = gtk.Frame("Shtoom - Notice")
        frame.set_border_width(8)
        self.win.add(frame)
        vbox = gtk.VBox(False,2)
        vbox.set_border_width(8)
        frame.add(vbox)
        label = gtk.Label(text)
        vbox.pack_start(label)
        # Standard message dialog
        hbox = gtk.HBox(False, 5)
        vbox.pack_start(gtk.HSeparator(), False, False, 0)
        vbox.pack_start(hbox, expand=False)
        for b in buttons:
            button = gtk.Button(b)
            button.connect('clicked', lambda x,b=b: self.button_click(b,x))
            hbox.pack_start(button, False, False, 0)
        self.win.resize(200, 150)
        self.win.show_all()
        self.timeout = timeout
        wwidth, wheight = self.win.get_size()
        self.startx = gtk.gdk.screen_width() - wwidth  -10
        self.starty = gtk.gdk.screen_height()
        self.endx = gtk.gdk.screen_width() - wwidth - 10
        self.endy = gtk.gdk.screen_height() - wheight  -10
        self.xincr = -cmp(self.startx, self.endx) * 2
        self.yincr = -cmp(self.starty, self.endy) * 2
        self.state = OUT
        return self.deferred

    def _move(self):
        import gobject
        if not self.win:
            return
        curx, cury = self.win.get_position()
        if self.state == OUT:
            curx += self.xincr
            cury += self.yincr
            if cury <= self.endy and curx <= self.endx:
                self.state = IN
                if self.timeout:
                    gobject.timeout_add(self.timeout, self._timedout)
            else:
                gobject.timeout_add(5, self._move)
        elif self.state == IN:
            curx -= self.xincr
            cury -= self.yincr
            if cury <= self.starty:
                gobject.timeout_add(10, self._move)
            else:
                self.win = None
                return
        self.win.move(curx, cury)

    def _timedout(self):
        if self.deferred:
            self._move()
            self.deferred.callback(None)

    def start(self):
        self.win.move(self.startx, self.starty)
        self._move()

    def _hide(self):
        self.xincr *= 3
        self.yincr *= 3
        self._move()

    def button_click(self, button, event):
        self._hide()
        self.deferred.callback(button)
        self.deferred = None

def done(*args):
    from twisted.internet import reactor
    print "third dialog got %s"%(args,)
    reactor.stop()

def testrun3(*args):
    print "second dialog got %s"%(args,)
    p = PopupNotice()
    d = p.popup('this is a notice\nwith three buttons',
                                buttons=('Yes','No','Maybe'))
    p.start()
    d.addCallback(done)

def testrun2(*args):
    print "first dialog got %s"%(args,)
    p = PopupNotice()
    d = p.popup('this is a notice with two buttons\n(and no timeout)',
                    buttons=('Yes','No'), timeout = 0)
    p.start()
    d.addCallback(testrun3)

def testrun():
    p = PopupNotice()
    d = p.popup('this is a notice with an ok button')
    p.start()
    d.addCallback(testrun2)

if __name__ == "__main__":
    import pygtk
    pygtk.require("2.0")
    from twisted.internet import gtk2reactor
    gtk2reactor.install()
    import gobject
    import gtk
    import gtk.gdk
    pygtk.require("2.0")
    import gobject
    import gtk
    import gtk.gdk
    import gnome
    global gnomeProgram
    gnomeProgram = gnome.init("popups", "Whatever Version")
    from twisted.internet import reactor
    reactor.callLater(0, testrun)
    reactor.run()
