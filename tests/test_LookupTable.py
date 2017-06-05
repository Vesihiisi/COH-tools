#!/usr/bin/python
# -*- coding: utf-8  -*-
import unittest
import importer.LookupTable as Lt


class TestTableConverter(unittest.TestCase):

    def setUp(self):
        self.converter = Lt.LookupTable("test")
        self.wikipage = ('lorem ipsum\n'
                         '{| class="wikitable sortable"\n! Name\n! Count\n'
                         '! Item(s)\n! Notes\n|-\n'
                         '| kloster\n|\n| {{Q|Q44613}}\n|\n|-\n'
                         '| pestsäule\n|31\n| {{Q|Q1549521}}\n| \n|}')

    def test_wikipage_to_table(self):
        output = ('{| class="wikitable sortable"\n! Name\n! Count\n'
                  '! Item(s)\n! Notes\n|-\n'
                  '| kloster\n|\n| {{Q|Q44613}}\n|\n|-\n'
                  '| pestsäule\n|31\n| {{Q|Q1549521}}\n| \n|}')
        self.assertEqual(
            self.converter.extract_table_from_page(self.wikipage), output)

    def test_table_to_json(self):
        wikitable = self.converter.extract_table_from_page(self.wikipage)
        output = {'Kloster': {'items': ['Q44613'], 'count': ''}, 'Pestsäule': {
            'items': ['Q1549521'], 'count': '31'}}
        parsed = self.converter.table_to_json(wikitable)
        self.assertEqual(parsed, output)


if __name__ == '__main__':
    unittest.main()
