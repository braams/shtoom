# Copyright (C) 2004 Anthony Baxter
# $Id: exceptions.py,v 1.1 2004/01/14 14:44:54 anthonybaxter Exp $

class FatalError(Exception): pass 
class     DependencyFailure(FatalError): pass 
class         NoAudioDevice(DependencyFailure): pass 
class         NoUserInterface(DependencyFailure): pass

class CallFailed(Exception): pass
class     CallRejected(CallFailed): pass
class     CallNotAnswered(CallFailed): pass
class     STUNFailed(CallFailed): pass

