# Copyright (C) 2004 Anthony Baxter

from twisted.python import log

class ShtoomBaseUI:
    """ Common code for all userinterfaces """

    def connectApplication(self, application):
        self.app = application

    def resourceUsage(self):
        try:
            import resource
        except ImportError:
            return
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        print "%fs user, %fs system"%(rusage[0], rusage[1])
