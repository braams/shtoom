## Interfaces for address books and entries
## Author: Casper Wilstrup

from twisted.python.components import Interface

class AddressEntry(Interface):
    """Interface for address entries in address books."""
    def isreadonly(self):
        """Indicate whether this address is editable. LDAP and other
           address sources may not be editable by the user"""

    def sip(self):
        """Return the sip address of the contact"""

    def realname(self):
        """Return the real name of the contact"""

    def nickname(self):
        """Return the nickname of the contact"""

    def givenname(self):
        """Return the first (given) names for the contact"""

    def surname(self):
        """Return the surname of the contact"""

    def organization(self):
        """Return the organization this contact is associated with"""

    ## Functions for editing the user entry. Raises exceptions if entry in r/o
    def setsip(self):
        """Set the sip address of the contact"""

    def setrealname(self):
        """Set the real name of the contact"""

    def setnickname(self):
        """Set the nickname of the contact"""

    def setgivenname(self):
        """Set the first (given) names for the contact"""

    def setsurname(self):
        """Set the surname of the contact"""

    def setorganization(self):
        """Set the organization this contact is associated with"""



class AddressBook(Interface):
    """Interface for actual address book implementations. All address books inherit
       from this interface"""

    def prefix(self):
        """Several address books can be distinguished from each other by a specific
           prefix, eg 'ldap:peter' would lookup in the LDAP address book, while
           'evo:peter' would lookup in the Evolution address book. The value 'sip'
           is obviously reserved"""

    def bookname(self):
        """Returns a descriptive name for the address book, eg. "Evolution contacts"
           or similar"""

    def isreadonly(self):
        """Indicate whether this address book supports adding and deleting
           address book entries"""

    def cansuggest(self):
        """Indicates whether this book allows suggest calls. Some books may simply
           chose to disallow this if the operation would be too expensive"""

    def lookup(self,key):
        """Returns an AddressEntry by looking up the address as entered by a user"""

    def suggest(self,key):
        """Return list of possible completions for a key partially entered by the user"""

    def __iter__(self):
        """Return an iterator to iterate over all entries"""

    ## The following are only usable if class is not readonly

    def delentry(self,entry):
        """Delete an entry from the address book"""

    def newentry(self):
        """Return a new blank entry for the address book"""

    def savebook(self):
        """Write the book contents to persistent storage"""
