class SilenceSource:
    "A SilenceSource generates silence and eats all audio given to it"
    def __init__(self):
        pass

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

class FileSource:
    "A FileSource connects to a file for either reading or writing"

    def __init__(self, fp, mode):
        self._fp = fp
        self._mode = mode

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
            return self._fp.read()

    def write(self, bytes):
        if self._mode == 'w':
            return self._fp.write(bytes)

def convertToSource(thing, mode='r'):
    if isinstance(thing, basestring):
        if mode == 'r':
            fp = open(thing, 'rb')
        elif mode == 'w':
            fp = open(thing, 'wb')
        else:
            raise ValueError("mode must be r or w")
    return FileSource(fp, mode)

