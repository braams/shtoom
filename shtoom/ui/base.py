# Copyright (C) 2004 Anthony Baxter

from twisted.python import log

class ShtoomBaseUI:
    """ Common code for all userinterfaces """

    def connectApplication(self, application):
        self.app = application

