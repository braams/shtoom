"Conferencing code"

# XXX A relatively simple enhancement to this would be to store the 
# volumes for each source in the conference, and use an exponential
# decay type algorithm to determine the "loudest". 

from shtoom.doug.source import Source
from twisted.internet.task import LoopingCall
from twisted.python import log
from sets import Set

class ConferenceError(Exception): pass
class ConferenceClosedError(ConferenceError): pass
class ConferenceMemberNotFoundError(ConferenceError): pass

CONFDEBUG = True
CONFDEBUG = False

class ConfSource(Source):
    "A ConfSource connects a voiceapp, and via that, a leg, to a room"

    def __init__(self, room, leg):
        self._user = leg.getDialog().getRemoteTag().getURI()
        self._room = room
        self._room.addMember(self)
        self._quiet = False
        self.makeBuffer()
        super(ConfSource, self).__init__()

    def makeBuffer(self):
        try: 
            from collections import deque
        except ImportError:
            # not optimal, but the queue isn't large
            self.deque = list()
            self.popleft = lambda: self.deque.pop(0)
        else:
            self.deque = deque()
            self.popleft = self.deque.popleft

    def truncBuffer(self):
        while len(self.deque) > 3:
            self.popleft()

    def isPlaying(self):
        return True

    def isRecording(self):
        return True

    def read(self):
        try:
            ret = self._room.readAudio(self)
        except ConferenceClosedError:
            return self.app._va_sourceDone(self)
        if not ret:
            if not self._quiet:
                log.msg("%r is now receiving silence"%(self))
                self._quiet = True
        elif self._quiet:
            log.msg("%r has stopped receiving silence"%(self))
            self._quiet = False
        return ret

    def close(self):
        self._room.removeMember(self)

    def write(self, bytes):
        self.deque.append(bytes)
        self.truncBuffer()
        if not self._room.isOpen():
            self.app._va_sourceDone(self)

    def getAudioForRoom(self):
        "get audio into the room"
        # XXX tofix - might not have enough data (short packets). rock on.
        if len(self.deque):
            bytes = self.popleft()
            return bytes

    def __repr__(self):
        return "<ConferenceUser %s in room %s at %x>"%(self._user,
                            self._room.getName(), id(self))


