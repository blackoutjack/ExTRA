
#
# This file contains some general-purpose utility functions that can be
# used by other Python scripts. It is not meant to be run on its own.
#

import sys
MAJOR = sys.version_info[0]
if MAJOR >= 3:
  import urllib.parse as urlparse
else:
  import urlparse
from config import *

def get_unique_filename(origpath):
  dirpath, filename = os.path.split(origpath)
  if not os.path.exists(dirpath):
    # Easy case: the original path is available.
    return origpath

  if not os.path.isdir(dirpath):
    dirparts = []
    # Climb the directory structure to see if there are conflicts.
    dirpart = dirpath
    while dirpart != '':
      # %%% Maybe need special handling for symlinks?
      if os.path.isdir(dirpart):
        break
      if os.path.isfile(dirpart):
        # Rename the directory.
        pathprefix = dirpart
        dirpart, lastpart = os.path.split(dirpart)
        dirparts.insert(0, lastpart)
        idx = 0
        while os.path.isfile(pathprefix):
          # Make an altered directory name.
          newlastpart = lastpart + '-' + str(idx)
          pathprefix = os.path.join(dirpart, newlastpart)
          idx += 1

        newfilepath = pathprefix
        for suffixpart in dirparts:
          newfilepath = os.path.join(newfilepath, suffixpart)

        if os.path.isdir(pathprefix):
          # Need to make sure the new path is available.
          return get_unique_filename(newfilepath)
        origpath = newfilepath
        break

      dirpart, lastpart = os.path.split(dirpart)
      dirparts.insert(0, lastpart)

    # Getting here means the original path is available.
    return origpath

  filebase, fileext = os.path.splitext(filename)
  newfilepath = origpath
  idx = 0
  while os.path.exists(newfilepath):
    # Make an altered filename.
    newfilebase = filebase + '-' + str(idx)
    newfilename = newfilebase + fileext
    newfilepath = os.path.join(dirpath, newfilename)
    idx += 1

  return newfilepath
# /get_unique_filename

def get_output_dir(top, base):
  parts = base.split('/')
  dirparts = parts[:-1]

  parent = top
  for dirpart in dirparts:  
    parent = os.path.join(parent, dirpart)

  lastpart = parts[-1]
  nextId = 0
  if os.path.isdir(parent):
    for curdir in os.listdir(parent):
      if curdir.startswith(lastpart + '-'):
        idx = curdir[len(lastpart)+1:]
        try:
          idxnum = int(idx)
          if idxnum >= nextId:
            nextId = idxnum + 1
        except:
          warn('Non-numeric suffix, ignoring: %s' % idx)
  dirparts.append(lastpart + '-' + str(nextId))

  ret = top
  for dirpart in dirparts:
    ret = os.path.join(ret, dirpart)
  return ret
# /get_output_dir

def fatal(txt, code=1):
  sys.stderr.write("FATAL: %s\n" % txt)
  sys.exit(code)

def err(txt):
  sys.stderr.write("ERROR: %s\n" % txt)
  sys.stderr.flush()

def out(txt):
  sys.stderr.write("INFO: %s\n" % txt)
  sys.stderr.flush()

def warn(txt):
  sys.stderr.write("WARNING: %s\n" % txt)
  sys.stderr.flush()

def get_lines(filename, comment=None):
  fl = open(filename, 'r')
  ret = []
  for line in fl.readlines():
    line = line.strip()
    if comment is not None and line.startswith(comment):
      continue
    ret.append(line)
  return ret

def get_file_info(filepath):
  return {
    'app': get_base(filepath),
    'desc': get_descriptors(filepath),
    'ext': get_ext(filepath)
  }
# /get_file_info

def get_ext(filepath):
  parts = os.path.splitext(filepath)
  return parts[1]
# /get_ext

# Get the internal dot-separated components of the filepath.
# E.g. "path/app.jam.more.extra.js" => ['jam', 'more', 'extra'].
def get_descriptors(filepath):
  dirpath, filename = os.path.split(filepath)
  dirname = os.path.basename(dirpath)

  if dirname.startswith('source-'):
    descname = dirname[len('source-'):]
    desc = descname.split('.')
  else:
    desc = []
    fileparts = filename.split('.')
    if len(fileparts) > 2:
      for i in range(1, len(fileparts) - 1):
        desc.append(fileparts[i])
  return desc
# /get_descriptors

# Get the first dot-separated component of a filename or filepath.
def get_base(filepath):
  filename = os.path.basename(filepath)
  fileparts = filename.split('.', 1)
  base = fileparts[0]
  return base

def symlink(srcpath, linkdir, linkname=None, relative=False): 
  srcdir, srcname = os.path.split(srcpath)
  if linkname is None:
    linkpath = os.path.join(linkdir, srcname)
  else:
    linkpath = os.path.join(linkdir, linkname)
  # |lexists| is true for broken symbolic links.
  # %%% Should check to see if the link is correct or needs updating.
  if not os.path.lexists(linkpath):
    if relative:
      # Get the path relative to the target directory.
      src = os.path.relpath(srcpath, linkdir)
    else:
      src = os.path.abspath(srcpath)
    os.symlink(src, linkpath)
  return linkpath
# /symlink

def is_url(uri):
  return get_protocol(uri) in ['http', 'https']
# /is_url

def get_protocol(url):
  urlparts = urlparse.urlparse(url)
  prot = urlparts[0]
  return prot
# /get_protocol

def get_relative_path(url, usedomain=False, referer=None):
  urlparts = urlparse.urlparse(url)
  filepath = urlparts[2]
  filepath = filepath.lstrip('/')
      
  if usedomain and is_url(url):
    # Prepend the domain
    filepath = os.path.join(urlparts[1], filepath)

  if referer is not None:
    # Get the path relative to the referer.
    refparts = urlparse.urlparse(referer)
    refpath = refparts[2]
    # Assume the referer is a file, and remove the filename.
    refpath = os.path.split(refpath)[0]
    if refpath.startswith('/'):
      refpath = refpath[1:]
    filepath = os.path.relpath(filepath, refpath)

  # Remove beginning and ending slashes.
  filepath = filepath.strip('/')

  return filepath
# /get_relative_path

