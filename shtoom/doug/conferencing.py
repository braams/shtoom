from shtoom.doug.events import *
from shtoom.doug.source import Source
from twisted.internet.task import LoopingCall
from sets import Set
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
        self._room.removeMember(self)

    def write(self, bytes):
        self._room.writeAudio(self, bytes)

class Room:
    """A room is a conference. Everyone in the room hears everyone else 
       (well, kinda)
    """

    # Theory of operation. Rather than rely on the individual sources 
    # timer loops (which would be, well, horrid), we trigger off our 
    # own timer. 
    # This means we don't have to worry about the end systems not 
    # contributing during a window.

    def __init__(self, MaxSpeakers=4):
        self._members = Set()
        self._audioIn = {}
        self._audioOut = {}
        self._audioOutDefault = ''
        self._maxSpeakers = MaxSpeakers
        self._audioCalcLoop = LoopingCall(self.mixAudio)
        self._audioCalcLoop.start(0.020)

    def shutdown(self):
        if hasattr(self._audioCalcLoop, 'cancel'):
            self._audioCalcLoop.cancel()
        else:
            self._audioCalcLoop.stop()
        # XXX close down any running sources!
        self._members = Set()
        del self._audioIn
        del self._audioOut

    def addMember(self, confsource):
        self._members.add(confsource)

    def removeMember(self, confsource):
        if len(self._members) and confsource in self._members:
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
        import audioop
        self._audioOut = {}
        samples = self._audioIn.items()
        power = [ (audioop.rms(x[1],2),x[1], x[0]) for x in samples ]
        power.sort(); power.reverse()
        speakers = Set([x[2] for x in power[:self._maxSpeakers]])
        # First we calculate the 'default' audio. Used for everyone who's
        # not a speaker in the room.
        samples = [ x[1] for x in power[:self._maxSpeakers] ]
        divsamples = [ audioop.mul(x, 2, len(samples)) for x in samples ]
        if divsamples:
            out = reduce(lambda x,y: audioop.add(x, y, 2), divsamples)
        else:
            out = ''
        self._audioOutDefault = out

        # Now calculate output for each speaker.
        allsamples = {}
        for p,sample,speaker in power:
            allsamples[speaker] = p, sample
        for s in speakers:
            # For each, take the set of (other speakers), grab the 
            # top N speakers, and combine them. Add to the _audioOut 
            # dictionary.
            all = allsamples.copy()
            del all[s]
            power = all.values()
            power.sort() ; power.reverse()
            samples = [ x[1] for x in power[:self._maxSpeakers] ]
            if samples:
                divsamples = [ audioop.mul(x, 2, len(samples)) for x in samples]
                out = reduce(lambda x,y: audioop.add(x, y, 2), divsamples)
            else:
                out = ''
            self._audioOut[speaker] = out
        self._audioIn = {}

_RegisterOfAllRooms = {}

def newConferenceMember(room):
    global _RegisterOfAllRooms

    if not room in _RegisterOfAllRooms:
        _RegisterOfAllRooms[room] = Room()
    room = _RegisterOfAllRooms[room] 
    return ConfSource(room)

