import gtk
import gtk.glade

from twisted.python import util, log
from twisted.internet import reactor, defer
from twisted.python import log

class AddressBook:
    def __init__(self, main):
        self.main = main
        self.xml = gtk.glade.XML(util.sibpath(__file__, "addressbook.glade"))
        self.xml.signal_autoconnect(self)
        self.window = self.xml.get_widget("addressbook")
        self.bookcombo = self.xml.get_widget("bookcombo")
        self.bookinfo = self.xml.get_widget("bookinfo")
        self.addresslist = self.xml.get_widget("addresslist")
        self.entrytreestore = gtk.TreeStore(str)
        self.addresslist.set_model(self.entrytreestore)
        self.addressselection = self.addresslist.get_selection()
        self.addressselection.set_select_function(self.on_selection_change,None)
        self.selpath = (0,)

        # Black treeview magic
        self.tvcolumn = gtk.TreeViewColumn('Column 0')
        self.addresslist.append_column(self.tvcolumn)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)

    def show(self):
        books = self.main.addrlookup.getactivebooks()
        booknames = map(lambda b: b.bookname(),books)
        self.bookcombo.set_popdown_strings(booknames)

        self.window.show()


    # GUI callbacks

    def on_selection_change(self,path, user_data):
        self.selpath = path
        return True

    def reloadlist(self):
        self.entrytreestore.clear()
        if self.book:
            for entry in self.book:
                piter = self.entrytreestore.append(None, [entry.nickname()])
                self.entrytreestore.append(piter,['Name: %s'%entry.realname()])
                self.entrytreestore.append(piter,['Organization: %s'%entry.organization()])
                self.entrytreestore.append(piter,['SIP: %s'%entry.sip()])

    def on_bookcombo_choice(self,item):
        self.book = None

        for book in self.main.addrlookup.getactivebooks():
            if book.bookname() == item.get_text():
                self.book = book
                break
        if self.book:
            if self.book.isreadonly():
                self.xml.get_widget("add").set_sensitive(0)
                self.xml.get_widget("remove").set_sensitive(0)
            else:
                self.xml.get_widget("add").set_sensitive(1)
                self.xml.get_widget("remove").set_sensitive(1)

            self.bookinfo.set_text("%s - prefix '%s:'"%(self.book.bookname(),self.book.prefix()))
            self.reloadlist()

    def on_ok_clicked(self,button):
        iter = self.entrytreestore.get_iter(self.selpath[0])
        nick = self.entrytreestore.get_value(iter,0)
        entry = self.book.lookup(nick)
        self.main.setaddress(entry.sip())
        self.window.hide()
        self.window.destroy()

    def on_cancel_clicked(self,button):
        self.window.hide()
        self.window.destroy()

    def on_add_clicked(self,button):
        entry = self.book.newentry()
        self.entry_editor = EntryEdit(self,self.book,entry)
        self.entry_editor.show()
        self.reloadlist()

    def on_remove_clicked(self,button):
        iter = self.entrytreestore.get_iter(self.selpath[0])
        nick = self.entrytreestore.get_value(iter,0)
        entry = self.book.lookup(nick)
        self.book.delentry(entry)
        self.reloadlist()

    def on_edit_clicked(self,button):
        iter = self.entrytreestore.get_iter(self.selpath[0])
        nick = self.entrytreestore.get_value(iter,0)
        entry = self.book.lookup(nick)
        self.entry_editor = EntryEdit(self,self.book,entry)
        self.entry_editor.show()

    def on_edit_ok_clicked(self,button):
        self.entry_editor.apply()
        self.entry_editor.hide()
        self.reloadlist()

    def on_edit_cancel_clicked(self,button):
        self.entry_editor.hide()


class EntryEdit:
    def __init__(self,parent,book,entry):
        self.parent = parent
        self.book = book
        self.entry = entry
        self.window = self.parent.xml.get_widget("editdialog")
        self.nickentry = self.parent.xml.get_widget("nickentry")
        self.givennameentry = self.parent.xml.get_widget("givennameentry")
        self.surnameentry = self.parent.xml.get_widget("surnameentry")
        self.organizationentry = self.parent.xml.get_widget("organizationentry")
        self.sipentry = self.parent.xml.get_widget("sipentry")
        print self.entry.isreadonly()
        if self.entry.isreadonly():
            for entry in (self.nickentry,self.givennameentry,self.surnameentry,
                          self.organizationentry,self.sipentry):
                entry.set_editable(0)
                entry.set_sensitive(0)

    def show(self):
        self.nickentry.set_text(self.entry.nickname())
        self.givennameentry.set_text(self.entry.givenname())
        self.surnameentry.set_text(self.entry.surname())
        self.organizationentry.set_text(self.entry.organization())
        self.sipentry.set_text(self.entry.sip())
        self.window.show()

    def hide(self):
        self.window.hide()

    def apply(self):
        if self.entry.isreadonly(): return
        self.entry.setnickname(self.nickentry.get_text())
        self.entry.setgivenname(self.givennameentry.get_text())
        self.entry.setsurname(self.surnameentry.get_text())
        self.entry.setorganization(self.organizationentry.get_text())
        self.entry.setsip(self.sipentry.get_text())
        if not self.book.isreadonly():
            self.book.savebook()
