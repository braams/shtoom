"""Class to perform address lookups."""

# Author: Casper Wilstrup

class AddrLookup:
    def __init__(self,app):
        self.app = app
        self.bookmap = {}  # A map of all active address books. The map key is the book prefix
        self.booklist = [] # A list of all active address books in priority order

        ## For now just add the default book to the lookup
        import defaultbook
        self.booklist.append(defaultbook.book)
        self.bookmap[defaultbook.book.prefix()] = defaultbook.book

    def _normalizesip(self,sipaddr):
        if not sipaddr.startswith('sip:'):
            sipaddr = 'sip:' + sipaddr
        if sipaddr.find('@')==-1:
            default_domain = self.app.getPref('register_uri')
            if default_domain:
                if default_domain.startswith('sip:'):
                    default_domain = default_domain[4:]
                sipaddr += '@'+default_domain
        return sipaddr

    def lookup(self,key):
        """Used to lookup a valid sip url from a possibly partial one"""
        key = key.strip()
        if key.find(':') == -1:
            ## No specific address book chosen. Lookup in all books
            for book in self.booklist:
                entry = book.lookup(key)
                if entry: return entry.sip()
            ## Not in any book. Return key normalized as sip address
            return self._normalizesip(key)
        else:
            ## User specified book
            prefix = key.split(':')[0]
            if prefix == 'sip': return self._normalizesip(key)
            book = self.bookmap.get(prefix)
            if not book:
                ## User specified book does not exist
                return key
            entry = book.lookup(key)
            if entry: return entry.sip()
            else: return key

        #Can't get here
        return "impossible"

    def suggest(self,url):
        """Used to find possible completions for an entered url"""
        # Stupid implementation so far.
        return self.lookup(url)

    def getactivebooks(self):
        return self.booklist
