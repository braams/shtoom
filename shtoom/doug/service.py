
class DougService:

    def __init__(self, voiceappClass):
        self.voiceappClass = voiceappClass

    def startService(self):
        from shtoom.app.doug import DougApplication
        self.app = DougApplication(self.voiceappClass)
        self.app.boot()
        self.app.start()

    def stopService(self):
        self.app.shutdown()
