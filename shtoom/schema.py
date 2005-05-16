import warnings

class DuplicateItemError(Exception):
    pass

class _BackwardsCompatMixin:
    def _getOptionType(self):
        warnings.warn("object.optionValue", DeprecationWarning, stacklevel=2)
        t = self.type
        return {'Integer':'Number'}.get(t, t)
    optionType = property(_getOptionType)

    def getDescription(self):
        warnings.warn("object.getDescription()", DeprecationWarning,
                                                        stacklevel=2)
        return self.description

    def getValue(self):
        warnings.warn("object.getValue()", DeprecationWarning, stacklevel=2)
        return self.value

    def getName(self):
        warnings.warn("object.getName()", DeprecationWarning, stacklevel=2)
        return self.name

    def getPrettyName(self):
        warnings.warn("object.getPrettyName()", DeprecationWarning, stacklevel=2)
        return self.name.replace('_', ' ')


class SchemaError(Exception):
    pass

class SchemaValueError(SchemaError):
    pass

# construct a singleton marker
class _NoDefaultValue(object):
    "Marker indicating no default value was specified"
    def _getValue(self):
        return self
    value = property(_getValue)

NoDefaultValue = _NoDefaultValue()
del _NoDefaultValue

class SchemaObject(_BackwardsCompatMixin, object):
    "Base class for all schema objects"
    _value = NoDefaultValue
    _requiredType = None

    def __init__(self, name='', description='', default=NoDefaultValue,
                 shortName='', help='', **kwargs):
        self.name = name
        self.description = description
        self.default = default
        if default is not NoDefaultValue:
            self.value = default
        self.shortName = shortName
        self.help = help
        self.type = self.__class__.__name__
        # Allow additional values, e.g. shortopt
        self.__dict__.update(kwargs)

    def _getValue(self):
        return self._value

    def _setValue(self, value):
        value = self._coerceValue(value)
        self._validateValue(value)
        self._value = value
        return value

    value = property(_getValue, _setValue)

    def _coerceValue(self, value):
        # XXX try adaption
        if value is NoDefaultValue:
            return value

        if not self._requiredType:
            return value
        try:
            value = self._requiredType(value)
        except (ValueError,TypeError):
            raise SchemaValueError('expected %s, got %r'%
                                        (self._requiredType, value))
        return value

    def _validateValue(self, value):
        if value is NoDefaultValue:
            return
        if self._requiredType and not isinstance(value, self._requiredType):
            raise SchemaValueError('expected %s, got %r'%(
                                                self._requiredType, value))
    def __repr__(self):
        return "<%s object '%s' at %x>"%(self.__class__.__name__, self.name, id(self))

class Integer(SchemaObject):
    "An integer"
    _requiredType = int

class Float(SchemaObject):
    "A float"
    _requiredType = float

class String(SchemaObject):
    "A string"
    _requiredType = unicode

class Password(String):
    "A password is a string that is handled 'differently' for display &c"

class Label(SchemaObject):
    "A label is a schema object that has no value, but is for display only"
    def _validateValue(self, value):
        raise SchemaValueError('Labels cannot have a value')

class Boolean(SchemaObject):
    "A boolean"

    def _coerceValue(self, value):
        # XXX try adaption

        # bool(obj) does true/false testing of obj - not what I want,
        # as it will too easily conceal errors - e.g. bool('Fasle') is True
        if isinstance(value, basestring):
            # How do I init gettext from trial?!
            if value.lower() in ('false', 'no', '0'): #, _('no'), _('false')
                return False
            elif value.lower() in ('true', 'yes', '1'): #, _('yes'), _('true')
                return True
            else:
                raise SchemaValueError('expected bool, got %r'%(value))
        elif value in ( 0, 1, True, False ):
            return bool(value)
        else:
            raise SchemaValueError('expected bool, got %r'%(value))


class ObjectGroup(object):
    "base class for all object containers"

    def __init__(self, name='', description='', help='', **kwargs):
        self.name = name
        self.description = description
        self.help = help
        self.type = self.__class__.__name__
        self.__dict__.update(kwargs)

    def _setValue(self, value):
        raise TypeError('%s is valueless'%(self.type))

    def _getValue(self):
        raise TypeError('%s is valueless'%(self.type))
    value = property(_getValue, _setValue)

    def add(self, other):
        if not isinstance(other, (SchemaObject, Choice)):
            raise TypeError("expected SchemaObject, not %r"%(other))
        self._addObject(other)

    def addOption(self, other):
        warnings.warn("object.addOption()", DeprecationWarning, stacklevel=2)
        self.add(other)

    def _addObject(self, other):
        raise NotImplementedError

    def remove(self, other):
        if hasattr(self, '_removeObjectByName'):
            if isinstance(other, (SchemaObject, Choice)):
                name = other.name
            elif isinstance(other, basestring):
                name = other
            else:
                raise TypeError("expected object or object name, not %r"%(other))
            self._removeObjectByName(name)
        elif hasattr(self, '_removeObjectByValue'):
            if isinstance(other, (SchemaObject, Choice)):
                value = other.value
            elif isinstance(other, basestring):
                value = other
            else:
                raise TypeError("expected object or object value, not %r"%(other))
            self._removeObjectByValue(value)

    def getGUI(self):
        warnings.warn("object.getGUI()", DeprecationWarning, stacklevel=2)
        return getattr(self, 'gui', True)

class List(_BackwardsCompatMixin, ObjectGroup):
    "A list of objects"
    def __init__(self, *args, **kwargs):
        self._subobjects = []
        self._objectNames = {}
        ObjectGroup.__init__(self, *args, **kwargs)

    def _addObject(self, object):
        if object.name in self._objectNames:
            raise DuplicateItemError(object)
        self._subobjects.append(object)
        self._objectNames[object.name] = True

    def _removeObjectByValue(self, value):
        # Completely non-optimal (O(2N)), but not a time-critical function
        for sub in self._subobjects:
            if sub.value == value:
                self._subobjects.remove(sub)
                break
        else:
            raise ValueError('%s not known'%(value,))

    def __iter__(self):
        return iter(self._subobjects)

class Choice(List):
    "A choice from one of the objects in the container"
    _value = NoDefaultValue
    default = NoDefaultValue

    def _setValue(self, value):
        for sub in self._subobjects:
            if value == sub.value:
                self._value = sub
                break
        else:
            vals = ', '.join([x.value for x in self])
            raise ValueError('%s is not a known value for %s (should be one of %s)'%(value, self.name, vals))

    def _getValue(self):
        return self._value.value

    value = property(_getValue, _setValue)

    def getChoices(self):
        warnings.warn("Choice.getChoices", DeprecationWarning, stacklevel=2)
        return [ x.value for x in self ]

class Dict(_BackwardsCompatMixin, ObjectGroup):
    "A dictionary of objects"
    variableNames = True

    def __init__(self, *args, **kwargs):
        self._subobjects = {}
        ObjectGroup.__init__(self, *args, **kwargs)

    def _addObject(self, object):
        self._subobjects[object.name] = object

    def _removeObjectByName(self, name):
        if name in self._subobjects:
            del self._subobjects[name]
        else:
            raise ValueError('%s not known'%(name,))

    def __iter__(self):
        return iter(self._subobjects.values())

    def keys(self):
        return self._subobjects.keys()
    def items(self):
        return self._subobjects.items()
    def values(self):
        return self._subobjects.values()


class OrderedDict(Dict):
    "An (ordered) dictionary of objects"
