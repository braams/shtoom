from twisted.web import xmlrpc, server
from twisted.python import log

class ShtoomPhoneRemoteXMLRPC(xmlrpc.XMLRPC):
    "XMLRPC interface for the phone"
    def __init__(self):
        from twisted.internet import reactor
        from __main__ import app

        port = app.getPref('xmlrpc_port')
        if port:
            self.listener = reactor.listenTCP(port, server.Site(self))

    def xmlrpc_call(self, uri):
        "make a call"
        from __main__ import app
        return app.ipcCommand('call', uri)

    def xmlrpc_hangup(self, uri):
        "hangup current call"
        from __main__ import app
        return app.ipcCommand('hangup', uri)

remoteObjects = dict(phone=ShtoomPhoneRemoteXMLRPC)
