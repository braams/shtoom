# A bare-bones SOAP client (needed for UPnP). I know it probably doesn't
# do everything, and I also don't care - as long as it allows UPnP to work,
# it's met it's design goal. Feel free to send patches to improve it, so long as
# you don't make it suck any more than it does already.

# (C) Copyright 2004 Anthony Baxter

from twisted.python import log

import urllib2

##########
# AAAAARGH
##########
import sgmllib, re
sgmllib.tagfind = re.compile('[a-zA-Z][-_.:a-zA-Z0-9]*')


class SOAPError(Exception):
    pass

try:
    from BeautifulSoup import BeautifulSoup, Tag, NavigableText
except ImportError:
    from shtoom.compat.BeautifulSoup import BeautifulSoup, Tag, NavigableText

from xml.sax.handler import ContentHandler
from xml.sax import parseString

class _BeautifulSaxParser(ContentHandler, Tag):
    "An XML Parser (using SAX) that generates BeautifulSoup objects"
    crackfulXML = False

    def __init__(self):
        self.tagStack = []
        self.currentData = ''
        self.currentTag = None
        self.pushTag(self)
        ContentHandler.__init__(self)
        Tag.__init__(self, '[document]')

    def pushTag(self, tag):
        if self.currentTag:
            self.currentTag.append(tag)
        self.tagStack.append(tag)
        self.currentTag = self.tagStack[-1]

    def popTag(self, name):
        # We stuff tags with no attributes and only text inside it as
        # attributes on the parent
        if self.crackfulXML and len(self.tagStack) > 1:
            tag = self.tagStack[-1]
            parent = self.tagStack[-2]
            parent._getAttrMap()
            if ( isinstance(tag, Tag) and
                             len(tag.contents) == 1 and
                             isinstance(tag.contents[0], NavigableText) and
                             not parent.attrMap.has_key(tag.name) ):
                parent[tag.name] = str(tag.contents[0])
                parent.attrs.append((tag.name, str(tag.contents[0])))
        tag = self.tagStack.pop()
        if tag.name != name:
            raise ValueError("expected to pop %s, but got %s"%(name, tag.name))
        self.currentTag = self.tagStack[-1]
        return self.currentTag

    def endData(self):
        if self.currentData:
            if not self.currentData.strip():
                if '\n' in self.currentData:
                    self.currentData = '\n'
                else:
                    self.currentData = ' '
            o = NavigableText(self.currentData, self.currentTag, self.previous)
            if self.previous:
                self.previous.next = o
            self.previous = o
            self.currentTag.contents.append(o)
        self.currentData = ''

    def startElement(self, name, attrs):
        #print "startElement", name, attrs, dir(attrs)
        self.endData()
        tag = Tag(name, attrs.items(), self.currentTag, self.previous)
        if self.previous:
            self.previous.next = tag
        self.previous = tag
        self.pushTag(tag)

    def endElement(self, name):
        #print "endElement", name
        self.endData()
        self.popTag(name)

    def characters(self, content):
        #print "characters", content
        self.currentData += content

    def _checkContents(self, obj, name):
        results = []
        for i in obj.contents:
            if isinstance(i, Tag):
                if ':' in i.name:
                    n = i.name
                    if type(n) is unicode:
                        # why must the world torture me this way??
                        n = n.encode('iso8859-1','replace')
                    uname = n.split(':')[-1]
                    if uname == name:
                        results.append(i)
                elif name == i.name:
                    results.append(i)
                if i.contents:
                    results.extend(self._checkContents(i, name))
        return results

    def fetchNameNoNS(self, name):
        "A much stupider version of fetch that only ignores XML namespaces"
        return self._checkContents(self, name)




def BeautifulSax(data):
    bs = _BeautifulSaxParser()
    parseString(data, bs)
    return bs

def BeautifulSoap(data):
    bs = _BeautifulSaxParser()
    bs.crackfulXML = True
    parseString(data, bs)
    return bs

