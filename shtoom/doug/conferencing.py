from shtoom.doug.events import *
from shtoom.doug.source import Source
from twisted.internet.task import LoopingCall
import sys

class ConfSource(Source):
    "A ConfSource connects a voiceapp, and via that, a leg, to a room"

    def __init__(self, room):
        self._room = room
        self._room.addMember(self)
        super(ConfSource, self).__init__()

    def isPlaying(self):
        return True

    def isRecording(self):
        return True

    def read(self):
        return self._room.readAudio(self)

    def close(self):
        return self._room.removeMember(self)

    def write(self, bytes):
        return self._room.writeAudio(self, bytes)

class Room:
    """A room is a conference. Everyone in the room hears everyone else 
       (well, kinda)
    """

    # Theory of operation. Rather than rely on the individual sources 
    # timer loops (which would be, well, horrid), we trigger off our 
    # own timer. 
    # This means we don't have to worry about the end systems not 
    # contributing during a window.

    def __init__(self):
        from sets import Set
        self._members = Set()
        self._audioIn = {}
        self._audioOut = {}
        self._audioOutDefault = ''
        self._audioCalcLoop = LoopingCall(self.mixAudio)

    def shutdown(self):
        self._audioCalcLoop.cancel()
        # XXX close down any running sources!
        del self._members
        del self._audioIn
        del self._audioOut

    def addMember(self, confsource):
        self._members.add(confsource)

    def removeMember(self, confsource):
        self._members.remove(confsource)
        if not len(self._members):
            self.shutdown()

    def isMember(self, confsource):
        return confsource in self._members

    def memberCount(self):
        return len(self._members)

    def writeAudio(self, confsource, audio):
        self._audioIn[confsource] = audio

    def readAudio(self, confsource):
        return self._audioOut.get(confsource, self._audioOutDefault)

    def mixAudio(self):
        # Not _quite_ right yet. This code returns the top 4 overall,
        # without knocking out the source's own audio. But it's close.

        # The short form of this is that it means you'll hear your own
        # voice on the call. Hey, it's a start.

        import audioop
        samples = self._audioIn.items()
        power = [ (audioop.rms(x[1],2),x[1], x[0]) for x in samples ]
        power.sort(); power.reverse()
        samples = [ x[1] for x in power[:4] ]
        divsamples = [ audioop.mul(x, 2, len(samples)) for x in samples ]
        out = reduce(lambda x,y: audioop.add(x, y, 2), divsamples)
        self._audioOutDefault = out
        return out

_RegisterOfAllRooms = {}

def newConferenceMember(room):
    global _RegisterOfAllRooms

    if not room in _RegisterOfAllRooms:
        _RegisterOfAllRooms[room] = Room()
    room = _RegisterOfAllRooms[room] 
    return ConfSource(room)

