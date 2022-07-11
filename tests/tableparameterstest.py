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

from dwca import TableParameters

DEFAULT_PARAMS = TableParameters(encoding='UTF-8', linesTerminatedBy=os.linesep)

class TableParametersTest(unittest.TestCase):
    def testMerge1(self):
        one = TableParameters(encoding='UTF-8', fieldsTerminatedBy=',', fieldsEnclosedBy='|')
        two = TableParameters(rowType='http://rs.tdwg.org/dwc/terms/Event', linesTerminatedBy='\n', ignoreHeaderLines=5)
        merged = one.merge(two)
        self.assertEqual('http://rs.tdwg.org/dwc/terms/Event', merged.rowType)
        self.assertEqual('UTF-8', merged.encoding)
        self.assertEqual(',', merged.fieldsTerminatedBy)
        self.assertEqual('\n', merged.linesTerminatedBy)
        self.assertEqual('|', merged.fieldsEnclosedBy)
        self.assertEqual(5, merged.ignoreHeaderLines)

    def testMerge2(self):
        one = TableParameters(rowType='http://rs.tdwg.org/dwc/terms/Occurrence', encoding='UTF-8', fieldsTerminatedBy=',', fieldsEnclosedBy='|', linesTerminatedBy='\r\n')
        two = TableParameters(rowType='http://rs.tdwg.org/dwc/terms/Event', encoding='ASCII', fieldsTerminatedBy='|', linesTerminatedBy='\n', fieldsEnclosedBy='"', ignoreHeaderLines=5)
        merged = one.merge(two)
        self.assertEqual('http://rs.tdwg.org/dwc/terms/Occurrence', merged.rowType)
        self.assertEqual('UTF-8', merged.encoding)
        self.assertEqual(',', merged.fieldsTerminatedBy)
        self.assertEqual('\r\n', merged.linesTerminatedBy)
        self.assertEqual('|', merged.fieldsEnclosedBy)
        self.assertEqual(5, merged.ignoreHeaderLines)

    def testMerge3(self):
        one = TableParameters(rowType='http://rs.tdwg.org/dwc/terms/Occurrence', encoding='UTF-8', fieldsTerminatedBy=',', fieldsEnclosedBy='|', linesTerminatedBy='\r\n')
        two = TableParameters(rowType='http://rs.tdwg.org/dwc/terms/Event', encoding='ASCII', fieldsTerminatedBy='|', linesTerminatedBy='\n', fieldsEnclosedBy='"', ignoreHeaderLines=5)
        merged = two.merge(one)
        self.assertEqual('http://rs.tdwg.org/dwc/terms/Event', merged.rowType)
        self.assertEqual('ASCII', merged.encoding)
        self.assertEqual('|', merged.fieldsTerminatedBy)
        self.assertEqual('\n', merged.linesTerminatedBy)
        self.assertEqual('"', merged.fieldsEnclosedBy)
        self.assertEqual(5, merged.ignoreHeaderLines)

    def testFromFile1(self):
        params = TableParameters.from_filename('event.csv', DEFAULT_PARAMS)
        self.assertEqual('http://rs.tdwg.org/dwc/terms/Event', params.rowType)
        self.assertEqual('UTF-8', params.encoding)
        self.assertEqual(',', params.fieldsTerminatedBy)
        self.assertEqual('\n', params.linesTerminatedBy)
        self.assertEqual('"', params.fieldsEnclosedBy)
        self.assertEqual(1, params.ignoreHeaderLines)

    def testFromFile2(self):
        params = TableParameters.from_filename('measurements.txt', DEFAULT_PARAMS)
        self.assertEqual('http://rs.tdwg.org/dwc/terms/MeasurementOrFact', params.rowType)
        self.assertEqual('UTF-8', params.encoding)
        self.assertEqual('\t', params.fieldsTerminatedBy)
        self.assertEqual('\n', params.linesTerminatedBy)
        self.assertEqual('"', params.fieldsEnclosedBy)
        self.assertEqual(1, params.ignoreHeaderLines)
