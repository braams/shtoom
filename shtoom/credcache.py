# A credentials cache
# Copyright (C) 2004 Anthony Baxter


class CredCache:

    def __init__(self, app):
        self.app = app
        self._cred = {}

    def loadCreds(self, creds):
        from base64 import decodestring
        for o in creds:
            realm = o.getName()
            dec = decodestring(o.getValue())
            user, password = dec.split(':', 1)
            self._cred[realm] = (user, password)

    def getCred(self, realm):
        if realm in self._cred:
            return self._cred.get(realm)
        else:
            return None

    def addCred(self, realm, user, password, save=False):
        from shtoom.Options import StringOption
        from base64 import encodestring
        self._cred[realm] = (user, password)
        opt = StringOption(realm, 'cred for %s'%realm)
        opt.setValue(encodestring('%s:%s'%(user, password)))
        if not save:
            opt.setDynamic(True)
        cred = self.app.getPref('credentials')
        cred.addOption(opt)
        if save:
            self.app.updateOptions({}, forceSave=True)

