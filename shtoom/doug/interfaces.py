# Copyright (C) 2004 Anthony Baxter

""" VoiceApp Interface

    This is just a first cut at the VoiceApp. Do NOT assume that
    the interfaces here won't be entirely rewritten in the future.

    In fact, ASSUME that they will be rewritten entirely. Repeatedly.

"""

class IVoiceApp:

    def mediaPlay(self, playlist):
        """ Play one or more audio objects. 'playlist' is a sequence of
            either filenames or open file-like objects - they should
            support 'read()' and 'close()'.

            If the voiceapp is currently playing any audio, the new
            objects will be appended to the end of the current playing
            list. If you want to abort the current playing things, call
            mediaStop first

            any open files will be handed back closed
        """

    def mediaRecord(self, destination):
        """ Record audio to a destination. 'destination' is either a
            filename or an open file-like object - the latter should
            support 'write()' and 'close()'

            Calling this when we're already recording is an error,
            call mediaStop first

            when completed, the file will be closed
        """

    def mediaStop(self):
        """ Stop any mediaPlay or mediaRecord that's currently running.
            Calling this when neither are running is a no-op.
        """

    def isPlaying(self):
        """ Returns True if the voiceapp is currently playing audio
        """

    def isRecording(self):
        """ Returns True if the voiceapp is currently recording audio
        """

    def __start__(self):
        """ This is called when the application starts for the first time

            An implementation _must_ provide an implementation of this
        """

    def dtmfMode(self, single=False, timeout=0):
        """ Set the DTMF mode we want. 'single' is a boolean - if False,
            digits will be collected until a star or a hash is entered.
        """

    def returnResult(self, result):
        """ Return 'result' to the caller of this application.

            In the case of a voicemail system calling the 'recorder'
            voiceapp, this would return the completed draft message.
        """

    def cleanUp(self):
        """ Clean up any temporary files or objects created during the
            execution of this voiceapp.
        """


class ISource:
    def __init__(self, whatsit):
        " "

    def isPlaying(self):
        """ Returns True if the source is a playing source
        """

    def isRecording(self):
        """ Returns True if the voiceapp is a recording source
        """

    def close(self):
        """ close the source
        """

    def read(self):
        """ read a packet of audio from the source
        """

    def write(self, bytes):
        """ write a packet of audio to the source
        """

class ILeg:
    """A Leg is a SIP connection into the voice app"""
