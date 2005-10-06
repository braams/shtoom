

class RPC:
    """ This class should be subclassed to define an RPC interface. RPC methods
        start with 'rpc_'. You should also override the 'name' attribute.

        See the PhoneRPC object, below, for an example.
    """
    name = 'undefined'

    def getMethods(self)
        d = {}
        for attr in dir(self):
            if attr.startswith('rpc_'):
                method = attr[4:]
                d[method] = getattr(self, attr)
        return d


class PhoneRPC:
    "RPC interface for the phone"
    name = 'ShtoomPhone'

    def rpc_call(self, uri):
        "make a call"
        from __main__ import app
        return app.ipcCommand('call', uri)

    def rpc_hangup(self, uri):
        "hangup current call"
        from __main__ import app
        return app.ipcCommand('hangup', uri)