class Room:
    """A room is a conference. Everyone in the room hears everyone else
       (well, kinda)
    """

    # Theory of operation. Rather than rely on the individual sources
    # timer loops (which would be, well, horrid), we trigger off our
    # own timer.
    # This means we don't have to worry about the end systems not
    # contributing during a window.
    _open = False

    def __init__(self, name, MaxSpeakers=4):
        self._name = name
        self._members = Set()
        self._audioOut = {}
        self._audioOutDefault = ''
        self._maxSpeakers = MaxSpeakers
        self.start()

    def start(self):
        self._audioCalcLoop = LoopingCall(self.mixAudio)
        self._audioCalcLoop.start(0.020)
        self._open = True

    def getName(self):
        return self._name

    def __repr__(self):
        if self._open:
            o = ''
        else:
            o = ' (closed)'
        return "<ConferenceRoom %s%s with %d members>"%(self._name, o,
                                            len(self._members))

    def shutdown(self):
        if hasattr(self._audioCalcLoop, 'cancel'):
            self._audioCalcLoop.cancel()
        else:
            self._audioCalcLoop.stop()
        # XXX close down any running sources!
        self._members = Set()
        del self._audioOut
        self._open = False
        removeRoom(self._name)

    def addMember(self, confsource):
        self._members.add(confsource)
        if CONFDEBUG:
            print "added", confsource, "to room", self
        if not self._open:
            self.start()

    def removeMember(self, confsource):
        if len(self._members) and confsource in self._members:
            self._members.remove(confsource)
            if CONFDEBUG:
                print "removed", confsource, "from", self
        else:
            raise ConferenceMemberNotFoundError(confsource)
        if not len(self._members):
            if CONFDEBUG:
                print "No members left, shutting down"
            self.shutdown()

    def isMember(self, confsource):
        return confsource in self._members

    def isOpen(self):
        return self._open

    def memberCount(self):
        return len(self._members)

    def readAudio(self, confsource):
        if self._open:
            return self._audioOut.get(confsource, self._audioOutDefault)
        else:
            raise ConferenceClosedError()

    def mixAudio(self):
        # XXX see the comment above about storing a decaying number for the
        # volume. For instance, each time round the loop, take the calculated
        # volume, and the stored volume, and do something like:
        # newStoredVolume = (oldStoredVolume * 0.33) + (thisPacketVolume * 0.66)
        import audioop
        self._audioOut = {}
        if not self._open:
            log.msg('mixing closed room %r'%(self,), system='doug')
            return
        audioIn = {}
        for m in self._members:
            bytes = m.getAudioForRoom()
            if bytes: audioIn[m] = bytes
        if CONFDEBUG:
            print "room %r has %d members"%(self, len(self._members))
            print "got %d samples this time"%len(audioIn)
            print "samples: %r"%(audioIn.items(),)
        # short-circuit this case
        if len(self._members) < 2:
            if CONFDEBUG:
                print "less than 2 members, no sound"
            self._audioOutDefault = ''
            return
        # Samples is (confsource, audio)
        samples = audioIn.items()
        # power is three-tuples of (rms,audio,confsource)
        power = [ (audioop.rms(x[1],2),x[1], x[0]) for x in samples ]
        power.sort(); power.reverse()
        if CONFDEBUG:
            for rms,audio,confsource in power:
                print confsource, rms
        # Speakers is a list of the _maxSpeakers loudest speakers
        speakers = Set([x[2] for x in power[:self._maxSpeakers]])
        # First we calculate the 'default' audio. Used for everyone who's
        # not a speaker in the room.
        samples = [ x[1] for x in power[:self._maxSpeakers] ]
        scaledsamples = [ audioop.mul(x, 2, 1.0/len(samples)) for x in samples ]
        if scaledsamples:
            # ooo. a use of reduce. first time for everything...
            try:
                combined = reduce(lambda x,y: audioop.add(x, y, 2), scaledsamples)
            except audioop.error, exc:
                # XXX tofix!
                print "combine got error %s"%(exc,)
                print "lengths", [len(x) for x in scaledsamples]
                combined = ''
        else:
            combined = ''
        self._audioOutDefault = combined
        # Now calculate output for each speaker.
        allsamples = {}
        for p,sample,speaker in power:
            allsamples[speaker] = p, sample
        for s in speakers:
            # For each speaker, take the set of (other speakers), grab
            # the top N speakers, and combine them. Add to the _audioOut
            # dictionary
            all = allsamples.copy()
            del all[s]
            power = all.values()
            power.sort() ; power.reverse()
            samples = [ x[1] for x in power[:self._maxSpeakers] ]
            if samples:
                scaled = [ audioop.mul(x, 2, 1.0/len(samples)) for x in samples]
                try:
                    out = reduce(lambda x,y: audioop.add(x, y, 2), scaled)
                except audioop.error, exc:
                    # XXX tofix!
                    print "combine got error %s"%(exc,)
                    print "lengths", [len(x) for x in scaled]
                    out = ''
            else:
                out = ''
            if CONFDEBUG:
                print "calc for", s, "is", audioop.rms(out, 2)
            self._audioOut[s] = out

_RegisterOfAllRooms = {}

_StickyRoomNames = {}

def removeRoom(roomname):
    global _RegisterOfAllRooms
    if roomname in _RegisterOfAllRooms and roomname not in _StickyRoomNames:
        del _RegisterOfAllRooms[roomname]

def newConferenceMember(roomname, leg):
    global _RegisterOfAllRooms

    if not roomname in _RegisterOfAllRooms:
        _RegisterOfAllRooms[roomname] = Room(roomname)
    room = _RegisterOfAllRooms[roomname]
    return ConfSource(room, leg)
