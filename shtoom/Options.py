class OptionValueInvalid(Exception): 
    pass

class _NoDefaultOption: pass

NoDefaultOption = _NoDefaultOption()

class Option(object):
    _value = NoDefaultOption
    _default = NoDefaultOption

    def __init__(self, name='', description='', default=NoDefaultOption):
        self._name = name
        if default is not NoDefaultOption:
            self._default = default
        self._description = description

    def getValue(self):
        return self._value

    def getName(self):
        return self._name

    def getDefault(self):
        return self._default

    def setValue(self, value):
        if not self.validate(value):
            raise OptionValueInvalid, value
        value = self.massageValue(value)
        self._setValue(value)

    def validate(self, value):
        return True

    def massageValue(self, value):
        return value

    def _setValue(self, value):
        self._value = value

    def getCmdLineOption(self):
        n = self._name
        n = n.replace('_', '-')
        return '--%s'%n

    def getCmdLineType(self):
        return None

    def buildOptParse(self, parser):
        t = self.getCmdLineType()
        if t:
            t.update({'dest':self._name, 'help':self._description, 'default':self._default})
        else:
            t = {'dest':self._name, 'help':self._description, 'default':self._default}
        parser.add_option(self.getCmdLineOption(), **t)

class BooleanOption(Option):

    _default = False

    def setValue(self, value):
        if isinstance(value, str):
            if value.lower() in ( 'true', '1', 't', 'y', 'yes' ):
                self._value = True
            elif value.lower() in ( 'false', '0', 'f', 'n', 'no' ):
                self._value = False
            else:
                raise OptionValueInvalid, value
        elif value in ( True, 1, ):
            self._value = True
        elif value in ( False, 0, ):
            self._value = False
        else:
            raise OptionValueInvalid, value

    def getCmdLineType(self):
        if self._default is False:
            return { 'action':'store_true' }
        elif self._default is True:
            return { 'action':'store_false' }
        else:
            raise ValueError, "Boolean must default to True or False, not %r"%self._default

class StringOption(Option):

    def massageValue(self, value):
        if not isinstance(value, basestring):
            # print a warning
            value = str(value)
        return value


class ChoiceOption(Option):

    def __init__(self, name='', description='', default=NoDefaultOption, choices=[]):
        self._choices = choices
        Option.__init__(self, name, description, default)

    def validate(self, value):
        if value in self._choices:
            return True
        else:
            return False

class NumberOption(Option):

    def massageValue(self, value):
        if not isinstance(value, int):
            # print a warning
            value = int(value)
        return value

    def validate(self, value):
        try:
            int(value)
        except ValueError:
            return False
        else:
            return True

    def getCmdLineType(self):
        return { 'type':'int' }

class OptionGroup(object):
    def __init__(self, name='', description=''):
        self._name = name
        self._description = description
        self._options = []

    def getName(self):
        return self._name

    def __iter__(self):
        for o in self._options:
            yield o

    def addOption(self, option):
        self._options.append(option)

    def buildOptParse(self, parser):
        for o in self._options:
            o.buildOptParse(parser)

class AllOptions(object):
    def __init__(self):
        self._groups = []

    def __iter__(self):
        for g in self._groups:
            yield g

    def addGroup(self, group):
        self._groups.append(group)

    def buildOptParse(self, parser):
        for g in self:
            g.buildOptParse(parser)

    def handleOptParse(self, opts, args):
        import shtoom.prefs


        for g in self:
            for o in g:
                val = getattr(opts, o.getName())
                if val is not NoDefaultOption and val is not None:
                    o.setValue(val)

    def emitConfigParser(self):
        out = []
        for g in self:
            thisblock = {}
            for o in g:
                if o.getValue() is not o.getDefault():
                    thisblock[o.getName()] = o.getValue()
            if thisblock:
                out.append('[%s]'%g.getName())
                for k,v in thisblock.items():
                    out.append("%s=%s"%(k, v))
                out.append('')
        return '\n'.join(out)

    def setOptsFile(self, filename):
        self._filename = filename

    def loadOptsFile(self):
        from ConfigParser import SafeConfigParser
        if self._filename is None:
            return None
        cfg = SafeConfigParser()
        cfg.readfp(open(self._filename, 'rU'))
        for g in self:
            gname = g.getName()
            if cfg.has_section(gname):
                for o in g:
                    oname = o.getName()
                    if cfg.has_option(gname, oname):
                        val= cfg.get(gname, oname)
                        o.setValue(val)

    def saveOptsFile(self):
        if self._filename is None:
            return None
        ini = self.emitConfigParser()
        if ini:
            fp = open(self._filename, 'wU')
            fp.write(ini)
            fp.close()

    def setOptions(self):
        import shtoom.prefs
        for group in self:
            for opt in group:
                key, val = opt.getName(), opt.getValue()
                if val is not NoDefaultOption and val is not None:
                    setattr(shtoom.prefs, key, val)

