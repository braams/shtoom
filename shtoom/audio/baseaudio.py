# Copyright (C) 2004 Anthony Baxter

class AudioDevice(object):
    encoder = None

    def __init__(self, mode='ignored'):
        self.openDev()
        self._closed = False

    def set_encoder(self, encoder):
        """
        The encoder object will subsequently receive calls to its 
        handle_audio() method when audio is available - it passes it on 
        to the rest of the system (eventually, to the network).
        """
        self.encoder = encoder

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
