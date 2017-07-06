import cv2
import os

from shutil import copyfile

mkpath = os.path.join   # for convenience

source_dir = mkpath(os.getcwd(), 'demo-images')

label_lookup = {
  ord('j') : ('bottle-bud-america',
    mkpath(source_dir, 'labeled/bottle-bud-america')),
  ord('k') : ('negative',
    mkpath(source_dir, 'labeled/negative')),
}

nav_keys = [27]

# create dictionary to hold counts for each label
counts = { v[0]:0 for v in label_lookup.itervalues() }

# check if filename extension is in a list of valid extensions
def valid_img_ext(fname):
  suffixes = ['.bmp', '.jpg', '.jpeg', '.png', '.tif', '.tiff']
  return reduce(lambda x,y: x or y, map(lambda x: fname.endswith(x), suffixes))

# get list of all files in source directory, if extension is valid 
filenames = [f for f in os.listdir(source_dir) if valid_img_ext(f)]

for filename in filenames:
  img_filepath = mkpath(source_dir, filename)
  img = cv2.imread(img_filepath)

  cv2.imshow('quick-tagger', img)

  # wait for a keypress (muust be either a label or a nav key)
  key = None
  while (key not in label_lookup) and (key not in nav_keys):
    key = cv2.waitKey(0)

  # if user pressed ESC or something, this is where we'll respond to that
  if key in nav_keys:
    break

  # move file into appropriate directory, increment count
  copyfile(img_filepath, mkpath(label_lookup[key][1], filename))
  counts[label_lookup[key][0]] += 1

cv2.destroyWindow('quick-tagger')
print "all done!"

  