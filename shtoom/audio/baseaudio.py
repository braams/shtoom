# Copyright (C) 2004 Anthony Baxter

class AudioDevice(object):
    sink = None

    def __init__(self, mode='ignored'):
        self.openDev()
        self._closed = False

    def set_sink(self, sink):
        """
        The sink object will subsequently receive calls to its handle_data() method.
        """
        self.sink = sink

    def close(self):
        if not self._closed:
            self._closed = True
            self.dev.close()

    def reopen(self):
        self.close()
        print "baseaudio: reopen"
        self.openDev()
        self._closed = False

    def isOpen(self):
        return not self._closed

    def openDev(self):
        raise NotImplementedError
