# Copyright (C) 2003 Anthony Baxter

from converters import NullConv, PCM16toULAWConv

opened = None

class AudioFromFiles:
    def __init__(self, infile, outfile):
        self._infp = open(infile, 'rb')
        self._outfp = open(outfile, 'wb')
        self.read = self._infp.read
        self.write = self._outfp.write

    def close(self):
        self._infp.close()
        self._outfp.close()

def getAudioDevice(mode):
    from shtoom import prefs
    return AudioFromFiles(prefs.audio_infile, prefs.audio_outfile)

if __name__ == "__main__":
    test()
