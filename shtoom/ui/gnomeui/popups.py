
# Based on code originally by Glyph 

import gobject
import gtk
import gtk.gdk

import sys

OUT = 1
IN = 2

class mover:
    def __init__(self, popup, timeout=5000):
        self.win = popup.w
        self.timeout = timeout
        wwidth, wheight = self.win.get_size()
        popup.mover = self
        self.startx = gtk.gdk.screen_width() - wwidth  -10
        self.starty = gtk.gdk.screen_height()
        self.endx = gtk.gdk.screen_width() - wwidth - 10
        self.endy = gtk.gdk.screen_height() - wheight  -10
        self.xincr = -cmp(self.startx, self.endx) * 2
        self.yincr = -cmp(self.starty, self.endy) * 2
        self.state = OUT

    def move(self):
        if not self.win:
            return
        curx, cury = self.win.get_position()
        if self.state == OUT:
            curx += self.xincr
            cury += self.yincr
            if cury <= self.endy and curx <= self.endx:
                self.state = IN
                if self.timeout:
                    gobject.timeout_add(self.timeout, self.move)
            else:
                gobject.timeout_add(5, self.move)
        elif self.state == IN:
            curx -= self.xincr
            cury -= self.yincr
            if cury <= self.starty:
                gobject.timeout_add(10, self.move)
            else:
                self.win = None
                return
        self.win.move(curx, cury)

    def start(self):
        self.win.move(self.startx, self.starty)
        self.move()

    def hide(self):
        self.xincr *= 3
        self.yincr *= 3
        self.move()

class PopupNotice:
    def __init__(self):
        self.mover = None
        self.w = None
        self.deferred = None

    def popup(self, text, buttons=('OK',)):
        from twisted.internet import defer
        self.deferred = defer.Deferred()
        self.w = gtk.Window(gtk.WINDOW_POPUP)
        frame = gtk.Frame("Shtoom - Notice")
        self.w.add(frame)
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
            button.connect('clicked', lambda x,b=b: self.hide_dialog(b,x))
            hbox.pack_start(button, False, False, 0)
        self.w.resize(200, 150)
        self.w.show_all()
        return self.deferred

    def hide_dialog(self, button, event):
        if self.mover:
            self.mover.hide()
        self.mover = None
        self.deferred.callback(button)

def done(*args):
    from twisted.internet import reactor
    print "third dialog got %s"%(args,)
    reactor.stop()

def testrun3(*args):
    print "second dialog got %s"%(args,)
    p = PopupNotice()
    d = p.popup('this is a notice\nwith three buttons', buttons=('Yes','No','Maybe'))
    mover(p).start()
    d.addCallback(done)

def testrun2(*args):
    print "first dialog got %s"%(args,)
    p = PopupNotice()
    d = p.popup('this is a notice with two buttons', buttons=('Yes','No'))
    mover(p).start()
    d.addCallback(testrun3)

def testrun():
    p = PopupNotice()
    d = p.popup('this is a notice with an ok button')
    mover(p).start()
    d.addCallback(testrun2)

if __name__ == "__main__":
    from twisted.internet import gtk2reactor
    gtk2reactor.install()
    import pygtk
    import gnome
    global gnomeProgram
    gnomeProgram = gnome.init("popups", "Whatever Version")
    from twisted.internet import reactor
    reactor.callLater(0, testrun)
    reactor.run()
