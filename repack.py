#!/usr/bin/python
# 
# This script is somewhat the inverse of unpack.py. It reinserts scripts
# and other resources into a previously unpacked HTML file.
# Reintegration is based on a specification file (corresponding to the
# "scripts.txt" file generated by unpack.py).
#
import sys
MAJOR = sys.version_info[0]

try:
  import bs4
except ImportError as e:
  if MAJOR == 3: aptget = "apt-get install python3-bs4"
  else: aptget = "apt-get install python-bs4"
  fatal("Unable to import BeautifulSoup 4: %s.\nFor Ubuntu, use ``%s''" % (str(e), aptget))

import os
import re
import shutil
import time
import imp
from optparse import OptionParser

from config import *
from util import fatal
from util import err
from util import warn
from util import out
from util import symlink

# Reinsert scripts into the stripped HTML file.
def repack(htmlfile, jslist, jsdir=None, policy=None):
  htmlfl = open(htmlfile, 'r')
  htmltext = htmlfl.read()
  htmlfl.close()
  soup = bs4.BeautifulSoup(htmltext)

  listfl = open(jslist, 'r')
  jsitems =listfl.readlines()
  listfl.close()
  # Get the directory that the paths are relative to.
  if jsdir is None:
    jsdir = os.path.dirname(jslist)

  for jsitem in jsitems:
    jsitem = jsitem.strip()
    if jsitem == '':
      continue
    if jsitem.startswith('#'):
      continue
    jsparts = jsitem.split(':')
    if len(jsparts) != 3:
      err('Invalid script specification: %s' % jsitem)
      continue
    
    jstype, jsid, jspath = jsparts
    jspath = os.path.join(jsdir, jspath)

    jsfl = open(jspath, 'r')
    jstext = jsfl.read()
    jsfl.close()

    elt = soup.find(id=jsid)
    if elt is None:
      err('No element found with id: %s' % jsid)
      continue

    if VERBOSE:
      out('Repacking %s, element: %s, id: %s' % (jstype, elt.name, jsid))

    if jstype == 'script.src':
      elt.string = '<![CDATA[\n' + jstext + '\n]]>'
    elif jstype == 'script.inline':
      # %%% Do inline scripts still have CDATA tags?
      elt.string = jstext
    elif jstype == 'script.href':
      elt['href'] = 'javascript:' + re.sub('\n', ' ', jstext)
    elif jstype.startswith('script.event.'):
      event = jstype[13:]
      eventattr = 'on' + event
      elt[eventattr] = re.sub('\n', ' ', jstext)

  if policy is not None:
    head = soup.head
    # Create the head tag if necessary.
    if head is None:
      head = soup.new_tag("head")
      html = soup.html
      assert html is not None, "HTML file doesn't contain html tag"
      html.insert(0, head)

    # Add the policy script tag. It should be relative to the output.
    polfilename = os.path.basename(policy)
    polfl = open(policy, 'r')
    polcontent = polfl.read()
    polfl.close()

    newpolfile = os.path.join(jsdir, polfilename)
    if os.path.exists(newpolfile):
      if not OVERWRITE:
        fatal('Unable to overwrite policy file: %s' % newpolfile)
    newpolfl = open(newpolfile, 'w')
    newpolfl.write(polcontent)

    policytag = soup.new_tag("script", src=polfilename)
    head.insert(0, policytag)

    # Create a symbolic link and insert the JAMScript library tag.
    libpath = JAMSCRIPT_LIB
    libdir, libname = os.path.split(libpath)
    # Link the library in the same directory as the policy.
    linkdir = jsdir
    linkpath = symlink(libpath, linkdir)
    libtag = soup.new_tag("script", src=libname)
    head.insert(1, libtag)

  return soup.prettify()
# /repack



def main():
  parser = OptionParser(usage="%prog HTMLFILE JSLIST")
  parser.add_option('-v', '--verbose', action='store_true', default=False, dest='verbose', help='verbose output')
  parser.add_option('--vv', action='store_true', default=False, dest='veryverbose', help='very verbose output')
  parser.add_option('-o', '--outfile', action='store', default=None, dest='outfile', help='output file')
  parser.add_option('-d', '--jsdir', action='store', default=None, dest='jsdir', help='script directory')
  parser.add_option('-f', '--force', action='store_true', default=False, dest='force', help='overwrite output file')
  parser.add_option('-p', '--policy', action='store', default=None, dest='policy', help='include policy file (and libTx.js)')

  opts, args = parser.parse_args()

  if len(args) != 2:
    parser.error("Invalid number of arguments")

  htmlfile = os.path.abspath(args[0])
  if not os.path.isfile(htmlfile):
    fatal("HTMLFILE argument is not a file")
  jslist = os.path.abspath(args[1])
  if not os.path.isfile(jslist):
    fatal("JSLIST argument is not a file")

  outfile = opts.outfile
  if outfile is not None:
    if os.path.exists(outfile):
      if not os.path.isfile(outfile) or not opts.force:
        fatal('Output file %s exists, use -f to overwrite' % outfile)

  global VERYVERBOSE, VERBOSE, OVERWRITE
  VERYVERBOSE = opts.veryverbose
  VERBOSE = opts.verbose
  OVERWRITE = opts.force

  policy = opts.policy

  newhtml = repack(htmlfile, jslist, jsdir=opts.jsdir, policy=policy)

  if outfile is None:
    outfl = sys.stdout
  else:
    outfl = open(outfile, 'w')

  outfl.write(newhtml)


if __name__ == "__main__":
  main()

