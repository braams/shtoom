
DEBUG=False

class _Playout:
    "Base class for playout. should be an interface - later"

class BrainDeadPlayout(_Playout):
    # We keep two packets of audio. self.b1 is the one "to be read"
    # while self.b2 is the pending one. No notice is taken of the
    # RTP timestamps, sequence numbers, or, really, anything else.

    def __init__(self):
        self.b1 = ''
        self.b2 = ''

    def write(self, bytes, packet=None):
        if not isinstance(bytes, basestring):
            raise ValueError("playout got %s instead of bytes"%(type(bytes)))
        if not self.b2:
            # underrun
            self.b2 = bytes
            return len(bytes)
        else:
            # overrun! log.msg, maybe?
            self.b1 = self.b2
            self.b2 = bytes
            return len(bytes)

    def read(self):
        if self.b1 is not None:
            bytes, self.b1, self.b2 = self.b1, self.b2, ''
            return bytes
        else:
            return ''

# Basically it introduces an n chunks long queue (the n being adjustable
# by changing self.backlog in the constructor). This queue is used for
# resequencing packets in the correct order. The size of the queue can
# decrease when no packets are received - eventually returning silence
# sound chunks if the queue grows empty.
# The size can also increase if too many packets are received in an
# interval. When the queue grows too large (currently backlogsize + 2)
# packets will be discarded. This strategy causes the number of discards
# to exactly match the number of dummy silence packets, and works quite
# well - assuming of course that the other RTP peer is behaving correctly
# and not generating an incorrect number of sound packets.
# I'd like to expand this functionality to support autoadjustment of the
# backlog size - fairly simple to do.

class BacklogPlayout(_Playout):
    def __init__(self):
        self.backlog = 3
        self.queue = ['\0'*320]*(self.backlog)
        self.expect_seq = None
        if DEBUG:
            self.count = 0

    def write(self, bytes, packet=None):
        if not isinstance(bytes, basestring):
            raise ValueError("playout got %s instead of bytes"%(type(bytes)))

        if self.expect_seq == None:
            self.expect_seq = packet.seq # First packet. Initialize seq
        
        backlog = len(self.queue)
        if packet.seq == self.expect_seq:
            self.expect_seq = packet.seq+1
            if backlog < self.backlog+1:
                self.queue.append(bytes)
            elif DEBUG:
                log.msg("BacklogPlayout discarding")
        else:
            offset = packet.seq-self.expect_seq
            if offset > 0 and offset < 3:
                # Fill with empty packets
                self.queue += [None]*offset
                self.queue.append(bytes)
                self.expect_seq = packet.seq+1
                if DEBUG:
                    log.msg("BacklogPlayout got hole at %d"%offset)
            elif offset < 0 and offset > -backlog:
                if self.queue[offset] != None:
                    if DEBUG: 
                        log.msg("BacklogPlayout discarding duplicate packet")
                else:
                    if DEBUG:
                        log.msg("BacklogPlayout got out of order packets")
                    self.queue[offset] = bytes
            return len(bytes)

    def read(self):
        available = len(self.queue)
        if DEBUG:
            self.count += 1
            if self.count%10==0:
                print available
            
        if available:
            data = self.queue.pop(0)
            return data
        elif DEBUG:
            log.msg("BacklogPlayout audio underrun")
        return ''
    

Playout = BrainDeadPlayout
