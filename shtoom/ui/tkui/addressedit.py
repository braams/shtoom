# Author: Casper Wilstrup

from twisted.python import util, log
from twisted.internet import reactor, defer
from twisted.python import log

from Tkinter import *
from tkSimpleDialog import Dialog

class AddressBook(Dialog):
    def __init__(self, parent, main):
        self.main = main
        Dialog.__init__(self, parent, title="Address Book")

    def body(self,parent):
        books = self.main.addrlookup.getactivebooks()
        booknames = map(lambda b: b.bookname(),books)

        Label(parent,text="Address Book:").grid(row=0,column=0,sticky=W)
        self._optionvar = StringVar()
        self._optionvar.set(booknames[0])
        self._addroption = OptionMenu(parent,self._optionvar,*booknames)
        self._addroption.grid(row=0,column=1,columnspan=2,sticky=E+W)

        self._addrinfo = Label(parent)
        self._addrinfo.grid(row=1,column=0,columnspan=3,sticky=W)

        self._list = Listbox(parent,width=40)
        self._list.grid(row=2,columnspan=2,rowspan=4,sticky=W+E+N+S)
        self._list.bind("<Button-1>",self.select_addr)

        self._add  = Button(parent,text="+",command=self.add_clicked)
        self._add.grid(row=2,column=2,sticky=W+E)
        self._del  = Button(parent,text="-",command=self.del_clicked)
        self._del.grid(row=3,column=2,sticky=W+E)
        self._edit = Button(parent,text="E",command=self.edit_clicked)
        self._edit.grid(row=4,column=2,sticky=W+E)

        Frame(parent).grid(row=5)
        parent.rowconfigure(5,weight=2)
        parent.pack()
        self._optionvar.trace("w",self.book_changed)
        self.book_changed(None,None,None)

    def book_changed(self,dummy1,dummy2,dummy3):
        bookname = self._optionvar.get()
        self.book = None
        for book in self.main.addrlookup.getactivebooks():
            if book.bookname()==bookname:
                self.book = book
                break
        if self.book:
            self._addrinfo.config(text=self._optionvar.get())
            self.update_list()
            if self.book.isreadonly():
                self._add.config(state=DISABLED)
            else:
                self._add.config(state=ACTIVE)
            self._del.config(state=DISABLED)
            self._edit.config(state=DISABLED)

    def update_list(self):
        self._list.delete(0,END)
        for entry in self.book:
            if entry.realname():
                item = "%s  (%s)"%(entry.nickname(),entry.realname())
            else: item = entry.nickname()
            self._list.insert(END,item)

    def select_addr(self,event):
        if not self.book.isreadonly():
            self._del.config(state=ACTIVE)
        self._edit.config(state=ACTIVE)


    def get_selected_entry(self):
        index = self._list.curselection()
        if len(index)==0: return None
        txt = self._list.get(index[0])
        entryname = txt.split('  (')[0]
        entry = self.book.lookup(entryname)
        return entry

    def add_clicked(self):
        entry = self.book.newentry()
        dlg = EntryEdit(self,self.book,entry)
        self.update_list()

    def del_clicked(self):
        entry = self.get_selected_entry()
        self.book.delentry(entry)
        self.update_list()

    def edit_clicked(self):
        entry = self.get_selected_entry()
        dlg = EntryEdit(self,self.book,entry)
        self.update_list()

    def apply(self):
        entry = self.get_selected_entry()
        if entry:
            self.main._urlentry.delete(0,END)
            self.main._urlentry.insert(0,entry.sip())

class EntryEdit(Dialog):
    def __init__(self,addrdlg,book,entry):
        self.addrdlg = addrdlg
        self.entry = entry
        self.book = book
        Dialog.__init__(self, addrdlg, title="Edit Contact")

    def body(self,parent):
        Label(parent,text="Nickname:").grid(row=0,sticky=W)
        Label(parent,text="Given name:").grid(row=1,sticky=W)
        Label(parent,text="Surname:").grid(row=2,sticky=W)
        Label(parent,text="Organization:").grid(row=3,sticky=W)
        Label(parent,text="SIP:").grid(row=4,sticky=W)

        self._nickname = Entry(parent)
        self._nickname.grid(row=0,column=1,sticky=W+E)
        self._nickname.insert(0,self.entry.nickname())

        self._givenname = Entry(parent)
        self._givenname.grid(row=1,column=1,sticky=W+E)
        self._givenname.insert(0,self.entry.givenname())

        self._surname = Entry(parent)
        self._surname.grid(row=2,column=1,sticky=W+E)
        self._surname.insert(0,self.entry.surname())

        self._organization = Entry(parent)
        self._organization.grid(row=3,column=1,sticky=W+E)
        self._organization.insert(0,self.entry.organization())

        self._sip = Entry(parent,width=30)
        self._sip.grid(row=4,column=1,sticky=W+E)
        self._sip.insert(0,self.entry.sip())

        parent.pack()

    def apply(self):
        self.entry.setnickname(self._nickname.get())
        self.entry.setgivenname(self._givenname.get())
        self.entry.setsurname(self._surname.get())
        self.entry.setorganization(self._organization.get())
        self.entry.setsip(self._sip.get())
        if not self.book.isreadonly():
            self.book.savebook()
