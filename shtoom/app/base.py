
from twisted.python import log

class BaseApplication:
    """ Base class for all applications. """

    __cookieCount = 0

    def __init__(self, prefs=None):
        self.connectSIP()


    def connectPrefs(self, prefs):
        if prefs:
            self._prefs = prefs
        else:
            from shtoom import prefs
            self._prefs = prefs

    def getPref(self, pref):
        return getattr(self._prefs, pref, None)

    def connectSIP(self):
        from shtoom import prefs
        from twisted.internet import reactor
        from shtoom import sip
        p = sip.SipPhone(self)
        self.sip = p
        self.sipListener = reactor.listenUDP(prefs.localport or 5060, p)
        log.msg('sip listener installed')

    def acceptCall(self, callcookie, calldesc):
        raise NotImplementedError

    def startCall(self, callcookie, cb):
        raise NotImplementedError

    def endCall(self, callcookie, reason):
        raise NotImplementedError

    def receiveRTP(self, callcookie, payloadType, payloadData):
        raise NotImplementedError

    def giveRTP(self, callcookie):
        raise NotImplementedError

    def getCookie(self):
        self.__cookieCount += 1
        return "CallCookie%d"%(self.__cookieCount)

