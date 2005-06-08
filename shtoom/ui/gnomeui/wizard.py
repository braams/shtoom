from shtoom.ui.wizards import IWizardDisplayer, IWizard, IPage
from twisted.internet import defer
import twisted.python.components as tpc

class GnomeWizardDisplay:
    __implements__ = (IWizardDisplayer,)

    def __init__(self, wizard):
        import gtk
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)#, wizard.title)
        self.frame = gtk.Frame('Wizard')
        self.frame.set_border_width(8)
        self.vbox = gtk.VBox()
        self.win.add(self.frame)
        self.win.resize(400,300)
        self.frame.add(self.vbox)
        self.startWizard(wizard)

    def startWizard(self, wizard):
        wizard = IWizard(wizard)
        page = defer.maybeDeferred(wizard.start).addCallback(self._displayNext)

    def _displayPage(self, page):
        import gtk
        self.frame.remove(self.vbox)
        self.getters = {}
        self.vbox = gtk.VBox(False, 8)
        self.vbox.set_border_width(8)
        self.frame.set_label(page.title)
        for elem in page.elements:
            if elem.type == 'Label':
                e = gtk.Label(elem.text)
                e.set_justify(gtk.JUSTIFY_LEFT)
                e.set_line_wrap(gtk.WRAP_WORD)
                self.vbox.pack_start(e, False, False)
            if elem.type in ('Text', 'Password'):
                h = gtk.HBox()
                l = gtk.Label(elem.label)
                h.pack_start(l)
                e = gtk.Entry()
                if elem.type == 'Password':
                    e.set_visibility(gtk.FALSE)
                e.set_text(elem.default)
                h.pack_start(e)
                self.vbox.pack_start(h, False, False)
                self.getters[elem.name] = e.get_text
            if elem.type == 'Choice':
                h = gtk.HBox()
                l = gtk.Label(elem.label)
                h.pack_start(l)
                c = gtk.combo_box_new_text()
                d = -1
                for i, e in enumerate(elem.choices):
                    c.append_text(e)
                    if e == elem.default:
                        d = i
                if d != -1:
                    c.set_active(d)
                h.pack_start(c)
                self.getters[elem.name] = (
                            lambda c=c,l=elem.choices: l[c.get_active()] )
                self.vbox.pack_start(h, False, False)
            if elem.type == 'Boolean':
                e = gtk.CheckButton(elem.label)
                if elem.default:
                    e.set_active(gtk.TRUE)
                else:
                    e.set_active(gtk.FALSE)
                self.getters[elem.name] = (
                        lambda e=e: e.get_active()==gtk.TRUE and True or False )
                self.vbox.pack_start(e, False, False)

        actionBox = gtk.HBox(False, 8)
        actions = list(page.actions)
        actions.reverse()
        for actionText, actionCallable in actions:
            b = gtk.Button(actionText)
            b.connect('clicked', lambda x, c=actionCallable: self._invoke(x,c))
            actionBox.pack_end(b, False, False)
        self.vbox.pack_end(actionBox, False, False)
        self.vbox.pack_end(gtk.HSeparator(), False, False)

        self.frame.add(self.vbox)
        self.win.show_all()

    def _displayNext(self, next):
        if next is None:
            # we're done
            self.destroy()
        elif tpc.implements(next, IPage):
            self._displayPage(next)
        elif tpc.implements(next, IWizard):
            self.startWizard(next)

    def _invoke(self, event, callable):
        values = {}
        for k, v in self.getters.items():
            values[k] = v()
        self.getters = {}
        defer.maybeDeferred(callable, **values).addCallback(self._displayNext)

    def destroy(self):
        self.win.destroy()


def demo():
    from shtoom.ui.demowiz import DemoWizard
    wiz = GnomeWizardDisplay(DemoWizard())

if __name__ == "__main__":
    import pygtk
    pygtk.require("2.0")
    from twisted.internet import gtk2reactor
    gtk2reactor.install()
    from twisted.internet import reactor
    reactor.callLater(0, demo)
    reactor.run()
