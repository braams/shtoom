import gtk

from shtoom.Options import NoDefaultOption
from twisted.python import log

class PreferencesDialog:
    def __init__(self, parent, main, opts):
        self.parent = parent
        self.main = main
        self.opts = opts

        self.setupDialog(parent)

    def show(self):
        self.dialog.show_all()
        res = self.dialog.run()
        if res == gtk.RESPONSE_ACCEPT:
            self.saveChanges()
        elif res == gtk.RESPONSE_REJECT:
            self.discardChanges()
        else:
            print "unknown response", res
        self.dialog.destroy()

    def saveChanges(self):
        optdict = {}
        for otype, oname, oget in self.widgets:
            if otype != 'Choice':
                oval = oget()
                if oval == gtk.TRUE:
                    oval = True
                if oval == gtk.FALSE:
                    oval = False
            else:
                for c, cget in oget:
                    if cget() == gtk.TRUE:
                        oval = c
                        break
                else:
                    log.err("No choice selected for %s"%oname)
                    raise ValueError
            optdict[oname] = oval
        self.main.save_preferences(optdict)
        del self.widgets

    def discardChanges(self):
        pass

    def setupDialog(self, parent):
        self.dialog = gtk.Dialog("Preferences", parent,
                                 gtk.DIALOG_DESTROY_WITH_PARENT,
                                 (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                                  gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))

        self.widgets = []

        self.tooltips = gtk.Tooltips()

        notebook = gtk.Notebook(spacing=8)
        notebook.set_border_width(4)
        self.dialog.vbox.set_border_width(4)
        self.dialog.vbox.pack_start(notebook)
        #self.dialog.add(vbox)

        for group in self.opts:
            tab = gtk.VBox(spacing=8)
            #print "tab", tab

            for optnumber, option in enumerate(group):
                optBox = gtk.HBox(spacing=8)

                l = gtk.Label(option.getPrettyName())
                self.tooltips.set_tip(l, option.getDescription())
                optBox.pack_start(l, gtk.FALSE, gtk.TRUE)

                if option.optionType in ('String', 'Number', 'Password'):
                    entry = gtk.Entry()
                    if option.optionType == 'Password':
                        entry.set_visibility(gtk.FALSE)

                    val = option.getValue()

                    if val and val is not NoDefaultOption:
                        entry.set_text(str(val))

                    self.tooltips.set_tip(entry, option.getDescription())
                    optBox.pack_end(entry, gtk.FALSE, gtk.TRUE)
                    self.widgets.append((option.optionType,
                                         option.getName(),
                                         entry.get_text))

                elif option.optionType == 'Choice':
                    choices = option.getChoices()
                    lb = None
                    buttons = []
                    for c in choices[::-1]:
                        b = gtk.RadioButton(lb, c)
                        self.tooltips.set_tip(b, option.getDescription())
                        if c == option.getValue():
                            #print "setting", c
                            b.set_active(gtk.TRUE)
                        else:
                            b.set_active(gtk.FALSE)
                        optBox.pack_end(b, gtk.FALSE, gtk.TRUE)
                        buttons.append((c,b.get_active))
                        lb = b
                    b = gtk.RadioButton(lb, 'default')
                    optBox.pack_end(b, gtk.FALSE, gtk.TRUE)
                    buttons.append((NoDefaultOption,b.get_active))
                    self.widgets.append((option.optionType,
                                         option.getName(),
                                         buttons))

                elif option.optionType == 'Boolean':
                    entry = gtk.CheckButton("")
                    self.tooltips.set_tip(entry, option.getDescription())
                    if option.getValue():
                        entry.set_active(gtk.TRUE)
                    else:
                        entry.set_active(gtk.FALSE)
                    optBox.pack_end(entry, gtk.FALSE, gtk.TRUE)
                    self.widgets.append((option.optionType,
                                         option.getName(),
                                         entry.get_active))
                else:
                    print "unknown option", option.optionType

                tab.pack_start(optBox, gtk.FALSE, gtk.FALSE)
            notebook.append_page(tab, gtk.Label(group.getName()))
