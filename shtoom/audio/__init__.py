"""Find appropriate audio device and expose via getAudioDevice().

getAudioDevice() accepts either 'r', 'w' or 'rw' as arguments,
and result will implement shtoom.audio.interfaces.IAudioReader
and/or IAudioWriter, as appropriate.
"""

FMT_PCMU = 1
FMT_GSM = 2
FMT_SPEEX = 3
FMT_DVI4 = 4
FMT_RAW = 5

def findAudioDevice(audioPref, audioFiles=None):
    attempts = ( tryOssAudio, tryFastAudio, )
    if audioFiles is not None:
        attempts = ( tryFileAudio, )
    elif audioPref:
        if audioPref == 'oss':
            attempts = (tryOssAudio,)
        elif audioPref in ( 'fast', 'port' ):
            attempts = (tryFastAudio,)
        else:
            raise ValueError("unknown audio %s"%(audioPref))
    for attempt in attempts:
        audio = attempt()
        if audio is not None:
            return audio
    return None

def tryFileAudio():
    try:
        import fileaudio
    except ImportError:
        return None
    from fileaudio import getAudioDevice
    return getAudioDevice

def tryOssAudio():
    try:
        import ossaudiodev
    except ImportError:
        return None
    from ossaudio import getAudioDevice
    return getAudioDevice

def tryFastAudio():
    try:
        import fastaudio
    except ImportError:
        return None
    from fast import getAudioDevice
    return getAudioDevice

_audioGet = None
def getAudioDevice(mode, audioPref=None, audioFiles=None):
    from shtoom.exceptions import NoAudioDevice
    global _audioGet
    if _audioGet is None:
        _audioGet = findAudioDevice(audioPref, audioFiles)
        if _audioGet is None:
            raise NoAudioDevice, "No working audio interface found"
    return _audioGet('rw')

