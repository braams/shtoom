

def findAudioDevice():
    for attempt in ( tryOssAudio, ):
	audio = attempt()
	if audio is not None:
	    return audio
    return None


def tryOssAudio():
    try:
	import ossaudiodev
    except ImportError:
	ossaudiodev = None
    if ossaudiodev is not None:
	from ossaudio import getAudioDevice 
	return getAudioDevice
    return None

getAudioDevice = findAudioDevice()
if getAudioDevice is None:
    del getAudioDevice
    # Log an error
