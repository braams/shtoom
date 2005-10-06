# Copyright (C) 2005 Anthony Baxter

from twisted.python import log
from shtoom.dbus import *

def start(app='phone', remote=None):
    if not isAvailable():
        log.msg('dbus support not available', system='dbus')
        return
    if remote is None:
        rem = remoteObjects.get(app)
        if rem is None:
            log.msg('no dbus interface available for app %s'%app, system='dbus')
            return
    else:
        rem = remote
    ssp = rem.ShtoomServicePath
    sessionBus = SessionBus()
    service = Service(ssp, bus=sessionBus)
    remobj = rem(service)
    return remobj


from shtoom.ipc.rpc import PhoneRPC
phonerpc = PhoneRPC()

class ShtoomPhoneRemote(Object):
    ShtoomServiceName = phonerpc.name
    ShtoomServicePath = 'net.shtoom.%s'%(ShtoomServiceName,)

    def __init__(self, service, phonerpc=phonerpc):
        self.phonerpc = phonerpc
        Object.__init__(self, '/%s'%(self.ShtoomServiceName,), service)

    def call(self, uri):
        from __main__ import app
        return app.ipcCommand('call', uri)
    call = method(ShtoomServicePath)(call)

    def hangup(self, uri):
        from __main__ import app
        return app.ipcCommand('hangup', uri)
    hangup = method(ShtoomServicePath)(hangup)


remoteObjects = dict(phone=ShtoomPhoneRemote)
