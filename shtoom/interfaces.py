# Copyright (C) 2003 Anthony Baxter

from twisted.python.components import Interface


class IPhoneUIFeedback(Interface):
    """ User interface glue layer.

        The phone calls back into this to make 'things happen' in the UI
    """

    def debugMessage(self, message):
        """ A debugging message.

            UI hint: some sort of text widget
        """

    def statusMessage(self, message):
        """ A status message.

            UI hint: some sort of text label
        """

    def callConnected(self, call):
        """ The call 'call' has been connected
        """

    def callDisconnected(self, call):
        """ The call 'call' has been disconnected
        """

    def incomingCall(self, description, call, defresp, defsetup):
        """ An incoming call (described by text 'description') has arrived.

            The UI should call defresp.callback() to accept the call, 
            and defresp.errback() to reject it.

            defsetup is a deferred which will be triggered when call setup
            is complete or failed, as in the response to placeCall()
            
            XXX should pass reject reasons back.
        """


class ISipPhone(Interface):
    """ SIP glue layer. The UI keeps a reference to a ISipPhone, and
        invokes it's methods to do stuff.
    """

    def placeCall(self, url):
        """ Place a call to 'url'

            Returns callid, a string
        """

    def dropCall(self, callid):
        """ Drop call identified by 'callid'
        """

    def startDTMF(self, digit):
        """ Start sending DTMF digit 'digit'
        """

    def stopDTMF(self, digit):
        """ Stop sending DTMF digit 'digit'
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