class SOAPRequestFactory:
    """A Factory object for SOAP Requests, which can then be passed to
       either urllib2 or nonsuckhttp.
    """
    def __init__(self, url, prefix=None):
        self.url = url
        self._prefix = prefix
        self.scpd = None

    def setSCPD(self, data):
        self.scpd = parseSCPD(data)

    def _set_prefix(self, prefix):
        if self._prefix is not None:
            log.msg('warning: resetting soap prefix from %s to %s'%(
                                                    self._prefix, prefix))
        self._prefix=prefix
    prefix = property(None, _set_prefix, None)

    def _methodCall(self, name, **kwargs):
        arglist = []
        log.msg("called %s(%s)"%(name,
                ', '.join([ ('%s=%s'%x) for x in kwargs.items()])
                          ), system='SOAP')
        if self.scpd:
            self.scpd.checkCall(name, **kwargs)
        for k,v in kwargs.items():
            if v is None:
                arglist.append('<%s></%s>'%(k,k))
            else:
                arglist.append('<%s>%s</%s>'%(k,v,k))
        arglist = '\r\n'.join(arglist)
        # If/when stan gets broken out of Nevow, I'll look at using it here,
        # instead of the canned XML. I'm not happy to make shtoom depend on
        # Nevow for all platforms, particularly if it's only for this piece
        # of trivial code.
        body = _CannedSoapHorror % dict(arglist=arglist,
                                       prefix=self._prefix,
                                       method=name)
        body = body.encode('utf-8')
        headers = { 'SOAPAction': '"%s#%s"'%(self._prefix,name) }
        req = urllib2.Request(self.url, body, headers)
        req.soapURN = self._prefix
        req.soapMethod = name
        req.soapArgs = kwargs
        return req

    def __str__(self):
        return "<SOAPRequestFactory %s %s>"%(self.url, self._prefix)

    def __getattr__(self, name):
        return lambda **kw: self._methodCall(name, **kw)

def SOAPResponseFactory(request, response):
    urn = request.soapURN
    method = request.soapMethod
    if response.status == 200:
        data = response.read()
        # Netgear's on my fucking list of death!
        if data[-1] == chr(0):
            data = data[:-1]
        bs = BeautifulSoap(data)
        key = '%sResponse'%(request.soapMethod)
        log.msg('response for %s'%request.soapMethod, system='SOAP')
        r = bs.fetchNameNoNS(key)
        if not r:
            raise SOAPError("couldn't find %s in response"%(key))
        r = r[0]
        out = {}
        for c in r.contents:
            if isinstance(c, Tag):
                if len(c.contents) == 1:
                    if out.get(c.name):
                        print "duplicated %s in response"%(c)
                    else:
                        out[c.name] = str(c.contents[0])
                elif not c.contents:
                    out[c.name] = None
                else:
                    print "got value for %s with contents %r"%(c.name, c)
            elif str(c).strip():
                print "got unexpected %s in response"%(c)
        return out
    else:
        print "ick. got non-200 response", response.status
        print request,response
        #print bs
    return response

def SOAPErrorFactory(request, httperror):
    # At this point, response is a HTTPError object
    data = httperror.response.read()
    if data[-1] == chr(0):
        data = data[:-1]
    body = BeautifulSoap(data)
    error = body.first('errorDescription')
    if error:
        log.msg('error %s for %s'%(error, request.soapMethod), system='SOAP')
        raise SOAPError(str(error.contents[0]))
    else:
        log.msg('unspecified error for %s'%(request.soapMethod), system='SOAP')
        raise SOAPError(str(body))

def soapenurl(request):
    from nonsuckhttp import urlopen
    d = urlopen(request)
    factory = lambda response: SOAPResponseFactory(request, response)
    errfactory = lambda response: SOAPErrorFactory(request, response.value)
    d.addCallbacks(factory, errfactory)
    return d


