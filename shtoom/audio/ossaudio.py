# Copyright (C) 2003 Anthony Baxter

def getAudioDevice(mode):
    import ossaudiodev
    dev = ossaudiodev.open(mode)
    dev.speed(8000)
    dev.nonblock()
    dev.channels(1)
    dev.setfmt(ossaudiodev.AFMT_MU_LAW)
    return dev
