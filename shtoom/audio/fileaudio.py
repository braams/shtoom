# Copyright (C) 2004 Anthony Baxter

from converters import MultipleConv

opened = None

class AudioFromFiles:
    def __init__(self, infile, outfile):
        self.infile = infile
        self.outfile = outfile
        self.reopen()

    def read(self):
        return self._infp.read(320)

    def write(self, bytes):
        return self._outfp.write(bytes)

    def reopen(self):
        self._infp = open(self.infile, 'rb')
        self._outfp = open(self.outfile, 'wb')

    def close(self):
        self._infp.close()
        self._outfp.close()

def getAudioDevice(mode):
    from __main__ import app
    global opened
    if opened is None:
        opened = MultipleConv(AudioFromFiles(app.getPref('audio_infile'), app.getPref('audio_outfile')))
    return opened

def getFileAudio(infile, outfile):
    return MultipleConv(AudioFromFiles(infile, outfile))

