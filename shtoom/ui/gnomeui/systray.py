
# Code for a system tray icon under Gnome. Yay for Gajim, whose source
# showed me the way to do this.

import gtk
from egg import trayicon
from twisted.python.util import sibpath

_ = lambda x:x

class SysTray:

    def __init__(self, ui):
        self.ui = ui
        self.t = trayicon.TrayIcon('ShtoomPhone')
        eb = gtk.EventBox()
        self.t.add(eb)
        self.img = gtk.Image()
        self.img.set_from_file(sibpath(__file__, "shtoomicon.png"))
        eb.add(self.img)
        eb.connect('button-press-event', self.on_clicked)
        self.t.show_all()

    def on_clicked(self, widget, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            menu = gtk.Menu()
            menuItems = [ ]
            if self.ui and self.ui.hidden:
                menuItems.append((_('Show Shtoom'), self.ui.showMainWindow))
            else:
                menuItems.append((_('Hide Shtoom'), self.ui.hideMainWindow))
            if self.ui and self.ui.cookie:
                menuItems.append((_('Hangup'), self.ui.on_hangup_clicked))
            menuItems.append((_('Preferences'),self.ui.on_preferences_activate))
            menuItems.append((_('Quit'), self.ui.on_quit_activate))
            for text, action in menuItems:
                mi = gtk.MenuItem(text)
                mi.connect('activate', action)
                menu.add(mi)
                mi.show()
            menu.popup(None, None, None, event.button, event.time)


if __name__ == "__main__":
    class FakeUI:
        hidden = False
        cookie = '1'
        def showMainWindow(self, w): pass
        def hideMainWindow(self, w): pass
        def on_hangup_clicked(self, w): pass
        def on_preferences_activate(self, w): pass
        def on_quit_activate(self, w): pass

    t = SysTray(ui=FakeUI())
    gtk.main()
