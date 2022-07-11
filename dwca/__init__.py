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

import csv
import datetime
import importlib.resources
import os
import re
import shutil
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger("dwca")

"""Lookup table mapping a column header onto a term. Loaded from terms.csv"""
_TERMS: Dict[str, str] = dict()

with importlib.resources.open_text(__package__, 'terms.csv') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        _TERMS[row[0]] = row[1]

def _normalise_csv(value: str) -> str:
    if value is None:
        return None
    value = value.strip()
    if len(value) == 0:
        return None
    value = value.replace('\\t', '\t')
    value = value.replace('\\n', '\n')
    value = value.replace('\\r', '\r')
    return value

def _attr_translate(value):
    """
    Translate escapes for common DwCA delimiters, replacing tabs and newlines by escapes.

    :param value: The input string
    :return:
    """
    if value is None:
        return None
    value = str(value)
    value = value.replace('\t', '\\t')
    value = value.replace('\n', '\\n')
    value = value.replace('\r', '\\r')
    value = value.replace('"', '&quot;')
    return value

class TableParameters:
    pass

"""Lookup table mapping a file name pattern onto a set of table parameters. Loaded from files.csv"""
_FILES: List[Tuple[re.Pattern, TableParameters]] = list()

class TableParameters:
    def __init__(self, rowType = None, encoding = None, fieldsTerminatedBy = None, linesTerminatedBy = None, fieldsEnclosedBy = None, ignoreHeaderLines = None):
        self.rowType = rowType
        self.encoding = encoding
        self.fieldsTerminatedBy = fieldsTerminatedBy
        self.linesTerminatedBy = linesTerminatedBy
        self.fieldsEnclosedBy = fieldsEnclosedBy
        self.ignoreHeaderLines = int(ignoreHeaderLines) if ignoreHeaderLines is not None else None

    def merge(self, other: TableParameters):
        return TableParameters(
            self.rowType if self.rowType is not None else other.rowType,
            self.encoding if self.encoding is not None else other.encoding,
            self.fieldsTerminatedBy if self.fieldsTerminatedBy is not None else other.fieldsTerminatedBy,
            self.linesTerminatedBy if self.linesTerminatedBy is not None else other.linesTerminatedBy,
            self.fieldsEnclosedBy if self.fieldsEnclosedBy is not None else other.fieldsEnclosedBy,
            self.ignoreHeaderLines if self.ignoreHeaderLines is not None else other.ignoreHeaderLines
        )

    def csv_reader(self, file):
        return csv.reader(file, delimiter=self.fieldsTerminatedBy, lineterminator=self.linesTerminatedBy, quotechar=self.fieldsEnclosedBy, doublequote=True)

    def __str__(self):
        return f"TableParameters(rowType={self.rowType}, encoding={self.encoding}, fieldsTerminatedBy={_attr_translate(self.fieldsTerminatedBy)}, linesTerminatedBy={_attr_translate(self.linesTerminatedBy)}, fieldsEnclosedBy={_attr_translate(self.fieldsEnclosedBy)}, ignoreHeaderLines={self.ignoreHeaderLines})"

    @classmethod
    def from_filename(cls, filename: str, defaults: TableParameters):
        parameters = defaults
        for pattern in _FILES:
            if pattern[0].fullmatch(filename):
                parameters = pattern[1].merge(parameters)
        logger.debug(f"Parameters for {filename} are {parameters}")
        return parameters

with importlib.resources.open_text(__package__, 'files.csv') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        _FILES.append((
            re.compile(row[0]),
            TableParameters(
                _normalise_csv(row[1]),
                _normalise_csv(row[2]),
                _normalise_csv(row[3]),
                _normalise_csv(row[4]),
                _normalise_csv(row[5]),
                _normalise_csv(row[6])
            )
        ))

class Table:
    def __init__(self, path: str, defaultParams: TableParameters):
        self.path = path;
        self.filename = os.path.basename(path)
        self.params = TableParameters.from_filename(self.filename, defaultParams)

    def map_fields(self, core: bool):
        with open(self.path) as csvfile:
            reader = self.params.csv_reader(csvfile)
            row = next(reader)
            self.fields = [_TERMS.get(f, f) for f in row]
        logger.debug(f"Mapped fields for {self.filename} to {self.fields}")


