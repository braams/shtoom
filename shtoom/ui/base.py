# Copyright (C) 2004 Anthony Baxter

from twisted.python import log

from shtoom.address.addrlookup import AddrLookup

class ShtoomBaseUI:
    """ Common code for all userinterfaces """

    # Does this UI need to run by itself in the main thread?
    threadedUI = False

    def connectApplication(self, application):
        self.app = application
        self.addrlookup = AddrLookup(self.app)
