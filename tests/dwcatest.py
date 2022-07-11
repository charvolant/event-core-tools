#  Copyright (c) 2022. Atlas of Living Australia.
#  All Rights Reserved.
#
#  The contents of this file are subject to the Mozilla Public
#  License Version 1.1 (the "License"); you may not use this file
#  except in compliance with the License. You may obtain a copy of
#  the License at http://www.mozilla.org/MPL/
#
#  Software distributed under the License is distributed on an "AS  IS" basis,
#  WITHOUT WARRANTY OF ANY KIND, either express or
#  implied. See the License for the specific language governing
#  rights and limitations under the License.

import shutil
import unittest
import tempfile
import os

from dwca import TableParameters, Table, DwCA

DEFAULT_PARAMS = TableParameters(encoding='UTF-8', linesTerminatedBy='\n')

class DwCATest(unittest.TestCase):
    def testCreate1(self):
        table1 = Table('event.csv', DEFAULT_PARAMS)
        dwca = DwCA(table1)
        self.assertIs(table1, dwca.core)
        self.assertIsNotNone(dwca.extensions)
        self.assertEqual(0, len(dwca.extensions))

    def testCreate2(self):
        table1 = Table('event.csv', DEFAULT_PARAMS)
        table2 = Table('occurrence.csv', DEFAULT_PARAMS)
        dwca = DwCA(table1, table2)
        self.assertIs(table1, dwca.core)
        self.assertIsNotNone(dwca.extensions)
        self.assertEqual(1, len(dwca.extensions))
        self.assertIs(table2, dwca.extensions[0])

    def testFindIndexField1(self):
        table1 = Table('event.csv', DEFAULT_PARAMS)
        table1.map_fields(True)
        dwca = DwCA(table1)
        index = dwca.find_index_field()
        self.assertEqual('http://rs.tdwg.org/dwc/terms/eventID', index)

    def testFindIndexField2(self):
        table1 = Table('event.csv', DEFAULT_PARAMS)
        table2 = Table('occurrence.csv', DEFAULT_PARAMS)
        table1.map_fields(True)
        table2.map_fields(False)
        dwca = DwCA(table1, table2)
        index = dwca.find_index_field()
        self.assertEqual('http://rs.tdwg.org/dwc/terms/eventID', index)

    def testWrite1(self):
        table1 = Table('event.csv', DEFAULT_PARAMS)
        dwca = DwCA(table1)
        temp = tempfile.mkdtemp()
        dwca.write(temp)
        self.assertTrue(os.path.exists(os.path.join(temp, 'event.csv')))
        self.assertTrue(os.path.exists(os.path.join(temp, 'meta.xml')))
        self.assertTrue(os.path.exists(os.path.join(temp, 'eml.xml')))
        shutil.rmtree(temp)


    def testWrite2(self):
        table1 = Table('event.csv', DEFAULT_PARAMS)
        table2 = Table('occurrence.csv', DEFAULT_PARAMS)
        dwca = DwCA(table1, table2)
        temp = tempfile.mkdtemp()
        dwca.write(temp)
        self.assertTrue(os.path.exists(os.path.join(temp, 'event.csv')))
        self.assertTrue(os.path.exists(os.path.join(temp, 'occurrence.csv')))
        self.assertTrue(os.path.exists(os.path.join(temp, 'meta.xml')))
        self.assertTrue(os.path.exists(os.path.join(temp, 'eml.xml')))
        shutil.rmtree(temp)
