"""Find appropriate audio device and expose via getAudioDevice().

getAudioDevice() accepts either 'r', 'w' or 'rw' as arguments,
and result will implement shtoom.audio.interfaces.IAudioReader
and/or IAudioWriter, as appropriate.
"""

def findAudioDevice():
    from shtoom import prefs
    attempts = ( tryOssAudio, tryFastAudio, )
    if prefs.audio_infile and prefs.audio_outfile:
        attempts = ( tryFileAudio, )
    if prefs.audio:
        if prefs.audio == 'oss':
            attempts = (tryOssAudio,)
        elif prefs.audio == 'fast':
            attempts = (tryFastAudio,)
        else:
            raise ValueError("unknown audio %s"%(prefs.audio))
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

getAudioDevice = findAudioDevice()
if getAudioDevice is None:
    del getAudioDevice
    # Log an error
