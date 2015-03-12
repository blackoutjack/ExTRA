import sys
import os
import subprocess
from subprocess import PIPE
from optparse import OptionParser
import tempfile

#
# This file contains various values (mostly paths)
# that can be imported into other Python scripts.
#

JAMPKG = os.getenv('JAMPKG')
JAMSCRIPT_DIR = os.path.join(JAMPKG, 'jamscript')
TESTS_DIR = os.path.join(JAMPKG, 'tests')

OUTDIR = os.path.join(JAMPKG,'output')
UTILDIR = os.path.join(JAMPKG, 'util')
UNPACKDIR = os.path.join(JAMPKG, 'unpacked')
ExTRADIR = os.path.join(UTILDIR, 'ExTRA')
UNPACK_SCRIPT = os.path.join(ExTRADIR, 'unpack.py')
REPACK_SCRIPT = os.path.join(ExTRADIR, 'repack.py')

JSLIBDIR = os.path.join(JAMSCRIPT_DIR, 'txjs')
JAMSCRIPT_LIB = os.path.join(JSLIBDIR, 'libTx.js')

# Configure files that are symlinked in woven test case directories. 
SYMLINK_FILES = [
  (JAMSCRIPT_LIB, None),
  (os.path.join(TESTS_DIR, 'test.php'), None),
  (os.path.join(TESTS_DIR, 'testindex.php'), 'index.php'),
  (os.path.join(TESTS_DIR, 'auto.js'), None),
]

