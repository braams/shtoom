# Copyright (C) 2004 Anthony Baxter

from twisted.python.components import Interface


class UI(Interface):
    """ This interface describes the user interface calls that can be
        invoked by the Application. Note that "user interface" does not
        necessarily mean some sort of graphical interface - for instance
        a conferencing server's UI would be a programmatic thing.
    """

    def debugMessage(self, message):
        """ A debugging message.
        """

    def statusMessage(self, message):
        """ Displays a status message. This will typically replace any
            previous status message.
        """

    def callConnected(self, cookie):
        """ The call identified by 'cookie' has been connected
        """

    def callDisconnected(self, cookie, reason):
        """ The call identified by 'cookie' has been disconnected. 'reason'
            gives a short text description for the call failure.
        """

    def incomingCall(self, description, cookie, defresp):
        """ An incoming call (described by text 'description') has arrived.

            The UI should call defresp.callback() to accept the call,
            and defresp.errback() to reject it.

            The Application will call 'callConnected()' when the call
            is setup, or callDisconnected() if the call could not be
            established.
        """

class SIP(Interface):
    """ This describes the interface to the SIP layer that the Application
        uses. 
    """

    def placeCall(self, sipURL):
        """ Place a call to URL 'sipURL'.
        """

class RTP(Interface):
    """ This describes the interface to the RTP layer used by the Application
    """

    def __init__(self, cookie):
        """ Create an RTP instance. The RTP object should use the 'cookie'
            for calls back into the Application (to request data, for instance)
        """
    def createRTPSocket(self, fromIP, withSTUN):
        """ Create the RTP socket. Use 'fromIP' as this end's IP address
            (note that it may be a different address to the system's - it's
            the externally visible address, as reported by STUN. If 
            withSTUN is true, use STUN to discover the external port numbers
            for RTP/RTCP
        """

    def getVisibleAddress(self):
        """ Returns the IP address for this end of the RTP connection.
        """

    def startSendingAndReceiving(self):
        """ Start the timer loop that delivers and receives packets.
        """

    def stopSendingAndReceiving(self):
        """ Stop the timer loop that delivers and receives packets.
        """

    

class AddressBook(Interface):
    """ Address Book interface
    """

    def browseAddressBook(self, query=None):
        """ Pop up the address book, with an optional 'query' (a string
            to begin the browsing).

            Returns a Deferred, the callback of which will be called with
            a string (the URI to call), or the errback if they select nothing
        """

    def addEntryToAddressBook(self, uri):
        """ Pop up the address book to add the URI 'uri' (a string).
        """

class StunPolicy(Interface):
    """ A STUNPolicy decides when STUN is applied """

    def checkStun(self, localip, remoteip):
        """ return True/False for whether STUN should apply """
