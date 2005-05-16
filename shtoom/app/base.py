
from twisted.python import log

STATE_NONE = 0x0
STATE_SENDING = 0x1
STATE_RECEIVING = 0x2
STATE_BOTH = 0x3
STATE_DONE = 0x4


class BaseApplication:
    """ Base class for all applications. """

    __cookieCount = 0
    _NATMapping = True

    def __init__(self, prefs=None):
        #self._options = _dummy()
        pass

    def boot(self, options=None, args=None):
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

    def getPref(self, pref, default=None):
        if self._options.hasValue(pref):
            return self._options.getValue(pref, default)
        return default

    def updateOptions(self, dict, forceSave=False):
        m = self._options.updateOptions(dict)
        if m or forceSave:
            self._options.saveOptsFile()

    def connectSIP(self):
        from twisted.internet import reactor
        from shtoom import sip
        from shtoom.nat import getMapper
        p = sip.SipProtocol(self)
        self.sip = p
        lport = self.getPref('listenport')
        if lport is None:
            lport = 5060
        self.sipListener = reactor.listenUDP(lport, p)
        listenport = self.sipListener.getHost().port
        if lport == 0:
            self.getOptions().setValue('listenport', listenport, dynamic=True)
        log.msg('sip listener installed on %d'%(listenport), system='app')
        if self._NATMapping:
            getMapper().addCallback(self._cb_mapSipPort)
        else:
            self._cb_mapSipPort(None)

    def _cb_mapSipPort(self, mapper):
        from twisted.internet import reactor
        if mapper:
            mapper.map(self.sipListener)
            t = reactor.addSystemEventTrigger('before',
                                              'shutdown',
                                              self.stopSIP)

    def stopSIP(self):
        from shtoom.nat import getMapper
        log.msg("stopping SIP, and unmapping it (%r)"%(self._NATMapping,))
        if self._NATMapping:
            d = getMapper()
            d.addCallback(self._cb_unmapSipPort).addErrback(log.err)
            return d
        else:
            self._cb_unmapSipPort(None)

    def _cb_unmapSipPort(self, mapper):
        log.msg("unmapping sip using %r"%(mapper,))
        if hasattr(self, 'sipListener'):
            if mapper:
                mapper.unmap(self.sipListener)
            self.sipListener.stopListening()
            del self.sip
            del self.sipListener

    def acceptCall(self, call):
        raise NotImplementedError

    def startCall(self, callcookie, remoteSDP, cb):
        raise NotImplementedError

    def endCall(self, callcookie, reason):
        raise NotImplementedError

    def incomingRTP(self, callcookie, payloadType, payloadData):
        raise NotImplementedError

    def getCookie(self):
        self.__cookieCount += 1
        return "CallCookie%d"%(self.__cookieCount)
