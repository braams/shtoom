import time

from twisted.python.components import Interface

#
# To Do:
#      Make the Tk window on the Mac get raised!
#      Test on Windows, see if it works there
#

_Debug = True

class ISlidable(Interface):
    """ A window that the mover can slide around. The underlying window
        should have override redirect set (so the window manager leaves it
        alone.

        Note very well:

            A window with 'override redirect' set (a Gtk Popup, or
            Tk's Toplevel.overrideredirect(1), can NOT get input focus.
            The window manager ignores it. Things you click on will work.
            Things you attempt to type into will NOT work.
    """

    def getScreenSize():
        "Returns (screenx, screeny)"

    def getWindowSize():
        "Returns (windowx, windowy)"

    def getPosition():
        "Returns current window position, as (rootx, rootx)"

    def movePosition((x, y)):
        "Move the window to (x,y)"

    def windowShown():
        "Called when the window is fully shown"

    def windowHidden():
        "Called when the window is fully hidden"

    def callLater(time, callable, *args):
        "UI-specific callLater"

class ISlider(Interface):
    """ A Slider slides a notification window in and out.
        Ctor args:
           win: an ISlidable window
           showTime: how long (in seconds) to take to display the
                     notification (default 1s)
           hideTime: how long to take to remove it
           offset: how far in from the corners to position the notification
    """

    def show(direction):
        """ Slide the window in from the direction specified. Direction
            should be one of
              'n', 'nne', 'ene', 'e', 'ese', 'sse',
              's', 'ssw', 'wsw', 'w', 'wnw', 'nnw'
        """

    def hide():
        """ Hide the window """


endPosition = {
    'n': lambda (sx, sy), (wx, wy), off:   ((sx-wx)/2, off),
    'nne': lambda (sx, sy), (wx, wy), off: (sx-wx-off, off),
    'ene': lambda (sx, sy), (wx, wy), off: (sx-wx-off, off),
    'e': lambda (sx, sy), (wx, wy), off:   (sx-wx-off,(sy-wy)/2),
    'ese': lambda (sx, sy), (wx, wy), off: (sx-wx-off,sy-wy-off),
    'sse': lambda (sx, sy), (wx, wy), off: (sx-wx-off,sy-wy-off),
    's': lambda (sx, sy), (wx, wy), off:   ((sx-wx)/2, sy-wy-off),
    'ssw': lambda (sx, sy), (wx, wy), off: (off, sy-wy-off),
    'wsw': lambda (sx, sy), (wx, wy), off: (off, sy-wy-off),
    'w': lambda (sx, sy), (wx, wy), off:   (off, (sy-wy)/2),
    'wnw': lambda (sx, sy), (wx, wy), off: (off, off),
    'nnw': lambda (sx, sy), (wx, wy), off: (off, off),
}

delta = {
    'nnw':  (0, 1),
    'n':    (0, 1),
    'nne':  (0, 1),
    'ene':  (-1, 0),
    'e':    (-1, 0),
    'ese':  (-1, 0),
    'sse':  (0, -1),
    's':    (0, -1),
    'ssw':  (0, -1),
    'wsw':  (1, 0),
    'w':    (1, 0),
    'wnw':  (1, 0),
}


def updatepos(cur, delta, final):
    # Update a number from 'cur' to 'final', making sure not to go past
    # final.
    new = cur + delta
    if delta == 0:
        if new != final:
            if abs(new-final) < 3:
                # mmm fuzz factor
                if _Debug: print "fuzzing %d to %d"%(new, final)
                return final
            else:
                raise ValueError('asked to not move %d to %d'%(cur, final))
        else:
            return cur
    elif delta > 0:
        if new < final:
            return new
        if new >= final:
            return final
    elif delta < 0 :
        if new > final:
            return new
        if new <= final:
            return final


