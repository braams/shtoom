# Copyright (C) 2003 Anthony Baxter

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
        self.openDev()
        self._closed = False

    def read(self, bytes):
        return self.dev.read(bytes)

    def write(self, data):
        return self.dev.write(data)

    def isClosed(self):
        return self._closed

    def openDev(self):
        raise NotImplementedError

