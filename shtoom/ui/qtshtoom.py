
# Copyright (C) 2003 Anthony Baxter
# $Id: qtshtoom.py,v 1.3 2003/11/16 06:49:58 anthonybaxter Exp $
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