class Slider:
    __implements__ = (ISlider,)

    stepTime = 0.020

    def __init__(self, win, showTime=1.0, hideTime=0.5, offset=20):
        self.win = win
        self.showTime = showTime
        self.hideTime = hideTime
        self.offset = offset
        self.direction = None

    def show(self, direction):
        # Because too often, the window changes size!
        self.winX, self.winY = self.win.getWindowSize()
        direction = direction.lower()
        if not endPosition.get(direction):
            raise ValueError("dont know direction %s should be one of (%s)"%(
                direction, ', '.join(endPosition.keys())))
        self.direction = direction
        self._startMoving(self.direction, show=True)

    def hide(self):
        if self._cl is not None:
            self._cl.cancel()
        if not self.direction:
            raise ValueError("call .show first")
        self._startMoving(self.direction, show=False)

    def _startMoving(self, direction, show=True):
        from twisted.internet import reactor
        sx, sy = self.win.getScreenSize()
        wx, wy = self.winX, self.winY
        if _Debug: print "window is", wx, wy
        dx, dy = delta[direction]
        showx, showy = endPosition[direction]((sx,sy),(wx,wy),self.offset)
        hidex = showx + (-dx * (wx+self.offset))
        hidey = showy + (-dy * (wy+self.offset))
        distance = max(abs(showx-hidex), abs(showy-hidey))

        if show:
            steps = float(self.showTime) / self.stepTime
            startx, starty = hidex, hidey
            endx, endy = showx, showy
        else:
            steps = float(self.hideTime) / self.stepTime
            startx, starty = self.win.getPosition()
            endx, endy = hidex, hidey
            dx, dy = -dx, -dy

        if _Debug: print "show/hide", (showx,showy),(hidex,hidey)
        if _Debug: print "Moving from", (startx,starty), "to", (endx,endy)
        dx = dx * (distance/steps)
        dy = dy * (distance/steps)
        if _Debug: print "distance", distance, "in", steps, "deltas", (dx,dy)
        if show:
            if _Debug: print "jumping to",(startx, startx)
            self.win.movePosition((int(startx), int(starty)))
        if _Debug: print "jumped to",(startx, starty)
        self._cl = self.win.callLater(self.stepTime,
            self._moveTo, (startx,starty), (dx,dy), (endx,endy), show)

    def _moveTo(self, (cx,cy), (dx,dy), (fx,fy), show):
        from twisted.internet import reactor
        nx = updatepos(cx, dx, fx)
        ny = updatepos(cy, dy, fy)
        self.win.movePosition((int(nx), int(ny)))
        if (nx,ny) == (fx,fy):
            self._cl = None
            if show:
                self.win.windowShown()
            else:
                self.win.windowHidden()
            if _Debug:
                print "done with this one"
        else:
            self._cl = self.win.callLater(self.stepTime,
                    self._moveTo, (nx,ny), (dx,dy), (fx,fy), show)


class SliderDemo:
    def __init__(self, slidableClass):
        self.slidable = slidableClass(self)
        self.mover = Slider(self, hideTime=0.25)
        self._cl = None

    def getScreenSize(self):
        return self.slidable.getScreenSize()

    def getWindowSize(self):
        return self.slidable.getWindowSize()

    def getPosition(self):
        return self.slidable.getPosition()

    def movePosition(self, (x, y)):
        self.slidable.movePosition((x,y))

    def callLater(self, *args):
        return self.slidable.callLater(*args)

    def hide(self):
        if self._cl is not None:
            self._cl.cancel()
            self._cl = None
        self.mover.hide()

    def timeout(self, d):
        if d == self.cd:
            self._cl = None
            self.hide()

    def windowShown(self):
        from twisted.internet import reactor
        self._cl = self.slidable.callLater(2, lambda d=self.cd: self.timeout(d))

    def windowHidden(self):
        from twisted.internet import reactor
        self.slidable.callLater(1, self.nextDirection)

    def nextDirection(self):
        from twisted.internet import reactor
        if not self.directions:
            self.slidable.callLater(2, reactor.stop)
        else:
            if hasattr(self.slidable, 'demoText'):
                self.slidable.demoText('%25s'%(
                            'This is direction %s'%self.directions[0]))
            self.cd = self.directions.pop(0)
            self.slidable.callLater(0, self.mover.show, self.cd)

    def demo(self):
        from twisted.internet import reactor
        self.directions = ['n','nne','ene','e','ese','sse',
                           's','ssw','wsw','w','wnw','nnw']
        self.slidable.callLater(0, self.nextDirection)
