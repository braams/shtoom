
from shtoom.ui.slider import ISlidable, Slider


class GtkSlidingWindow:
    __implements__ = (ISlidable,)

    def getScreenSize(self):
        import gtk.gdk
        return gtk.gdk.screen_width(), gtk.gdk.screen_height()

    def getWindowSize(self):
        return self.win.get_size()

    def getPosition(self):
        return self.win.get_position()

    def movePosition(self, (x, y)):
        print "moving to", x, y
        self.win.move(x, y)
        self.win.show_all()

    def windowShown(self):
        pass

    def windowHidden(self):
        pass

    def callLater(self, time, callable, *args):
        #import gobject
        #gobject.timeout_add(int(time*1000), lambda args=args:callable(*args))
        return reactor.callLater(time, callable, *args)



def demo():
    from twisted.internet import reactor, tksupport
    from shtoom.ui.slider import SliderDemo
    import gtk

    class GtkDemoWindow(GtkSlidingWindow):
        def __init__(self, parent):
            self.parent = parent
            self.win = gtk.Window(gtk.WINDOW_POPUP)
            self.frame = gtk.Frame("Shtoom - Notice")
            self.frame.set_border_width(8)
            vbox = gtk.VBox(False,2)
            vbox.set_border_width(8)
            self.frame.add(vbox)
            self.label = gtk.Label(' '*25)
            vbox.pack_start(self.label)
            # Standard message dialog
            hbox = gtk.HBox(False, 5)
            vbox.pack_start(gtk.HSeparator(), False, False, 0)
            button = gtk.Button('Ok')
            button.connect('clicked', lambda x: self.slider.hide())
            hbox.pack_start(button, False, False, 0)
            vbox.pack_start(hbox, expand=False)
            self.win.add(self.frame)
            self.win.resize(200, 150)
            print "done", self.win
            self.win.show()

        def demoText(self, text):
            self.label.set_text(text)

        def setSlider(self, slider):
            self.slider = slider

    demo = SliderDemo(GtkDemoWindow)
    demo.demo()

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

    reactor.callLater(0, demo)
    reactor.run()
