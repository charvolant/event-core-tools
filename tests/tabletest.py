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

import os
import unittest

from dwca import TableParameters, Table

DEFAULT_PARAMS = TableParameters(encoding='UTF-8', linesTerminatedBy=os.linesep)

class TableParametersTest(unittest.TestCase):
    def testCreate1(self):
        table = Table('event.csv', DEFAULT_PARAMS)
        self.assertEqual('http://rs.tdwg.org/dwc/terms/Event', table.params.rowType)

    def testMapFields1(self):
        table = Table('event.csv', DEFAULT_PARAMS)
        table.map_fields(True)
        self.assertIsNotNone(table.fields)
        self.assertEqual('http://rs.tdwg.org/dwc/terms/eventID', table.fields[0])
        self.assertEqual('http://rs.tdwg.org/dwc/terms/parentEventID', table.fields[1])
        self.assertEqual('eventType', table.fields[2])
        self.assertEqual('http://rs.tdwg.org/dwc/terms/eventRemarks', table.fields[6])
