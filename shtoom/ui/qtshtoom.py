
# Feed it hostname, port, and an audio file (in 8bit ulaw - sox -t ul)
# Or skip the audio file and it'll read from the microphone
# See also rtprecv.py for something that listens to a port and dumps it to
# the audio device
#
# Set option 'use_setitimer' for better results - needs
# http://polykoira.megabaud.fi/~torppa/py-itimer/
# $Id: qtshtoom.py,v 1.2 2003/11/16 06:28:16 anthonybaxter Exp $
#

import time, signal, socket, struct
from time import time, sleep

import qt
from twisted.internet import qtreactor

app=qt.QApplication([])
qtreactor.install(app)

from twisted.internet import reactor

def shutdown():
    import itimer
    itimer.setitimer(itimer.ITIMER_REAL, 0.0, 0.0)
    reactor.stop()

def main():
    import sys
    from twisted.internet import reactor
    from twisted.python import log

    start = time()

    from shtoom.ui.qtui import ShtoomMainWindow
    UI = ShtoomMainWindow()
    #UI.setAudioSource(sys.argv[1])
    UI.connectSIP()
    UI.show()
    #log.startLogging(UI.getLogger())
    log.startLogging(sys.stdout)
    
    reactor.addSystemEventTrigger('after', 'shutdown', app.quit )
    app.connect(app, qt.SIGNAL("lastWindowClosed()"), shutdown)

    reactor.run()
    import resource
    rusage = resource.getrusage(resource.RUSAGE_SELF)
    print "%fs user, %fs system, %ds total"%(rusage[0], rusage[1], time()-start )

if __name__ == "__main__":
    main()
