# Copyright (C) 2004 Anthony Baxter
# This file is necessary to make this directory a package

from twisted.python.components import Interface

class ApplicationSIPInterface(Interface):
    """This interface describes the interface to the Application that
       the SIP layer uses.
    """

    def getPref(self, pref):
        """ Return a preference setting """

    def acceptCall(self, call):
        """ Setup a new call.
            Passed a sip.Call object.
            Returns a deferred - .callback() will be invoked if
            the call is to be accepted, or .errback() if the call is to be
            rejected.  The callback will return the callcookie - callcookie
            is a unique identifier used for all dealings with the Application
            in the future about this call.
        """

    def startCall(self, callcookie, oksdp, cb):
        """ Call setup is complete, the call is now live.
            Passed the final SDP for the call, and a callback which should
            be invoked when the application wishes to terminate the call.
            The callback will be passed a reason for the call teardown.
        """

    def endCall(self, callcookie, reason):
        """ Other end has terminated the call. Reason is a string.
        """

    def ringBack(self):
        """ The other side sent a "180 Ringing".  This is purely informational
            -- the app may wish to, for example, play a ringback sound to the
            user.
        """

    def notifyEvent(self, event, eventArg):
        """ Notify the app that something interesting has happened. eventArg
            depends on the event.
            discoveredIP : local IP address (a string)
            discoveredStunnedIP : externally visible address (host, port)
            registrationOK: a Registration object
        """

    def authCred(self, method, uri, realm, retry=False):
        """ Get auth credentials. Will return a deferred which when triggered
            will be passed either (username, password) or None (if no auth
            is available). retry means that the auth failed (so, for instance,
            the app should re-ask for auth credentials).
        """

    def getSDP(self, callcookie, otherSDP=None):
        """ Returns a shtoom.sdp.SDP instance for this call.
            if otherSDP is not None, do an intersection with it and return
            the result.
        """

    def debugMessage(self, message):
        """ Display a debugging message
        """

    def statusMessage(self, message):
        """ Display a status message. This should replace the previous
            status message
        """

class ApplicationRTPInterface(Interface):
    """This interface describes the interface that an RTP implementation
       uses to talk to the Application instance
    """

    def incomingRTP(self, callcookie, payloadType, payloadData):
        """ Pass an RTP packet that was received from the network to the
            application. This might be audio, comfort noise (CN), an NTE
            packet, or something else.
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
