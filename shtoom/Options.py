# Copyright (C) 2004 Anthony Baxter

# Generic option handling. This will eventually become a package,
# with the UI-specific preferences handling as a part of it.

import os

class OptionValueInvalid(Exception):
    pass

class _NoDefaultOption: pass

NoDefaultOption = _NoDefaultOption()

class Option(object):
    _value = NoDefaultOption
    _default = NoDefaultOption
    _dynamic = False
    optionType = 'Option'

    def __init__(self, name='', description='', default=NoDefaultOption, shortopt=''):
        self._name = name
        if default is not NoDefaultOption:
            self._default = default
        self._description = description
        self._shortopt = shortopt

    def getValue(self):
        return self._value

    def getName(self):
        return self._name

    def getDefault(self):
        return self._default

    def setValue(self, value):
        self.validate(value)
        value = self.massageValue(value)
        return self._setValue(value)

    def validate(self, value):
        return

    def massageValue(self, value):
        return value

    def _setValue(self, value):
        ovalue = self._value
        self._value = value
        if ovalue != value:
            # Modified. Signal that.
            return True
        else:
            return False

    def getCmdLineOption(self):
        n = self._name
        n = n.replace('_', '-')
        return '--%s'%n

    def getCmdLineType(self):
        return None

    def getPrettyName(self):
        n = self._name
        n = n.replace('_', ' ')
        return n

    def getDescription(self):
        return self._description

    def buildOptParse(self, parser):
        t = self.getCmdLineType()
        if t:
            t.update({'dest':self._name, 'help':self._description, 'default':self._default})
        else:
            t = {'dest':self._name, 'help':self._description, 'default':self._default}
        if self._shortopt:
            short = '-'+self._shortopt
        else:
            short = ''
        parser.add_option(short, self.getCmdLineOption(), **t)

    # A dynamic option is not written to any stored config file
    def getDynamic(self):
        return self._dynamic

    def setDynamic(self, dynamic):
        self._dynamic = dynamic

class BooleanOption(Option):

    _default = False
    optionType = 'Boolean'

    def massageValue(self, value):
        if isinstance(value, str):
            if value.lower() in ( 'true', '1', 't', 'y', 'yes' ):
                return True
            elif value.lower() in ( 'false', '0', 'f', 'n', 'no' ):
                return False
            else:
                raise OptionValueInvalid, value
        elif value in ( True, 1, ):
            return True
        elif value in ( False, 0, ):
            return False
        else:
            raise OptionValueInvalid("expected a true/false value, got %r"%(value))

    def getCmdLineType(self):
        if self._default is False:
            return { 'action':'store_true' }
        elif self._default is True:
            return { 'action':'store_false' }
        else:
            raise ValueError, "Boolean must default to True or False, not %r"%self._default

class StringOption(Option):
    optionType = 'String'

    def massageValue(self, value):
        if not isinstance(value, basestring):
            # print a warning
            value = str(value)
        if not value:
            value = self._default
        return value

class PasswordOption(StringOption):
    optionType = 'Password'

class ChoiceOption(Option):
    optionType = 'Choice'

    def __init__(self, name='', description='', default=NoDefaultOption, choices=[], shortopt=''):
        self._choices = choices
        Option.__init__(self, name, description, default, shortopt)

    def validate(self, value):
        if not isinstance(value, basestring):
            # print a warning
            value = str(value)
        if not value in self._choices:
            raise OptionValueInvalid("%s is not one of %s"%(value, ', '.join(self._choices)))

    def getChoices(self):
        return self._choices[:]

class NumberOption(Option):
    optionType = 'Number'

    def massageValue(self, value):
        if value is NoDefaultOption:
            return value
        if not isinstance(value, int):
            # print a warning
            value = int(value)
        return value

    def validate(self, value):
        if value is NoDefaultOption:
            return
        try:
            int(value)
        except ValueError:
            raise OptionValueInvalid("expected a number, got %r"%(value))

    def getCmdLineType(self):
        return { 'type':'int' }

class OptionGroup(object):

    def __init__(self, name='', description='', gui=True):
        self._name = name
        self._description = description
        self._options = []
        self._gui = gui

    def getGUI(self):
        return self._gui

    def getName(self):
        return self._name

    def getDescription(self):
        return self._description

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
        self._filename = None
        self._cached_options = {}

    def __iter__(self):
        for g in self._groups:
            yield g

    def addGroup(self, group):
        self._groups.append(group)

    def buildOptParse(self, parser):
        [ g.buildOptParse(parser) for g in self ]

    def handleOptParse(self, opts, args):
        for g in self:
            for o in g:
                val = getattr(opts, o.getName())
                if val is not NoDefaultOption and val is not None:
                    o.setValue(val)

    def setOptions(self, opts):
        for group in self:
            for opt in group:
                key, val = opt.getName(), opt.getValue()
                if val is not NoDefaultOption and val is not None:
                    setattr(opts, key, val)

    def emitConfigParser(self):
        out = []
        for g in self:
            thisblock = {}
            for o in g:
                if o.getValue() is not o.getDefault() and not o.getDynamic():
                    thisblock[o.getName()] = o.getValue()
            if thisblock:
                out.append('[%s]'%g.getName())
                for k,v in thisblock.items():
                    out.append("%s=%s"%(k, v))
                out.append('')
        return '\n'.join(out)

    def setOptsFile(self, filename):
        if filename is None:
            self._filename = None
        else:
            d = findOptionsDir()
            self._filename = os.path.join(d, filename)

    def loadOptsFile(self):
        from ConfigParser import SafeConfigParser
        if self._filename is None:
            return None
        cfg = SafeConfigParser()
        if hasattr(os, 'access'):
            if not os.access(self._filename, os.R_OK|os.W_OK):
                return
        try:
            cfg.readfp(open(self._filename, 'rU'))
        except IOError:
            return
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

    def updateOptions(self, dict=None, **kw):
        modified = {}
        if dict is None:
            dict = kw

        for g in self:
            for o in g:
                n = o.getName()
                if dict.get(n) is not None:
                    if dict[n] == '' and o.optionType == 'Number':
                        if o.setValue(o.getDefault()):
                            modified[n] = o.getDefault()
                    elif o.setValue(dict[n]):
                        modified[n] = dict[n]
                    else:
                        pass
        # If any changed, clear the cache
        return modified

    def setValue(self, option, value=NoDefaultOption, dynamic=False):
        if value is NoDefaultOption:
            # Unset the value
            raise ValueError, "unsetting options dynamically is not supported"
        else:
            for g in self:
                for o in g:
                    if o.getName() == option:
                        o.setValue(value)
                        del self._cached_options[option]
                        o.setDynamic(dynamic)

    def getValue(self, option, dflt=NoDefaultOption):
        if not self._cached_options.has_key(option):
            for g in self:
                for o in g:
                    self._cached_options[o.getName()] = o
        val = self._cached_options[option].getValue()
        if val is NoDefaultOption:
            val = dflt
        return val

    def optionsStartup(self, version='%prog'):
        import optparse
        parser = optparse.OptionParser(version=version)
        self.buildOptParse(parser)
        (opts, args) = parser.parse_args()
        if getattr(opts, 'no_config_file'):
            self.setOptsFile(None)
        self.loadOptsFile()
        self.handleOptParse(opts, args)
        self.saveOptsFile()

def findOptionsDir():
    try:
        saveDir = os.path.expanduser('~%s'%os.getlogin())
    except:
        saveDir = os.getcwd()
    return saveDir
