import shtoom.ui.wizards as wiz

class DemoWizard(wiz.Wizard):

    title = 'Demonstration Wizard'
    entry = ''
    entry2 = 'default second entry'
    pick = ''
    onoff = True

    def aborted(self):
        print "User aborted the wizard"

    def completed(self):
        print "final values:", self.entry, self.entry2, self.pick, self.opt

    def start(self):
        page = wiz.Page('Demonstration - Page 1', [
                 wiz.Label('intro', 'This is the first page of a wizard, with some very very very very very very very very very very long introductory text'),
                 wiz.Text('entry2', 'Some more text', default=self.entry2),
                 wiz.Password('entry', 'Enter a secret', default=self.entry),
                 wiz.Choice('pick', 'Choose a number', choices=['one', 'two', 'three'],
                                                     default=self.pick),
                 wiz.Boolean('onoff', 'Select on or off', default=self.onoff),
                 wiz.Label('outro', 'Make your choices and hit Next'),
              ], (('Next', self.handlePageOne), ('Cancel', self.cancelled)))
        print self.onoff
        return page

    def handlePageOne(self, **args):
        from twisted.internet import defer, reactor
        # Save the values we get
        print "got", args
        self.__dict__.update(args)

        page = wiz.Page('Demonstration - Page 2',
                        [wiz.Label('thanks', 'Thank You'),],
                        (('Back', self.start), ('Finish', self.finished),))
        d = defer.Deferred()
        reactor.callLater(1, d.callback, page)
        return d

    def finished(self, **args):
        print "finished got", args
        return None

    def cancelled(self, **args):
        print "cancelled got", args
