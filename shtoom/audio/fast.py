"""Use fastaudio.

Requires http://www.freenet.org.nz/python/pyPortAudio/fastaudio.tar.gz
"""

# system imports
import fastaudio

# sibling imports
import interfaces


class AudioFile:

    __implements__ = (interfaces.IAudioReader, interfaces.IAudioWriter)

    def __init__(self, stream):
        self.stream = stream
        self.stream.open()
        self.buffer = ""
    
    def __del__(self):
        self.stream.stop()
        self.stream.close()
        del self.stream

    def write(self, data):
        self.stream.write(data)

    def read(self, length):
        self.buffer += self.stream.read()
        result, self.buffer = self.buffer[:length], self.buffer[length:]
        return result


def getAudioDevice(mode):
    # we ignore mode, result can always both read and write
    # XXX no idea if these inputs are correct
    return AudioFile(fastaudio.stream(8000, channels=1))
