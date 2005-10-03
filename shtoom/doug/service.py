
class DougService:

    configFileName = ''


    def __init__(self, voiceappClass):
        self.voiceappClass = voiceappClass

    def startService(self, mainhack=False, args=None):
        from shtoom.app.doug import DougApplication
        self.app = DougApplication(self.voiceappClass)
        if self.configFileName != '':
            self.app.configFileName = self.configFileName
        if mainhack:
            import __main__
            __main__.app = self.app
        if args is None:
            self.app.boot()
        else:
            self.app.boot(args=args)
        self.app.start()

    def stopService(self):
        self.app.shutdown()
