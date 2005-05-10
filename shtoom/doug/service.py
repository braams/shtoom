
class DougService:

    def __init__(self, voiceappClass):
        self.voiceappClass = voiceappClass

    def startService(self, mainhack=False):
        from shtoom.app.doug import DougApplication
        self.app = DougApplication(self.voiceappClass)
        if mainhack:
            import __main__
            __main__.app = self.app
        self.app.boot()
        self.app.start()

    def stopService(self):
        self.app.shutdown()
