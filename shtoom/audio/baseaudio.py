# Copyright (C) 2004 Anthony Baxter

class AudioDevice(object):
    def __init__(self, mode, wrapped=1):
        self._mode = mode
        self._wrapped = wrapped
        self.openDev()
        self._closed = False

    def close(self):
        if not self._closed:
            self._closed = True
            self.dev.close()

    def reopen(self):
        print "audio: reopen"
        self.openDev()
        self._closed = False

    def read(self):
        return self.dev.read()

    def write(self, packet):
        return self.dev.write(packet)

    def isClosed(self):
        return self._closed

    def openDev(self):
        raise NotImplementedError

    def selectDefaultFormat(self, format):
        return self.dev.selectDefaultFormat(format)
