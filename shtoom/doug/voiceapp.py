""" VoiceApp base class
"""

class VoiceApp(object):

    def mediaPlay(self, playlist):
        pass

    def mediaRecord(self, destination):
        pass

    def isPlaying(self):
        pass

    def isRecording(self):
        pass

    def __start__(self):
        raise NotImplementedError

    def dtmfMode(self, single=False, timeout=0):
        pass

    def returnResult(self, result):
        pass

    def cleanUp(self):
        pass
