import sys

class Source(object):
    "A Source object is a source and sink of audio data"

    # Can this Source handle DMTF?
    wantsDTMF = False

    def __init__(self):
        self.leg = None

    def getLeg(self):
        return self.leg

    def isPlaying(self):
        return NotImplementedError

    def isRecording(self):
        return NotImplementedError

    def read(self):
        return NotImplementedError

    def close(self):
        return NotImplementedError

    def write(self, bytes):
        return NotImplementedError

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


class EchoSource(Source):
    """ An EchoSource just repeats back whatever you send it. An optional
        'delay' argument to the constructor specifies a delay - the
        EchoSource will buffer that many seconds of audio before returning
        anything.
    """

    def __init__(self, delay=0.0):
        self._buffer = ''
        self._delay = delay

    def isPlaying(self):
        return True

    def isRecording(self):
        return True

    def close(self):
        self._buffer = ''
        return

    def read(self):
        # 2 bytes per sample, 8000 samples per second
        if len(self._buffer) >= 320+(self._delay * 16000.0):
            r, self._buffer = self._buffer[:320], self._buffer[320:]
            return r
        else:
            return ''

    def write(self, bytes):
        self._buffer += bytes

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
                self.leg._sourceDone(self)
            else:
                return bytes

    def write(self, bytes):
        if self._mode == 'w':
            try:
                self._fp.write(bytes)
            except:
                e,v,t = sys.exc_info()
                print "write failed %s: %r"%(e,v)
                self.leg._sourceDone(self)

def convertToSource(thing, mode='r'):
    if isinstance(thing, Source):
        return thing
    elif isinstance(thing, basestring):
        if mode == 'r':
            fp = open(thing, 'rb')
        elif mode == 'w':
            fp = open(thing, 'wb')
        else:
            raise ValueError("mode must be r or w")
    else:
        raise ValueError('source must be filename or source, not %r'%(type(thing)))
    return FileSource(fp, mode)
