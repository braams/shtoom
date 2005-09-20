# Copyright (C) 2004 Anthony Baxter

# Generic option handling. This will eventually become a package,
# with the UI-specific preferences handling as a part of it.

import os
import shtoom.schema
from shtoom.schema import NoDefaultValue as NoDefaultOption
from shtoom.schema import Boolean, String, List, Choice, Dict, Password, Integer

OptionGroup = List
OptionDict = Dict
StringOption = String
PasswordOption = Password
NumberOption = Integer
BooleanOption = Boolean
DuplicateOptionError = shtoom.schema.DuplicateItemError

def getPrettyName(opt):
    n = opt.name
    return n.replace('_', ' ')

def ChoiceOption(name, description, default=None, choices=[]):
    C = Choice(name, description)
    for c in choices:
        s = String(c)
        s.value = c
        C.add(s)
    if default is not None:
        C.value = default
        C.default = default
    return C

def _valueSetter(opt, value):
    "Sets opt.value to value, returns True if it changed"
    if isinstance(opt, String) and value == '':
        value = opt.default
    if opt.value == value:
        ret = False
    else:
        ret = True
    ovalue = opt.value
    opt.value = value
    #print "_valueSetter: %s %r %r %s"%(opt.name, ovalue, opt.value, ret)
    return ret

def _optParseBuilder(opt, parser):
    args = {}
    if isinstance(opt, Boolean):
        if opt.default is False:
            args['action'] = 'store_true'
        elif opt.default is True:
            args['action'] = 'store_false'
        else:
            raise ValueError("Boolean must default to True or False, not %r"%
                                                                opt._default)
    help = opt.description
    if isinstance(opt, Choice):
        help = help+ ' (%s) (default %s)'%(
                                ', '.join([ str(x.value) for x in opt ]),
                                opt.default)
    args.update({'dest': opt.name,
                 'help': help
               })
    cmdopt = '--' + opt.name.replace('_', '-')
    if hasattr(opt, 'shortopt'):
        shortopt = '-' + opt.shortopt
    else:
        shortopt = ''
    parser.add_option(shortopt, cmdopt, **args)

class AllOptions(object):
    def __init__(self):
        self._groups = []
        self._groupdict = {}
        self._filename = None
        self._cached_options = {}

    def __iter__(self):
        for g in self._groups:
            yield g

    def add(self, group):
        n = group.name
        if n in self._groupdict:
            raise DuplicateOptionError(n)
        # Ick. n^2 behaviour. Oh well, it's only at startup
        for opt in group:
            for g in self:
                gopts = [x.name for x in g]
                if opt.name in gopts:
                    raise DuplicateOptionError(n)
        self._groupdict[n] = group
        self._groups.append(group)
    addGroup = add

    def buildOptParse(self, parser):
        for g in self:
            for o in g:
                _optParseBuilder(o, parser)

    def handleOptParse(self, opts, args):
        for g in self:
            if getattr(g, 'variableNames', None):
                continue
            for o in g:
                val = getattr(opts, o.name)
                if val is not NoDefaultOption and val is not None:
                    o.value = val

    def setOptions(self, opts):
        for group in self:
            if getattr(group, 'variableNames', None):
                # Then don't cache everything, just the group
                setattr(opts, group.name, group)
                continue
            for opt in group:
                key, val = opt.name, opt.value
                if val is not NoDefaultOption and val is not None:
                    setattr(opts, key, val)

    def emitConfigParser(self):
        out = []
        for g in self:
            thisblock = {}
            for o in g:
                if o.value not in (NoDefaultOption, o.default) \
                                        and not getattr(o, 'dynamic', None):
                    thisblock[o.name] = o.value
            if thisblock:
                out.append('[%s]'%g.name)
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

    def loadOptsFile(self, loadData=None):
        from ConfigParser import SafeConfigParser
        if loadData is None:
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
        else:
            cfg = SafeConfigParser()
            cfg.readfp(loadData)
        for g in self:
            gname = g.name
            if cfg.has_section(gname):
                if getattr(g, 'variableNames', None):
                    for name, value in cfg.items(gname):
                        opt = String(name, name)
                        _valueSetter(opt,value)
                        g.add(opt)
                else:
                    for o in g:
                        oname = o.name
                        if cfg.has_option(gname, oname):
                            val= cfg.get(gname, oname)
                            o.value = val

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
                n = o.name
                if dict.get(n) is not None:
                    if dict[n] == '' and o.type == 'Integer':
                        if _valueSetter(o, o.default):
                            modified[n] = o.default
                    elif _valueSetter(o, dict[n]):
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
                    if o.name == option:
                        o.value = value
                        if option in self._cached_options:
                            del self._cached_options[option]
                        if dynamic:
                            o.dynamic = True

    def hasValue(self, option):
        if not self._cached_options.has_key(option):
            for g in self:
                if getattr(g, 'variableNames', None):
                    # Then cache the group object, not the items in it
                    self._cached_options[g.name] = g
                    continue
                for o in g:
                    self._cached_options[o.name] = o
        return option in self._cached_options

    def getValue(self, option, dflt=NoDefaultOption):
        if not self._cached_options.has_key(option):
            for g in self:
                if getattr(g, 'variableNames', None):
                    # Then cache the group object, not the items in it
                    self._cached_options[g.name] = g
                    continue
                for o in g:
                    self._cached_options[o.name] = o
        val = self._cached_options[option]
        if hasattr(val, 'value'):
            val = val.value
        if val is NoDefaultOption:
            val = dflt
        return val

    def optionsStartup(self, version='%prog', args=None):
        import optparse
        parser = optparse.OptionParser(version=version)
        self.buildOptParse(parser)
        (opts, args) = parser.parse_args(args=args)
        if getattr(opts, 'no_config_file'):
            self.setOptsFile(None)
        self.loadOptsFile()
        self.handleOptParse(opts, args)
        self.saveOptsFile()

def findOptionsDir():
    try:
        saveDir = os.path.expanduser('~')
    except:
        saveDir = os.getcwd()
    return saveDir
