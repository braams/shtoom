from twisted.python.components import Interface


class IAudio(Interface):
    '''Lowlevel interface to audio source/sink.'''

    def getFormats(self):
        '''Retuns a list of the supported audio formats'''

    def selectDefaultFormat(self, format):
        '''Select a particular format for audio. This format is used for
           both reading and writing.
        '''

    def close(self):
        '''Close the underlying audio device'''

    def reopen(self):
        '''Reopen a closed audio device'''

    def isOpen(self):
        '''Return True if and only if the underlying audio is available'''

    def read(self):
        '''Return a packet of audio. The length of the audio returned depends
           on the currently selected audio Format.
        '''

    def write(self, data):
        '''Writes audio.'''
