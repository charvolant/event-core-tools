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

import argparse
import logging
import os

from dwca import TableParameters, Table, DwCA

CSV_PARAMS = TableParameters(fieldsTerminatedBy=',', linesTerminatedBy=os.linesep, fieldsEnclosedBy='"', ignoreHeaderLines=1)
TSV_PARAMS = TableParameters(fieldsTerminatedBy='\t', linesTerminatedBy=os.linesep, fieldsEnclosedBy='"', ignoreHeaderLines=1)

logger = logging.getLogger("dwca")
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

parser = argparse.ArgumentParser(description='Convert a collection of CSV/TSV files into a Darwin Core Archive')
parser.add_argument('-o', '--output', type=str, help='Directory that contains the resulting DwCA', default='./dwca')
parser.add_argument('--encoding', type=str, help='The default file encoding', default='UTF-8')
parser.add_argument('--title', type=str, help='The metadata title')
parser.add_argument('--creator', type=str, help='The metadata creator')
parser.add_argument('-t', '--tabs', help='Expect tab separation by default', action='store_true')
parser.add_argument('files', type=str, metavar='FILE', nargs='+', help='The list of source files (core file first)')
parser.add_argument('-v', '--verbose', help='Verbose information', action='store_true')
args = parser.parse_args()

output_dir = args.output
defaultParameters = TableParameters(
    encoding=args.encoding,
    fieldsTerminatedBy='\t' if args.tabs else ',',
    linesTerminatedBy=os.linesep,
    fieldsEnclosedBy='"',
    ignoreHeaderLines=1
)
if args.verbose:
    logger.setLevel(logging.DEBUG)

logger.debug(f"Default parameters {defaultParameters}")
tables = [Table(f, defaultParameters) for f in args.files]
dwca = DwCA(*tables)
if args.title is not None:
    dwca.metadata['title'] = args.title
if args.creator is not None:
    dwca.metadata['creator'] = args.creator
logger.debug(f"Writing to {output_dir}")
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)
dwca.write(output_dir)