class DwCA:
    def __init__(self, core: Table, *extensions):
        self.core = core
        self.extensions = extensions
        self.metadata = dict()

    def write(self, destpath: str):
        self.core.map_fields(True)
        for ext in self.extensions:
            ext.map_fields(False)
        self.index = self.find_index_field()
        logger.debug(f"Index field is {self.index}")
        self.write_table(self.core, destpath)
        for ext in self.extensions:
            self.write_table(ext, destpath)
        self.write_meta(destpath)
        self.write_eml(destpath)

    def find_index_field(self):
        fields = set(self.core.fields)
        for ext in self.extensions:
            fields = fields.intersection(set(ext.fields))
        if len(fields) == 0:
            return None
        logger.debug(f"Potential index fields: {fields}")
        for field in self.core.fields:
            if field in fields:
                return field
        return None

    def write_table(self, table: Table, destpath: str):
        destpath = os.path.join(destpath, table.filename)
        if table.path != destpath:
            logger.debug(f"Copying {table.filename} to {destpath}")
            shutil.copy(table.path, destpath)

    def write_meta(self, destpath: str):
        destpath = os.path.join(destpath, "meta.xml")
        logger.debug(f"Writing metafile {destpath}")
        with open(destpath, "w") as meta:
            meta.write('<archive xmlns="http://rs.tdwg.org/dwc/text/" metadata="eml.xml">\n')
            meta.write('  <!-- Generated on {timestamp} -->\n'.format(timestamp=str(datetime.datetime.now())))
            self.write_table_meta(self.core, meta, True)
            for ext in self.extensions:
                self.write_table_meta(ext, meta, False)
            meta.write('</archive>')

    def write_table_meta(self, table: Table, meta, core: bool):
        element = 'core' if core else 'extension'
        idelement = 'id' if core else 'coreid'
        idindex = table.fields.index(self.index) if self.index is not None else None
        logger.debug(f"Writing {element} meta description for {table.filename}")
        meta.write('  <{element} rowType="{rowType}" encoding="{encoding}" fieldsTerminatedBy="{fieldsTerminatedBy}" linesTerminatedBy="{linesTerminatedBy}" fieldsEnclosedBy="{fieldsEnclosedBy}" ignoreHeaderLines="{ignoreHeaderLines}">\n'.format(
            element=element,
            rowType=table.params.rowType,
            encoding=table.params.encoding,
            fieldsTerminatedBy=_attr_translate(table.params.fieldsTerminatedBy),
            linesTerminatedBy=_attr_translate(table.params.linesTerminatedBy),
            fieldsEnclosedBy=_attr_translate(table.params.fieldsEnclosedBy),
            ignoreHeaderLines=table.params.ignoreHeaderLines
        ))
        meta.write('    <files>\n')
        meta.write('      <location>{filename}</location>\n'.format(filename=table.filename))
        meta.write('    </files>\n')
        if idindex is not None:
            meta.write('    <{idelement} index="{idindex}"/>\n'.format(idelement=idelement, idindex=idindex))
        pos = 0
        for field in table.fields:
            meta.write('    <field index="{index}" term="{field}"/>\n'.format(index=pos, field=field))
            pos += 1
        meta.write('  </{element}>\n'.format(element=element))

    def write_eml(self, destpath: str):
        destpath = os.path.join(destpath, "eml.xml")
        logger.debug(f"Writing metadata {destpath}")
        with open(destpath, "w") as eml:
            title = self.metadata.get('title', 'Title goes here')
            creator = self.metadata.get('creator', 'Creator name')
            pubdate = datetime.date.today().isoformat()
            timestamp = datetime.datetime.now().isoformat()
            data = """
<?xml version="1.0" encoding="utf-8"?>
<eml:eml xmlns:d="eml://ecoinformatics.org/dataset-2.1.0" xmlns:eml="eml://ecoinformatics.org/eml-2.1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:dc="http://purl.org/dc/terms/" xsi:schemaLocation="eml://ecoinformatics.org/eml-2.1.1 http://rs.gbif.org/schema/eml-gbif-profile/1.1/eml-gbif-profile.xsd" system="ALA-Registry" scope="system" xml:lang="en">
  <dataset>
    <title xmlns:lang="en">{title}</title>
    <creator>
      <organizationName>{creator}</organizationName>
    </creator>
    <pubDate>{pubdate}</pubDate>
    <abstract>
      <para>Abstract</para>
    </abstract>
  </dataset>
  <additionalMetadata>
    <metadata>
      <gbif>
        <dateStamp>{timestamp}</dateStamp>
        <hierarchyLevel>dataset</hierarchyLevel>
      </gbif>
    </metadata>
  </additionalMetadata>
</eml:eml>            
            """.format(title=title, creator=creator, pubdate=pubdate, timestamp=timestamp)
            eml.write(data)
