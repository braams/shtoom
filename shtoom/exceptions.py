# Copyright (C) 2004 Anthony Baxter
# $Id: exceptions.py,v 1.2 2004/03/02 13:03:03 anthony Exp $

class FatalError(Exception): pass
class     DependencyFailure(FatalError): pass
class         NoAudioDevice(DependencyFailure): pass
class         NoUserInterface(DependencyFailure): pass

class CallFailed(Exception):
    sipCode = 500
    def __init__(self, args, cookie=None):
        self.args = args
        self.cookie = cookie

class     CallRejected(CallFailed):
    sipCode = 603

class     CallNotAnswered(CallFailed):
    sipCode = 600

class     UserBusy(CallFailed):
    sipCode = 600

class     STUNFailed(CallFailed): pass
class     UserBogosity(CallFailed): pass
class     HostNotKnown(UserBogosity): pass
class     InvalidSIPURL(UserBogosity): pass
