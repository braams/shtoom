from twisted.python.components import Interface

# XXX better explanation of audio format etc.

class IAudioReader(Interface):
    """Reads in audio."""

    def read(self, length):
        """Return length bytes."""


class IAudioWriter(Interface):
    """Writes audio out."""

    def write(self, data):
        """Writes audio."""
