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

    def getString(self, message):
        """ Prompt the user for information, with the prompt 'message'
            returns a Deferred
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

    def getAuth(self, message):
        """ Prompt for user auth, using the message 'message'.
            Returns a Deferred that returns ( user, passwd )
            on success, or fails with CallRejected.
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
    def createRTPSocket(self, localIP, withSTUN):
        """ Create the RTP socket. Use 'localIP' as this end's IP address
            (note that it may be a different address to the system's - it's
            the externally visible address, as reported by STUN. If
            withSTUN is true, use STUN to discover the external port numbers
            for RTP/RTCP
        """

    def getVisibleAddress(self):
        """ Returns the IP address for this end of the RTP connection.
        """

    def start(self):
        """ Start the timer loop that sends packets of audio.
        """

    def stopSendingAndReceiving(self):
        """ Stop the timer loop that delivers and receives packets.
        """

    def startDTMF(self, digit):
        """ Start sending digit 'digit'
        """

    def stopDTMF(self, digit):
        """ Stop sending digit 'digit'
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

class NATMapper(Interface):
    """ NAT Mapper interface.

        A NAT Mapper is passed a Port object, and does the appropriate
        thing to make the port available on the outside of a NAT.

        The STUN NAT Mapper can only do this for UDP, while the UPnP Mapper
        can do both UDP and TCP.
    """

    def map(self, port):
        """ Passed a Port object, returns a Deferred. The Deferred will
            be triggered with a t.i.address.IPv4Address of the external
            address. If the same Port is passed a second time, the same
            address will be returned.
        """

    def info(self, port):
        """ Returns an IPv4Address of a mapped Port. .map() should have
            been called with this Port object first and the resulting deferred
            is required to have been triggered - otherwise a ValueError will be
            raised.
        """

    def unmap(self, port):
        """ Remove the external port mapping for the given port. .map()
            should have already been called with the given Port.
            Returns a deferred that will be triggered when the mapping
            has been removed.

            Note that for the STUN mapper, this is a no-op, but you should do
            it anyway.
        """
