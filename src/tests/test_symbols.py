#!/usr/bin/python

try:
    import unittest
    unittest.TextTestResult
except AttributeError:
    import unittest2 as unittest
    unittest.TextTestResult

import ram.symbols

class SymbolsTestCase(unittest.TestCase):
    """cycling"""

    def test_empty_cycle(self):
        """empty ram.symbols"""
        assert str(ram.symbols()) == ""

    def test_symbols_copy_of(self):
        """symbols copy of"""

        symbols = ram.symbols({'xxx.yyy': {'zzz.www': '_'}})
        assert symbols == {'xxx': {'yyy': {'zzz': {'www': '_'}}}}

        symbols.update({'xxx': {'yyy.zzz': '_'}})
        assert symbols == {'xxx': {'yyy': {'zzz': '_'}}}

        symbols.update({'xxx.www': '_'})
        assert symbols == {'xxx': {'yyy': {'zzz': '_'}, 'www': '_'}}


class StructsTestCase(unittest.TestCase):
    """structs"""

    def setUp(self):
        self.symbols = ram.symbols()
        self.symbols['root']['strings'] = '_'
        self.symbols['root']['present']['sub'] = '_'

    def test_present_sub_get(self):
        """get present subkeys"""

        assert self.symbols['root.present.sub'] == '_'
        assert self.symbols['root']['present']['sub'] == '_'
        assert self.symbols['root', 'present', 'sub'] == '_'
        assert self.symbols['root', 'present']['sub'] == '_'
        assert self.symbols['root']['present', 'sub'] == '_'

    def test_chained_sub_set(self):
        """set contain subkeys"""

        self.symbols['root.contain.sub'] = 'flat'
        assert self.symbols['root.contain.sub'] == 'flat'

        del self.symbols['root.contain.sub']
        assert self.symbols['root.contain.sub'] == ''
        assert self.symbols['root.contain'] == ''

        self.symbols['root']['contain']['sub'] = 'node'
        assert self.symbols['root']['contain']['sub'] == 'node'

        del self.symbols['root']['contain']['sub']
        assert self.symbols['root']['contain']['sub'] == ''
        assert self.symbols['root']['contain'] == ''

        self.symbols['root', 'contain', 'sub'] = 'list'
        assert self.symbols['root', 'contain', 'sub'] == 'list'

        del self.symbols['root', 'contain', 'sub']
        assert self.symbols['root', 'contain', 'sub'] == ''
        assert self.symbols['root', 'contain'] == ''

        self.symbols['root', 'contain']['sub'] = 'lide'
        assert self.symbols['root', 'contain']['sub'] == 'lide'

        del self.symbols['root', 'contain']['sub']
        assert self.symbols['root', 'contain']['sub'] == ''
        assert self.symbols['root', 'contain'] == ''

        self.symbols['root']['contain', 'sub'] = 'nost'
        assert self.symbols['root']['contain', 'sub'] == 'nost'

        del self.symbols['root']['contain', 'sub']
        assert self.symbols['root']['contain', 'sub'] == ''
        assert self.symbols['root']['contain'] == ''

    def test_missing_sub_get(self):
        """get missing subkeys"""

        assert self.symbols['root.missing.sub'] == ''
        assert self.symbols['root']['missing']['sub'] == ''
        assert self.symbols['root', 'missing', 'sub'] == ''
        assert self.symbols['root', 'missing']['sub'] == ''
        assert self.symbols['root']['missing', 'sub'] == ''

    def test_missing_top_get(self):
        """get missing topkeys"""

        assert self.symbols['none.missing.sub'] == ''
        assert self.symbols['none']['missing']['sub'] == ''
        assert self.symbols['none', 'missing', 'sub'] == ''
        assert self.symbols['none', 'missing']['sub'] == ''
        assert self.symbols['none']['missing', 'sub'] == ''


    def test_strings_sub_get(self):
        """get strings subkeys"""

        with self.assertRaises(TypeError):
            self.symbols['root.strings.sub']

        with self.assertRaises(TypeError):
            self.symbols['root']['strings']['sub']

        with self.assertRaises(TypeError):
            self.symbols['root', 'strings', 'sub']

        with self.assertRaises(TypeError):
            self.symbols['root', 'strings']['sub']

        with self.assertRaises(TypeError):
            self.symbols['root']['strings', 'sub']


    def test_strings_sub_set(self):
        """set string subkeys"""

        with self.assertRaises(TypeError):
            self.symbols['root.strings.sub'] = '_'

        with self.assertRaises(TypeError):
            self.symbols['root']['strings']['sub'] = '_'

        with self.assertRaises(TypeError):
            self.symbols['root', 'strings', 'sub'] = '_'

        with self.assertRaises(TypeError):
            self.symbols['root', 'strings']['sub'] = '_'

        with self.assertRaises(TypeError):
            self.symbols['root']['strings', 'sub'] = '_'

        with self.assertRaises(TypeError):
            del self.symbols['root.strings.sub']

        with self.assertRaises(TypeError):
            del self.symbols['root']['strings']['sub']

        with self.assertRaises(TypeError):
            del self.symbols['root', 'strings', 'sub']

        with self.assertRaises(TypeError):
            del self.symbols['root', 'strings']['sub']

        with self.assertRaises(TypeError):
            del self.symbols['root']['strings', 'sub']


    def test_symbols_of_data(self):
        """symbols of data"""

        self.assertIsInstance(self.symbols, dict)
        self.assertIsInstance(self.symbols['root'], dict)
        self.assertIsInstance(self.symbols['root']['present'], dict)
        self.assertIsInstance(self.symbols['root']['present']['sub'], str)
        self.assertIsInstance(self.symbols['root']['missing']['sub'], str)

        assert self.symbols == {'root': {'present': {'sub': '_'}, 'strings': '_'}}
        assert self.symbols['root'] == {'present': {'sub': '_'}, 'strings': '_'}
        assert self.symbols['root']['present'] == {'sub': '_'}
        assert self.symbols['root', 'present'] == {'sub': '_'}
        assert self.symbols['root.present'] == {'sub': '_'}


    def test_chained_sub_key(self):
        """chained sub get"""

        assert sorted(self.symbols) == sorted(('root',))
        assert len(self.symbols) == 1

        assert sorted(self.symbols['root']) == sorted(('present', 'strings'))
        assert len(self.symbols['root']) == 2

        assert sorted(self.symbols['root.present']) == sorted(('sub',))
        assert len(self.symbols['root.present']) == 1

        assert sorted(self.symbols['root.missing']) == sorted(())
        assert len(self.symbols['root.missing']) == 0

        self.symbols['root.chained'] = ''

        assert sorted(self.symbols) == sorted(('root',))
        assert len(self.symbols) == 1

        assert sorted(self.symbols['root']) == sorted(('present', 'strings'))
        assert len(self.symbols['root']) == 2

        assert sorted(self.symbols['root.chained']) == sorted(())
        assert len(self.symbols['root.chained']) == 0

        self.symbols['root.chained.sub'] = '_'
        del self.symbols['root.chained']

        assert sorted(self.symbols) == sorted(('root',))
        assert len(self.symbols) == 1

        assert sorted(self.symbols['root']) == sorted(('present', 'strings'))
        assert len(self.symbols['root']) == 2

        assert sorted(self.symbols['root.chained']) == sorted(())
        assert len(self.symbols['root.chained']) == 0

        self.symbols['root.chained.sub'] = '_'
        self.symbols['root.chained.top'] = '_'

        del self.symbols['root.chained.sub']

        assert sorted(self.symbols) == sorted(('root',))
        assert len(self.symbols) == 1

        assert sorted(self.symbols['root']) == sorted(('present', 'strings', 'chained'))
        assert len(self.symbols['root']) == 3

        assert sorted(self.symbols['root.chained']) == sorted(('top',))
        assert len(self.symbols['root.chained']) == 1

        del self.symbols['root.chained.top']

        assert sorted(self.symbols) == sorted(('root',))
        assert len(self.symbols) == 1

        assert sorted(self.symbols['root']) == sorted(('present', 'strings'))
        assert len(self.symbols['root']) == 2

        assert sorted(self.symbols['root.chained']) == sorted(())
        assert len(self.symbols['root.chained']) == 0

        self.symbols['root.chained.sub'] = '_'
        self.symbols['root.chained.top'] = '_'
        self.symbols['root.chained'] = None

        assert sorted(self.symbols) == sorted(('root',))
        assert len(self.symbols) == 1

        assert sorted(self.symbols['root']) == sorted(('present', 'strings'))
        assert len(self.symbols['root']) == 2

        assert sorted(self.symbols['root.chained']) == sorted(())
        assert len(self.symbols['root.chained']) == 0


    def test_contain_sub_key(self):
        """contain sub key"""

        self.assertIn('root', self.symbols)
        self.assertNotIn('none', self.symbols)

        self.assertIn('root.present', self.symbols)
        self.assertNotIn('root.missing', self.symbols)

        self.assertIn('root.present.sub', self.symbols)
        self.assertNotIn('root.missing.sub', self.symbols)
        self.assertNotIn('root.present.top', self.symbols)

        self.assertIn(('root', 'present', 'sub'), self.symbols)
        self.assertNotIn(('root', 'missing', 'sub'), self.symbols)
        self.assertNotIn(('root', 'present', 'top'), self.symbols)

        self.assertIn('present', self.symbols['root'])
        self.assertIn('present.sub', self.symbols['root'])
        self.assertIn(('present','sub'), self.symbols['root'])
        self.assertNotIn('missing', self.symbols['root'])
        self.assertNotIn('missing.sub', self.symbols['root'])
        self.assertNotIn(('missing', 'sub'), self.symbols['root'])
        self.assertNotIn('present.top', self.symbols['root'])
        self.assertNotIn(('present', 'top'), self.symbols['root'])

        self.assertIn('sub', self.symbols['root.present'])
        self.assertIn('sub', self.symbols['root']['present'])
        self.assertIn('sub', self.symbols['root', 'present'])
        self.assertNotIn('sub', self.symbols['root.missing'])
        self.assertNotIn('sub', self.symbols['root']['missing'])
        self.assertNotIn('sub', self.symbols['root', 'missing'])
        self.assertNotIn('top', self.symbols['root.present'])
        self.assertNotIn('top', self.symbols['root']['present'])
        self.assertNotIn('top', self.symbols['root', 'present'])

        self.assertNotIn('strings.sub', self.symbols['root'])
        self.assertNotIn(('strings', 'sub'), self.symbols['root'])

        self.assertNotIn('sub.top', self.symbols['root.present'])
        self.assertNotIn(('sub','top'), self.symbols['root.present'])
        self.assertNotIn('sub.top', self.symbols['root']['present'])
        self.assertNotIn(('sub','top'), self.symbols['root']['present'])
        self.assertNotIn('sub.top', self.symbols['root', 'present'])
        self.assertNotIn(('sub','top'), self.symbols['root', 'present'])


    def test_symbols_key_str(self):
        """symbols key str"""

        with self.assertRaises(TypeError):
            self.symbols[None]

        with self.assertRaises(TypeError):
            self.symbols['root', None]

        with self.assertRaises(TypeError):
            self.symbols['root'][None]

        with self.assertRaises(TypeError):
            self.symbols['']

        with self.assertRaises(TypeError):
            self.symbols['root.']

        with self.assertRaises(TypeError):
            self.symbols['root', 'missing.']

        with self.assertRaises(TypeError):
            self.symbols['root']['missing.']

        with self.assertRaises(TypeError):
            self.symbols['root', 'missing', '']

        with self.assertRaises(TypeError):
            self.symbols['root']['missing']['']

        assert self.symbols['root']['my-keys'] == ''
        assert self.symbols['root']['my_keys'] == ''

        assert self.symbols['root', 'my-keys'] == ''
        assert self.symbols['root', 'my_keys'] == ''


if __name__ == '__main__':
    unittest.main()
