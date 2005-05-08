#!/usr/bin/env python

# Copyright (C) 2004 Anthony Baxter

# Hack hack hack.
import sys, os
f = sys.path.pop(0)
if f.endswith('scripts') and os.path.isdir(os.path.join(os.path.dirname(f),
                                                        'shtoom')):
    sys.path.insert(0, os.path.dirname(f))
else:
    sys.path.append(f)

app = None

def main():
    from twisted.python import threadable
    threadable.init(1)

    from shtoom.app.phone import Phone
    global app

    app = Phone()
    app.boot(args=sys.argv[1:])

    audioPref = app.getPref('audio')

    from twisted.python import log
    log.msg("Getting new audio device", system='phone')

    from shtoom.audio import getAudioDevice
    # XXX Aarrgh.
    app._audio = getAudioDevice()
    log.msg("Got new audio device %s :: %s" % (app._audio, type(app._audio),))

    def run_it():
        app.start()

    def run_it_with_profiling():
        import profile
        p = profile.Profile()
        p.runcall(app.start)
        import tempfile
        (tmpfile, tmpfname,) = tempfile.mkstemp(prefix='shtoomphone')
        p.dump_stats(tmpfname)
        del p

    run_it()
    # run_it_with_profiling()

if __name__ == "__main__":
    from shtoom import i18n
    i18n.install()
    main()
