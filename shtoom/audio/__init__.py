"""Find appropriate audio device and expose via getAudioDevice().

getAudioDevice() accepts either 'r', 'w' or 'rw' as arguments,
and result will implement shtoom.audio.interfaces.IAudioReader
and/or IAudioWriter, as appropriate.
"""

def findAudioDevice():
    for attempt in (tryOssAudio, tryFastAudio):
	audio = attempt()
	if audio is not None:
	    return audio
    return None


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

getAudioDevice = findAudioDevice()
if getAudioDevice is None:
    del getAudioDevice
    # Log an error
