import sys
import unittest

sys.path.append("./")
from ramnode import RamNode


class TestRamNode(unittest.TestCase):

    def setUp(self):
        pass

    def test_simple(self):
        self.assertTrue(True)

    def test_invalid_key(self):
        node = RamNode()
        functions = [node.create, node.delete, node.list, node.read]

        for function in functions:
            with self.assertRaises(KeyError):
                self.assertTrue(function('anka/banka'))

    def test_create_and_list(self):

        node = RamNode()
        self.assertEqual('', node.list(''))
        self.assertEqual('', node.list('/'))

        self.assertTrue(node.create('anka'))
        self.assertTrue(node.create('anka2'))

        res = node.list('')
        self.assertTrue(res.find('anka') >= 0)
        self.assertTrue(res.find('anka2') >= 0)

        self.assertTrue(node.create('anka/banka'))
        self.assertTrue('banka' in node.list('anka/'))
        self.assertTrue('banka' in node.list('anka'))

    def test_create_and_delete(self):

        node = RamNode()
        self.assertTrue(node.create('anka'))
        self.assertTrue(node.create('anka/hej'))
        self.assertTrue('hej' in node.list('anka'))
        node.delete('anka/hej')
        self.assertFalse('hej' in node.list('anka'))

    def test_update_and_read(self):

        node = RamNode()
        self.assertTrue(node.create('anka'))
        node.update('anka', 'hej')
        self.assertEqual('hej', node.read('anka'))
        node.update('anka', 'content', 2)
        self.assertEqual('hecontent', node.read('anka'))
        node.update('anka', 'hejtent', 2)
        self.assertEqual('hehejtent', node.read('anka'))

if __name__ == '__main__':
    unittest.main()
