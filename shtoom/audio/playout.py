
class _Playout:
    "Base class for playout. should be an interface - later"


class BrainDeadPlayout(_Playout):
    # We keep two slices of buffering. self.b1 is the one "to be read"
    # while self.b2 is the pending one.

    def __init__(self):
        self.b1 = ''
        self.b2 = ''

    def write(self, bytes):
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

Playout = BrainDeadPlayout