# Canned for now
_CannedSoapHorror = u"""<?xml version="1.0"?>\r
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\r
    <s:Body>\r
        <u:%(method)s xmlns:u="%(prefix)s">\r
            %(arglist)s\r
        </u:%(method)s>\r
    </s:Body>\r
</s:Envelope>\r
"""


class SoapArgument(object):
    __slots__ = [ 'direction', 'name', 'relatedStateVariable' ]

class SoapAction(object):
    __slots__ = [ 'name', 'arguments','inargs', 'outargs' ]
    def __init__(self):
        self.name = 'unset'
        self.arguments = []
        self.inargs = {}
        self.outargs = {}

    def addArgument(self, arg):
        self.arguments.append(arg)
        if arg.direction == 'in':
            self.inargs[arg.name] = arg
        elif arg.direction == 'out':
            self.outargs[arg.name] = arg

    def __str__(self):
        return "<SoapAction %s, taking %d arguments>"%(self.name, len(self.arguments))

class SoapVariable(object):
    __slots__ = [ 'name', 'dataType', 'allowedValues' ]
    def __init__(self):
        self.allowedValues = []

def tagContents(bs):
    return [ x for x in bs.contents if isinstance(x, Tag) ]

class SCPD:
    def __init__(self):
        self.actions = {}
        self.variables = {}

    def checkCall(self, name, **kwargs):
        "Validate the name and arguments"
        action = self.actions.get(name)
        if not action:
            raise NameError('No such SOAP request %s'%(name))
        for val in kwargs.keys():
            arg = action.inargs.get(val)
            if not arg:
                raise TypeError("%s got unexpected keyword argument '%s'"%(
                                                    name, val))
        # More checking here - check types, check required values, &c

    def dump(self):
        for action in self.actions.values():
            inargs = [ x for x in action.arguments if x.direction == 'in' ]
            outargs = [ x for x in action.arguments if x.direction == 'out' ]
            print
            print "def %s(%s):"%(action.name,
                                 ', '.join([x.name for x in inargs]))
            print '    """'
            if inargs:
                print "    Argument Types"
            for arglist in (inargs, None, outargs):
                if arglist is None:
                    if outargs:
                        print "    Returns:"
                    continue
                for arg in arglist:
                    rsv = arg.relatedStateVariable
                    var = self.variables[rsv]
                    if var.allowedValues:
                        allowed = ', '.join(var.allowedValues)
                        allowed = "["+allowed+"]"
                    else:
                        allowed = ''
                    print "        %s(%s) %s"%(arg.name, var.dataType, allowed)
            print '    """'

def parseSCPD(xml):
    scpd = SCPD()
    bs = BeautifulSax(xml)
    actionListXML = bs.first('actionList')

    for actionXML in tagContents(actionListXML):
        if actionXML.name != 'action':
            raise ValueError('expected action, got %s'%(actionXML.name))
        action = SoapAction()
        # strip whitespace crap
        for item in tagContents(actionXML):
            if item.name == 'name':
                action.name = str(item.contents[0])
            if item.name == 'direction':
                action.direction = str(item.contents[0])
            if item.name == 'argumentList':
                for argXML in tagContents(item):
                    if argXML.name != 'argument':
                        raise ValueError('expected argument, got %s'%(
                                                                argXML.name))
                    arg = SoapArgument()
                    for bits in tagContents(argXML):
                        setattr(arg, bits.name, str(bits.contents[0]))
                    action.addArgument(arg)
        scpd.actions[action.name] = action

    variableXML = bs.first('serviceStateTable')
    for varXML in tagContents(variableXML):
        if varXML.name != 'stateVariable':
            raise ValueError('expected stateVariable, got %s'%(varXML.name))
        var = SoapVariable()
        for bit in tagContents(varXML):
            if bit.name == 'name':
                var.name = str(bit.contents[0])
            if bit.name == 'dataType':
                var.dataType = str(bit.contents[0])
            if bit.name == 'allowedValueList':
                for av in tagContents(bit):
                    var.allowedValues.append(str(av.contents[0]))
        scpd.variables[var.name] = var
    return scpd
