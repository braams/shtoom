
from twisted.python import log

class BaseApplication:
    """ Base class for all applications. """

    __cookieCount = 0

    def __init__(self, prefs=None):
        self._options = _dummy()

    def boot(self):
        self.connectSIP()

    def initOptions(self, options=None):
        import shtoom
        from shtoom.opts import buildOptions
        if options is None:
            options = buildOptions(self)
        options.optionsStartup(version='%%prog %s'%shtoom.Version)
        self._options = options

    def getOptions(self):
        return self._options

    def getPref(self, pref):
        return self._options.getValue(pref, None)

    def updateOptions(self, dict):
        m = self._options.updateOptions(dict)
        if m:
            self._options.saveOptsFile()

    def connectSIP(self):
        from twisted.internet import reactor
        from shtoom import sip
        p = sip.SipPhone(self)
        self.sip = p
        self.sipListener = reactor.listenUDP(self.getPref('listenport') or 5060, p)
        log.msg('sip listener installed')

    def stopSIP(self):
        self.sipListener.stopListening()
        del self.sip
        del self.sipListener

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
