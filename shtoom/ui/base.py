# Copyright (C) 2004 Anthony Baxter

from twisted.python import log

class ShtoomBaseUI:
    """ Common code for all userinterfaces """

    def connectSIP(self):
        from shtoom import prefs
        from twisted.internet import reactor
        from shtoom import sip
        p = sip.SipPhone(self)
        self.sip = p
        self.sipListener = reactor.listenUDP(prefs.localport or 5060, p)
        log.msg('sip listener installed')

    def resourceUsage(self):
        import resource
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        print "%fs user, %fs system"%(rusage[0], rusage[1])
