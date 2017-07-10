import cv2
import os
import time
import itertools
import numpy as np
from shutil import copyfile

mkpath = os.path.join   # for convenience

# dimension of window (to display images to be labeled)
window_w = 650
window_h = 650

nav_keys = [27]

def parse_config_file(config):

  # set up structures for storing directories, labels, etc.
  root_dir = os.getcwd()
  source_dirs = []
  label_lookup = {}

  # read config.txt
  with open(config) as f:

    for i, line in enumerate(f.readlines()):
      # remove trailing whitespace and parse, using ' ' as delimiter
      parsed_line = line.strip().split(' ')
      tag, args = parsed_line[0], parsed_line[1:]

      # skip empty lines
      if len(args) < 1: continue

      # extract root directory
      elif (tag == 'root' and len(args) == 1):
        root_dir = os.path.join(os.getcwd(), args[0])

      # add directory to list of source directories
      elif (tag == 'source' and len(args) == 1):
        source_dirs.append(args[0])

      # add to label lookup
      elif (tag == 'label' and len(args) == 3):
        key, label, target_dir = args

        # check to make sure that key is valid        
        if len(key) != 1:
          print "problem parsing config.txt: invalid key"
          print "on line: " + i
          return -1

        # if everything checks out, add to label lookup dictionary
        label_lookup[ord(key)] = (label, os.path.join('labeled', target_dir))


  # join source directory paths with root directory path
  source_dirs = [os.path.join(root_dir, i) for i in source_dirs]

  # join target directory paths with root directory path
  for i, v in label_lookup.iteritems():
    img_dir = os.path.join(root_dir, v[1])
    label_lookup[i] = (v[0], img_dir)

    # create directory if it doesn't already exist
    if not os.path.exists(img_dir): os.makedirs(img_dir)

  return root_dir, source_dirs, label_lookup


# -------------------------------------------------------------------------

# parse config file and extract sources, labels, target directories, etc.
root_dir, source_dirs, label_lookup = parse_config_file(
  os.path.join(os.getcwd(), 'config.txt'))

# create dictionary to hold counts for each label
counts = { v[0]:0 for v in label_lookup.itervalues() }

# check if filename extension is in a list of valid extensions
def valid_img_ext(fname):
  suffixes = ['.bmp', '.jpg', '.jpeg', '.png', '.tif', '.tiff']
  return reduce(lambda x,y: x or y, map(lambda x: fname.endswith(x), suffixes))

# go through source dirs and create list of filenames, if extension is valid
filenames = list(itertools.chain.from_iterable(
  [[os.path.join(d, f) for f in os.listdir(d) if valid_img_ext(f)] \
  for d in source_dirs]))

for filename in filenames:
  img = cv2.imread(filename)

  # get height and width of image to label, skip if its larger than max size
  h, w, _ = img.shape
  if h > window_h - 10 or w > window_w - 10:
    print "image exceeds bounds, skipping."
    continue

  # create empty frame (all zeros) and center image within frame
  frame = np.zeros((window_w, window_h, 3), np.uint8)
  top, left = (window_h/2 - h/2, window_w/2 - w/2) # top left corner img
  frame[top:top+h, left:left+w] = img

  cv2.imshow('quick-tagger', frame)

  # wait for a keypress (muust be either a label or a nav key)
  key = None
  while (key not in label_lookup) and (key not in nav_keys):
    key = cv2.waitKey(0)

  # if user pressed ESC or something, this is where we'll respond to that
  if key in nav_keys:
    print "goodbye!"
    break

  label, target_dir = label_lookup[key]

  # add a label to the image (just for user to see)
  font = cv2.FONT_HERSHEY_SIMPLEX
  cv2.putText(frame, label, (10,50), font, 1, (255,255,255), 2)
  cv2.imshow('quick-tagger', frame)
  cv2.waitKey(500)

  # move file into appropriate directory, increment count
  copyfile(filename, mkpath(target_dir, os.path.basename(filename)))
  counts[label] += 1

cv2.destroyWindow('quick-tagger')
print counts
print "all done!"