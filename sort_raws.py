#!/usr/bin/python

"""
Usage: manage_raws.py [DIR] [options]

Options:
  --move        Create directories for each exposure value and move files there
  -v --verbose  Show the individual files in the summary
  -h --help     show this
"""

import docopt
from collections import namedtuple, defaultdict
import shutil
import py

Info = namedtuple('Info', ['iso', 'shutter_speed', 'f'])


def load_exif(fname):
    import exifread
    with fname.open('rb') as f:
        tags = exifread.process_file(f)
    return tags

def divide(r):
    return float(r.num)/r.den

def load_info(fname):
    tags = load_exif(fname)
    iso = tags['EXIF ISOSpeedRatings'].values[0]
    shutter_speed = divide(tags['EXIF ExposureTime'].values[0])
    f = divide(tags['EXIF FNumber'].values[0])
    return Info(iso, shutter_speed, f)


def print_tags(tags):
    for tag in tags.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            print "Key: %s, value %s" % (tag, tags[tag])

def move(src, dst):
    shutil.move(str(src), str(dst))

def summarize_jpg(root, verbose):
    root = py.path.local(root)
    infodict = defaultdict(list)
    for jpg in root.visit('*.JPG'):
        info = load_info(jpg)
        infodict[info].append(jpg)
    #
    items = infodict.items()
    items.sort(key=lambda item: len(item[1]))
    for info, files in items:
        print 'ISO %5d %9.5fs F/%2s: %4d' % (info.iso, info.shutter_speed,
                                             info.f, len(files))
        if verbose:
            for f in sorted(files):
                print '    %s' % f.relto(root)
            print


def sort_jpg(root):
    root = py.path.local(root)
    for jpg in root.visit('*.JPG'):
        info = load_info(jpg)
        target_dir = root.join('iso%s-%ss-F%s' % info)
        target_dir.ensure(dir=True)
        move(jpg, target_dir)
        cr3 = jpg.new(ext='CR3')
        move(cr3, target_dir)

        


def main():
    args = docopt.docopt(__doc__)
    d = args['DIR'] or '.'
    summarize_jpg(d, args['--verbose'])
    if args['--move']:
        sort_jpg(d)


if __name__ == '__main__':
    main()
    
