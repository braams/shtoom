from shtoom.doug.events import *

class Source(object):
    "A Source object is a source and sink of audio data"
    def __init__(self):
        self.app = None

    def getVoiceApp(self):
        return self.app

class SilenceSource(Source):
    "A SilenceSource generates silence and eats all audio given to it"
    def __init__(self):
        super(SilenceSource, self).__init__()

    def isPlaying(self):
        return False

    def isRecording(self):
        return False

    def close(self):
        pass # noop - you cannot close what does not live! 

    def read(self):
        return ''

    def write(self, bytes):
        pass

class FileSource(Source):
    "A FileSource connects to a file for either reading or writing"

    def __init__(self, fp, mode):
        self._fp = fp
        self._mode = mode
        super(FileSource, self).__init__()

    def isPlaying(self):
        return self._mode == 'r'

    def isRecording(self):
        return self._mode == 'w'

    def close(self):
        self._fp.close()

    def read(self):
        if self._mode == 'w':
            return ''
        else:
            bytes = self._fp.read(320)
            if not bytes:
                self.app._triggerEvent(MediaPlayContentDoneEvent(self))
            else:
                return bytes

    def write(self, bytes):
        if self._mode == 'w':
            res = self._fp.write(bytes)
            if not res:
                self.app._triggerEvent(MediaRecordStoreFailedEvent(self))

def convertToSource(thing, mode='r'):
    print "opening thing", thing
    if isinstance(thing, basestring):
        if mode == 'r':
            fp = open(thing, 'rb')
        elif mode == 'w':
            fp = open(thing, 'wb')
        else:
            raise ValueError("mode must be r or w")
    return FileSource(fp, mode)

