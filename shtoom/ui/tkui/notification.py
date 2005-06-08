
from shtoom.ui.slider import ISlidable, Slider

class TkSlidingWindow:
    __implements__ = (ISlidable,)

    def getScreenSize(self):
        return (self.win.winfo_screenwidth(), self.win.winfo_screenheight())

    def getWindowSize(self):
        return (self.win.winfo_width(), self.win.winfo_height())

    def getPosition(self):
        return (self.win.winfo_rootx(), self.win.winfo_rooty())

    def movePosition(self, (x, y)):
        self.win.geometry('+%d+%d'%(x,y))

    def windowHidden(self):
        pass

    def windowShown(self):
        pass

    def callLater(self, time, callable, *args):
        from twisted.internet import reactor
        return reactor.callLater(time, callable, *args)

def demo():
    from twisted.internet import reactor, tksupport
    from shtoom.ui.slider import SliderDemo

    class TkDemoWindow(TkSlidingWindow):

        def __init__(self, parent):
            from Tkinter import Tk, Label, Button
            self.parent = parent
            self.win = Tk(className='moving')
            self.win.overrideredirect(1)
            self.win.tkraise()
            self.label = Label(self.win, text=' '*25, font='fixed')
            self.label.pack(padx=20, pady=10)
            self.button = Button(self.win, text='OK', command=self.parent.hide)
            self.button.pack(pady=5)
            tksupport.install(self.win)

        def demoText(self, text):
            self.label.configure(text=text)
            self.win.geometry('+%d+%d'%self.getScreenSize())
            self.label.pack()

    demo = SliderDemo(TkDemoWindow)
    demo.demo()

if __name__ == "__main__":
    from twisted.internet import reactor
    reactor.callLater(0, demo)
    reactor.run()
