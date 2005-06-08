import gtk

from shtoom.Options import NoDefaultOption, getPrettyName
from twisted.python import log

from gettext import gettext as _

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
            oval = oget()
            if oval == True:
                oval = True
            if oval == False:
                oval = False
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

        notebook = gtk.Notebook()
        notebook.set_border_width(4)
        self.dialog.vbox.set_border_width(4)
        self.dialog.vbox.pack_start(notebook)
        #self.dialog.add(vbox)

        for group in self.opts:
            if not group.getGUI():
                continue
            tab = gtk.VBox(False,8)
            tab.set_border_width(8)
            #print "tab", tab
            desc = gtk.Label(group.description)
            tab.pack_start(desc, False, False)

            for optnumber, option in enumerate(group):
                optBox = gtk.HBox(spacing=8)

                l = gtk.Label(getPrettyName(option))
                self.tooltips.set_tip(l, option.description)
                optBox.pack_start(l, False, True)

                if option.type in ('String', 'Integer', 'Password'):
                    entry = gtk.Entry()
                    if option.type == 'Password':
                        entry.set_visibility(False)

                    val = option.value

                    if val and val is not NoDefaultOption:
                        entry.set_text(str(val))

                    self.tooltips.set_tip(entry, option.description)
                    optBox.pack_end(entry, False, True)
                    self.widgets.append((option.type,
                                         option.name,
                                         entry.get_text))

                elif option.type == 'Choice':
                    choices = option.getChoices()
                    combo = gtk.combo_box_new_text()
                    combo.append_text(_('Select one'))
                    active_num = 0
                    for n, c in enumerate(choices):
                        combo.append_text(c)
                        if c == option.value:
                            active_num = n+1
                    combo.set_active(active_num)
                    optBox.pack_end(combo, False, True)
                    self.tooltips.set_tip(combo, option.description, None)
                    def getter(combo=combo):
                        model = combo.get_model()
                        active = combo.get_active()
                        if active == 0:
                            return None
                        return model[active][0]
                    self.widgets.append((option.type,
                                         option.name,
                                         getter))

                elif option.type == 'Boolean':
                    entry = gtk.CheckButton("")
                    self.tooltips.set_tip(entry, option.description)
                    if option.value:
                        entry.set_active(True)
                    else:
                        entry.set_active(False)
                    optBox.pack_end(entry, False, True)
                    self.widgets.append((option.type,
                                         option.name,
                                         entry.get_active))
                else:
                    print "unknown option", option.type

                tab.pack_start(optBox, False, False)
            notebook.append_page(tab, gtk.Label(group.name))
        self.tooltips.enable()
