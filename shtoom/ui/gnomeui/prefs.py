import gtk

from shtoom.Options import NoDefaultOption

class PreferencesDialog:
    def __init__(self, parent, main, opts):
        self.parent = parent
        self.main = main
        self.opts = opts

        self.setupDialog(parent)

    def show(self):
        self.dialog.show_all()

    def setupDialog(self, parent):
        self.dialog = gtk.Dialog("Preferences", parent,
                                 gtk.DIALOG_DESTROY_WITH_PARENT,
                                 (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                                  gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))

        #vbox = gtk.VBox()
        notebook = gtk.Notebook()
        self.dialog.vbox.pack_start(notebook)
        #self.dialog.add(vbox)

        for group in self.opts:
            tab = gtk.VBox()
            print "tab", tab

            for optnumber, option in enumerate(group):
                optBox = gtk.HBox()

                optBox.pack_start(gtk.Label(option.getPrettyName()), 
                                                        gtk.FALSE, gtk.TRUE)

                if option.optionType in ('String', 'Number', 'Password'):
                    entry = gtk.Entry()
                    if option.optionType == 'Password':
                        entry.set_visibility(gtk.FALSE)

                    val = option.getValue()
                    
                    if val and val is not NoDefaultOption:
                        entry.set_text(str(val))

                    optBox.pack_end(entry, gtk.FALSE, gtk.TRUE)

                elif option.optionType == 'Choice':
                    choices = option.getChoices()
                    lb = None
                    for c in choices[::-1]:
                        b = gtk.RadioButton(lb, c)
                        if c == option.getValue():
                            print "setting", c
                            b.set_active(gtk.TRUE)
                        else:
                            b.set_active(gtk.FALSE)
                        optBox.pack_end(b, gtk.FALSE, gtk.TRUE)
                        lb = b
                elif option.optionType == 'Boolean':
                    entry = gtk.CheckButton("")
                    if option.getValue():
                        entry.set_active(gtk.TRUE)
                    else:
                        entry.set_active(gtk.FALSE)
                    optBox.pack_end(entry, gtk.FALSE, gtk.TRUE)
                else:
                    print "unknown option", option.optionType

                tab.pack_start(optBox, gtk.FALSE, gtk.FALSE)
            notebook.append_page(tab, gtk.Label(group.getName()))
                    
                                  
                
        
                                 
                 
        
