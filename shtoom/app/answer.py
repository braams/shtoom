# Copyright (C) 2004 Anthony Baxter

# The Answering Machine app. Accepts all calls, plays a message 
# (based on the 'to' address) then records a message for them.

from shtoom.app.interfaces import Application
from shtoom.app.base import BaseApplication
from twisted.internet import defer
from twisted.python import log
from twisted.protocols import sip as tpsip
import sys, time, os

from shtoom.app.base import STATE_SENDING, STATE_RECEIVING

from shtoom.audio import FMT_PCMU, FMT_GSM, FMT_SPEEX, FMT_DVI4
from shtoom.audio.fileaudio import getFileAudio

from message import Message

class AnsweringMachine(Message):
    __implements__ = ( Application, )

    def __init__(self, *args, **kwargs):
        self._playingAnnounce = {}
        Message.__init__(self, *args, **kwargs)

    def acceptCall(self, call, **calldesc):
        print "acceptCall for %r"%calldesc
        calltype = calldesc.get('calltype')
        if calldesc.get('toAddr'):
            comment, toAddress, tag = tpsip.parseAddress(calldesc['toAddr'][0])
            toAddress = (toAddress.username, toAddress.host)
        else:
            toAddress = None
        if calldesc.get('fromAddr'):
            comment, fromAddress, tag = tpsip.parseAddress(calldesc['fromAddr'][0])
            fromAddress = (fromAddress.username, fromAddress.host)
        else:
            fromAddress = None
        d = defer.Deferred()
        cookie = self.getCookie()
        self.openAudioDevice(cookie, toAddress, fromAddress)
        d.addCallback(lambda x: self._createRTP(cookie,
                                                calldesc['localIP'],
                                                calldesc['withSTUN']))
        self._calls[cookie] = call
        if calltype == 'inbound':
            # Otherwise we chain callbacks
            log.msg("accepting incoming call from %s"%calldesc['desc'])
            d.callback(cookie)
        else:
            raise ValueError, "unknown call type %s"%(calltype)
        return d

    def openAudioDevice(self, callcookie, toAddress, fromAddress):
        import os, os.path
        announceDir = self.getPref('announce_directory')
        messageDir = self.getPref('message_directory')
        if not os.path.isdir(announceDir):
            log.err("ANNOUNCEMENTS DIRECTORY IS MISSING: %s"%(announceDir))
            self.dropCall(callcookie)
        if not os.path.isdir(messageDir):
            log.err("MESSAGE DIRECTORY IS MISSING: %s"%(messageDir))
            self.dropCall(callcookie)
        touser, todomain = toAddress
        fromuser, fromdomain = fromAddress
        da = os.path.join(announceDir, todomain)
        if os.path.isdir(da):
            announceFile = os.path.join(da, '%s.wav'%touser)
            if os.path.exists(announceFile):
                messageFile = os.path.join(messageDir, 
                        '%s@%s_%s@%s_%d.raw'%(touser, todomain,
                                              fromuser, fromdomain,
                                              time.time()))
                
            else:
                announceFile = self.getPref('fallback_message')
                messageFile = None
        else:
            log.err("announcements directory for domain %s is missing"%(todomain))
            announceFile = self.getPref('fallback_message')
            messageFile = None

        self._audios[callcookie] = getFileAudio(announceFile, messageFile)
        self._audioStates[callcookie] = STATE_SENDING
        self._playingAnnounce[callcookie] = messageFile

    def closeAudioDevice(self, callcookie):
        self._audios[callcookie].close()
        del self._audios[callcookie]
        if self._audioStates[callcookie] == STATE_SENDING:
            # They didn't get to record a message
            if self._playingAnnounce[callcookie] is not None:
                os.remove(self._playingAnnounce[callcookie])
        del self._audioStates[callcookie]
        del self._playingAnnounce[callcookie]

    def finishedAudio(self, callcookie):
        if self._playingAnnounce[callcookie] is None:
            self.dropCall(callcookie)
        else:
            self._audioStates[callcookie] = STATE_RECEIVING
        
    def appSpecificOptions(self, opts):
        import os.path
        from shtoom.Options import OptionGroup, StringOption, ChoiceOption
        app = OptionGroup('shtam', 'Shtam')
        app.addOption(StringOption('announce_directory','announcements live here', default='/tmp/recordings'))
        app.addOption(StringOption('message_directory','saved messages live here', default='/tmp/messages'))
        app.addOption(StringOption('fallback_message','fallback message when no announcement can be found', default='/tmp/fallback.wav'))
        opts.addGroup(app)
        opts.setOptsFile('.shtamrc')

