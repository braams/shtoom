# Copyright (C) 2004 Anthony Baxter

class AudioDevice(object):
    def __init__(self, mode='ignored'):
        self.openDev()
        self._closed = False

    def close(self):
        if not self._closed:
            self._closed = True
            self.dev.close()

    def reopen(self):
        print "baseaudio: reopen"
        self.openDev()
        self._closed = False

    def isClosed(self):
        return self._closed

    def openDev(self):
        raise NotImplementedError
