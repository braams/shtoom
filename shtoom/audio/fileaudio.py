# Copyright (C) 2004 Anthony Baxter

from twisted.python import log
from shtoom.audio import baseaudio
from twisted.internet.task import LoopingCall

# XXX TOFIX: use the audio pref to specify infile,outfile and kill two options
class AudioFromFiles(baseaudio.AudioDevice):
    _infp = _outfp = None
    _closed = True

    def __init__(self):
        try:
            from __main__ import app
        except:
            log.msg("couldn't find app preferences, no file audio", 
                    system="audio")
            raise ValueError('no app for filename preferences?')
        device = app.getPref('audio_device')
        if not device:
            log.msg("need to provide audio_device with files"
                    " as infile,outfile", system="audio")
            raise ValueError('no audio_device specified')
        files = device.split(',',2)
        if len(files) != 2:
            raise ValueError("device spec should be infile,outfile")
        self.infile, self.outfile = files
        baseaudio.AudioDevice.__init__(self)

    def _push_up_some_data(self):
        if not self.encoder:
            return
        data = self._infp.read(320)
        if self.encoder and data:
            self.encoder.handle_audio(data)

    def write(self, bytes):
        if self._outfp is not None:
            return self._outfp.write(bytes)

    def reopen(self):
        if self.infile is not None:
            self._infp = open(self.infile, 'rb')
        else:
            self._infp = None
        if self.outfile is not None:
            self._outfp = open(self.outfile, 'wb')
        else:
            self._outfp = None
        self.openDev()

    def close(self):
        if self._closed:
            return
        if self._infp is not None:
            self._infp.close()
        if self._outfp is not None:
            self._outfp.close()
        self._closed = True
        self._infp = self._outfp = None
        try:
            self.LC.stop()
        except AttributeError:
            pass

    def openDev(self):
        if self._infp is None and self._outfp is None:
            self.reopen()
        self._closed = False
        self.LC = LoopingCall(self._push_up_some_data)
        self.LC.start(0.020)


Device = AudioFromFiles
