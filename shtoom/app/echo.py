# Copyright (C) 2004 Anthony Baxter

# The Echo Server.
# Accepts all calls, echos audio received back to the sender

from shtoom.app.interfaces import Application
from shtoom.app.answer import AnsweringMachine
from shtoom.app.base import STATE_BOTH
from shtoom.audio.echoaudio import getEchoAudio

class EchoServer(AnsweringMachine):
    __implements__ = ( Application, )
    startingState = STATE_BOTH

    def openAudioDevice(self, callcookie, toAddress, fromAddress):
        self._audios[callcookie] = getEchoAudio()
        self._audioStates[callcookie] = STATE_BOTH

    def closeAudioDevice(self, callcookie):
        self._audios[callcookie].close()
        del self._audios[callcookie]
        del self._audioStates[callcookie]

    def finishedAudio(self, callcookie):
        pass

    def appSpecificOptions(self, opts):
        from shtoom.Options import OptionGroup, StringOption
        app = OptionGroup('echotest', 'Echo Test')
        app.addOption(StringOption('logfile','log to this file'))
        opts.addGroup(app)
        opts.setOptsFile('.shechorc')
