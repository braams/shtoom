# Copyright (C) 2004 Anthony Baxter
# This file is necessary to make this directory a package

from twisted.python.components import Interface

class ApplicationSIPInterface(Interface):
    """This interface describes the interface to the Application that 
       the SIP layer uses.
    """

    def acceptCall(self, call, **calldesc):
        """ Setup a new call. 
            calldesc describes the new call, it's a dictionary with the 
            following entries:
                calltype : 'outbound' or 'inbound'

            Returns  deferred - .callback() will be invoked if 
            the call is to be accepted, or .errback() if the call is to be 
            rejected.  The callback will return the callcookie - callcookie 
            is a unique identifier used for all dealings with the Application 
            in the future about this call.
        """

    def startCall(self, callcookie, cb):
        """ Call setup is complete, the call is now live. Accepts a callback 
            which is invoked when the application wishes to terminate the call. 
            The callback is passed a reason for the call teardown.
        """

    def endCall(self, callcookie, reason):
        """ Other end has terminated the call.
        """

class ApplicationRTPInterface(Interface):
    """This interface describes the interface that an RTP implementation
       uses to talk to the Application instance
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

class ApplicationUIInterface(Interface):
    """ This interface describes the interface that the UI can use
        to communicate with the Application.
    """

    def placeCall(self, sipURL):
        """ Place a call. returns a a deferred. The deferred's callback
            will be passed a call cookie when the call is setup. The 
            UI should use the call cookie in all future communications 
            with the Application to indicate which call it is handling.
            The deferred's errback will be called if the call setup fails.
        """

    def dropCall(self, cookie):
        """ Drop call identified by the call cookie. """

    def startDTMF(self, cookie, digit):
        """ Start sending DTMF digit 'digit' """

    def stopDTMF(self, cookie, digit):
        """ Stop sending DTMF digit 'digit' """


class Application(ApplicationSIPInterface, 
                  ApplicationRTPInterface, 
                  ApplicationUIInterface):

    def __init__(self):
        """ Create the application. The application should create the SIP
            listener and any user interface that's needed.
        """


