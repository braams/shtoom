# Copyright (C) 2004 Anthony Baxter
# This file is necessary to make this directory a package

class IApplication:

    def __init__(self):
        """ Create the application. The application should create the SIP
            listener and any user interface that's needed.
        """

    def acceptCall(self, **calldesc):
        """ Setup a new call. 
            calldesc describes the new call, it's a dictionary with the 
            following entries:
                calltype : 'outbound' or 'inbound'

            Returns  (callcookie,deferred) - .callback() will be invoked if 
            the call is to be accepted, or .errback() if the call is to be 
            rejected.  'callcookie' is a unique identifier used for all 
            dealings with the Application in the future about this call.
        """

    def startCall(self, callcookie, cb):
        """ Call setup is complete, the call is now live. Accepts a callback 
            which is invoked when the application wishes to terminate the call. 
            The callback is passed a reason for the call teardown.
        """

    def endCall(self, callcookie, reason):
        """ Other end has terminated the call.
        """

    def receiveRTP(self, callcookie, payloadType, payloadData):
        """ Pass an RTP packet that was received from the network to the
            application. This might be audio, comfort noise (CN), an NTE
            packet, or something else.
        """

    def giveRTP(self, callcookie):
        """ The network layer wants an RTP packet to send. Return a 2-tuple
            of (payloadType, payloadData)
        """

class IPhoneApplication(IApplication):
    """ A Phone Application """

    def placeCall(self, sipURL):
        """ Place a call. returns a callid (a string) and a deferred.
            Deferred callback triggered when call is connected, errback
            on call failure. Use the callid to communicate with the 
            application about the call.
        """

    def dropCall(self, callid):
        """ Drop call identified by callid. """

    def startDTMF(self, callid, digit):
        """ Start sending DTMF digit 'digit' """

    def stopDTMF(self, callid, digit):
        """ Stop sending DTMF digit 'digit' """

