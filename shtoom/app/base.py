
from twisted.python import log

STATE_NONE = 0x0
STATE_SENDING = 0x1
STATE_RECEIVING = 0x2
STATE_BOTH = 0x3
STATE_DONE = 0x4


class BaseApplication:
    """ Base class for all applications. """

    __cookieCount = 0

    def __init__(self, prefs=None):
        #self._options = _dummy()
        pass

    def boot(self):
        self.connectSIP()

    def initOptions(self, options=None, args=None):
        import shtoom
        from shtoom.opts import buildOptions
        if options is None:
            options = buildOptions(self)
        options.optionsStartup(version='%%prog %s'%shtoom.__version__,args=args)
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
        lport = self.getPref('listenport')
        if lport is None:
            lport = 5060
        self.sipListener = reactor.listenUDP(lport, p)
        listenport = self.sipListener.getHost().port
        if lport == 0:
            self.getOptions().setValue('listenport', listenport, dynamic=True)
        log.msg('sip listener installed on %d'%(listenport), system='app')

    def stopSIP(self):
        self.sipListener.stopListening()
        del self.sip
        del self.sipListener

    def acceptCall(self, call):
        raise NotImplementedError

    def startCall(self, callcookie, remoteSDP, cb):
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
