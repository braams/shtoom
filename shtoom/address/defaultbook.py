## Implementation of the stupid default Shtoom address book
## Author: Casper Wilstup

from addrinterface import AddressEntry, AddressBook
from ConfigParser import SafeConfigParser
import os
import os.path

class DefaultBookEntry:
    __implements__ = (AddressEntry)
    _startReactor = True

    def __init__(self,book,name,settings=[]):
        self.book = book
        self._values = {'nick': name}

        for key,val in settings:
            self._values[key]=val

    def isreadonly(self):
        return False

    def sip(self):
        return self._values.get('sip','sip:<not available>')

    def nickname(self):
        return self._values.get('nick','')

    def givenname(self):
        return self._values.get('givenname','')

    def surname(self):
        return self._values.get('surname','')

    def realname(self):
        return "%s %s"%(self._values.get('givenname',''),self._values.get('surname',''))

    def organization(self):
        return self._values.get('organization','')

    def setnickname(self,nick):
        del self.book.entries[self._values['nick']]
        self._values['nick']=nick
        self.book.entries[nick] = self

    def setgivenname(self,name):
        self._values['givenname']=name

    def setsurname(self,name):
        self._values['surname']=name

    def setorganization(self,org):
        self._values['organization']=org

    def setsip(self,sip):
        self._values['sip']=sip


class DefaultBook:
    __implements__ = (AddressBook)
    _startReactor = True

    def __init__(self):
        self.entries = {}
        self.cfg = SafeConfigParser()
        try:
            self._filename = os.path.expanduser('~/.shtoombook')
        except:
            self._filename = '%s/.shtoombook'%os.getcwd()
        self.cfg.read([self._filename])

        for name in self.cfg.sections():
            entry = DefaultBookEntry(self,name,self.cfg.items(name))
            self.entries[name]=entry


    def prefix(self):
        return "addr"

    def bookname(self):
        return "Shtoom Address Book"

    def isreadonly(self):
        return False

    def cansuggest(self):
        return True

    def lookup(self,key):
        return self.entries.get(key)

    def suggest(self,key):
        return []

    def __iter__(self):
        return self.entries.values().__iter__()

    def newentry(self):
        i=0
        nick = "unnamed"
        while nick in self.entries.keys():
            i+=1
            nick = "unnamed-%i"%i
        entry = DefaultBookEntry(self,nick)
        self.entries[nick]=entry
        return entry

    def delentry(self,entry):
        nick = entry.nickname()
        del self.entries[nick]
        self.savebook()

    def savebook(self):
        parser = SafeConfigParser()
        for entry in self.entries.values():
            section = entry.nickname()
            parser.add_section(section)
            parser.set(section,"givenname",entry.givenname())
            parser.set(section,"surname",entry.surname())
            parser.set(section,"organization",entry.organization())
            parser.set(section,"sip",entry.sip())
        file = open(self._filename,"w")
        parser.write(file)
        file.close()

book = DefaultBook()
