from twisted.python.log import err, msg
from twisted.python import log

try:
    from twisted.python.util import untilConcludes
except ImportError:
    def untilConcludes(f, *a, **kw):
        return f(*a, **kw)


class SaneLogObserver:
    """Log observer that writes to a file-like object, and is sane"""
    # Will be further-refactored to make it even cleaner
    NL='\n'

    def __init__(self, fp):
        self.fp = fp

    def formatMessage(self, eventDict):
        text = None
        msg = eventDict.get('message')
        if msg:
            text = ' '.join([str(x) for x in msg])
        elif eventDict['isError'] and 'failure' in eventDict:
            text = eventDict['failure'].getTraceback()
        elif eventDict.has_key('format'):
            try:
                text = eventDict['format'] % eventDict
            except:
                text = "Invalid format in log event '%r'"%(eventDict,)
        return text

    def formatTime(self, t):
        "Return a time string"
        import time, datetime
        if not t:
            t = time.time()
        return datetime.datetime.fromtimestamp(t).isoformat()

    def emit(self, eventDict):
        text = self.formatMessage(eventDict)
        if text is None:
            # Don't know how to format this entry, so dump it
            return
        # Indent all but first line
        text = text.replace(self.NL, self.NL+'\t')
        timestamp = self.formatTime(eventDict.get('time'))
        output = '%s [%s] %s%s'%(timestamp, eventDict.get('system', '-'),
                                text, self.NL)
        self.output(output)

    def output(self, output):
        untilConcludes(self.fp.write, output)
        untilConcludes(self.fp.flush)

    def start(self):
        """Start observing log events."""
        log.addObserver(self.emit)

    def stop(self):
        """Stop observing log events."""
        log.removeObserver(self.emit)

def startLogging(fp, *a, **kw):
    obs = SaneLogObserver(fp)
    log.startLoggingWithObserver(obs.emit, *a, **kw)
