# Event Core Tools

A collection of tools for assembling darwin core archives
that meet the expectations of the *ALA Extended Data Producers’ Guide*

This is a minimal collection of tools intended for people who wish to
build Darwin Core Archives from pre-existing files and supplements the
information in the Guide.
If you have a more complex project or something that you want
to be repeatable, have a look at the 
[preingestion framework](https://github.com/AtlasOfLivingAustralia/preingestion)

## Installation

You will need, already installed on your system:

* [python](https://www.python.org/) version 3.8 or above. The scripts should work with the standard python install.
* A downloaded copy of this project

## Use

Use `python dwca.py -h` for information on usage, options, etc.

### DwCA construction

`python dwca.py [options] files ...`

This will create a DwCA in a directory (by default, dwca in the current directory)
that contains all the listed files.
The script will attempt to work out what fields are in the files,
how things link together, the type of object in the file, etc.
using the file names and the fields in each file as a guide.
It will generate a `meta.xml` and a skeleton `eml.xml` for the resulting
DwCA.

The input files will need to have a header row containing the
field names.