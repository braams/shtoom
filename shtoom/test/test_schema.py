


from twisted.trial import unittest

from shtoom.schema import *

class SchemaTests(unittest.TestCase):

    def test_basevalues(self):
        ae = self.assertEquals
        s = SchemaObject(name='foo')
        s.value = 1234
        ae(s.value, 1234)
        s.value = 1236
        ae(s.value, 1236)

    def test_integervalues(self):
        ae = self.assertEquals
        ar = self.assertRaises
        i = Integer(name='bar')
        i.value = 1234
        ae(i.value, 1234)
        i.value = '12'
        ae(i.value, 12)
        i.value = 12.5
        ae(i.value, 12)
        i.value = False
        ae(i.value, 0)
        ar(SchemaValueError, setattr, i, 'value', 'foo')
        ar(SchemaValueError, setattr, i, 'value', object())
        ar(SchemaValueError, setattr, i, 'value', ValueError)
        class _I:
            def __init__(self, val):
                self.val = val
            def __int__(self):
                return self.val
        i.value = _I(12)
        ae(i.value, 12)

    def test_booleanvalues(self):
        ae = self.assertEquals
        ar = self.assertRaises
        b = Boolean(name='bazbool')
        for v in True, 'True', 1, '1', 'yes', 'YES':
            b.value = v
            ae(b.value, True)
        for v in False, 'False', 0, '0', 'no', 'NO':
            b.value = v
            ae(b.value, False)
        ar(SchemaValueError, setattr, b, 'value', object())
        ar(SchemaValueError, setattr, b, 'value', ValueError)

    def test_floatvalues(self):
        ae = self.assertEquals
        ar = self.assertRaises
        f = Float(name='bar')
        f.value = 1234
        ae(f.value, 1234.0)
        f.value = '12'
        ae(f.value, 12.0)
        f.value = 12.5
        ae(f.value, 12.5)
        f.value = False
        ae(f.value, 0.0)
        ae(f.type, 'Float')
        ar(SchemaValueError, setattr, f, 'value', 'foo')
        ar(SchemaValueError, setattr, f, 'value', object())
        ar(SchemaValueError, setattr, f, 'value', ValueError)
        class _F:
            def __init__(self, val):
                self.val = val
            def __float__(self):
                return self.val
        f.value = _F(12.0)
        ae(f.value, 12.0)

    def test_stringvalues(self):
        ae = self.assertEquals
        ar = self.assertRaises
        klasses = String, Password
        for klass in klasses:
            s = klass(name='stringobject')
            # XXX should we let everything through?
            for v in 'foo', u'bar', 15, object(), ValueError:
                s.value = v
                ae(s.value, unicode(v))

    def test_objectlist(self):
        ae = self.assertEquals
        ar = self.assertRaises
        for klass in (List, Choice):
            lobj = klass()
            for val in 'abc', 'def', 'ghi':
                v = String(name='%s_name'%(val,))
                v.value = val
                lobj.add(v)
            ae([ x.value for x in lobj ], ['abc', 'def', 'ghi'])
            lobj.remove('def')
            ae([ x.value for x in lobj ], ['abc', 'ghi'])
            ar(ValueError, lobj.remove, 'def')
            ar(ValueError, lobj.remove, 'abc_name')
            i = Integer('floob')
            i.value = 15
            lobj.add(i)
            ae([ x.value for x in lobj ], ['abc', 'ghi', 15])

    def test_objectchoice(self):
        ae = self.assertEquals
        ar = self.assertRaises
        ch = Choice(name='choicelist')
        for val in 'abc', 'def', 'ghi', 'jkl', 'mno':
            v = String(name='%s_name'%(val,))
            v.value = val
            ch.add(v)
        ae([ x.value for x in ch ], ['abc', 'def', 'ghi', 'jkl', 'mno'])
        ch.value = 'def'
        ae(ch.value, 'def')
        ar(ValueError, setattr, ch, 'value', 'abcde')
        ch.value = 'abc'
        ae(ch.value, 'abc')
        # XXX What happens in this case? Should it go to being unset?
        # ch.remove('abc')

    def test_objectdict(self):
        ae = self.assertEquals
        ar = self.assertRaises
        dobj = Dict()
        for val in 'abc', 'def', 'ghi':
            v = String(name='%s_name'%(val,))
            v.value = val
            dobj.add(v)
        vals = [ x.value for x in dobj ]
        vals.sort()
        ae(vals, ['abc', 'def', 'ghi'])
        dobj.remove('def_name')
        vals = [ x.value for x in dobj ]
        vals.sort()
        ae(vals, ['abc', 'ghi'])
        ar(ValueError, dobj.remove, 'def_name')
        ar(ValueError, dobj.remove, 'abc')
        i = Integer('floob')
        i.value = 15
        dobj.add(i)
        vals = [ x.value for x in dobj ]
        vals.sort()
        # XXX brittle, because heterogenous object sorting is wacky
        ae(vals, [15, 'abc', 'ghi'])
        k = dobj.keys()
        k.sort()
        ae(k, ['abc_name', 'floob', 'ghi_name'])
