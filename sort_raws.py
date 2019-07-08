#!/usr/bin/python

"""
Usage: manage_raws.py [DIR] [options]

Options:
  --move                  Create directories for each exposure value and move files there
  --round-ss              Round shutter speed to the closest 10s (e.g. 88s => 90s)
  -n --min-folder-size=N  Minimum number of files needed to make a folder [Default: 5]
  -v --verbose            Show the individual files in the summary
  -h --help               show this
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

def load_info(fname, round_ss):
    tags = load_exif(fname)
    iso = tags['EXIF ISOSpeedRatings'].values[0]
    shutter_speed = divide(tags['EXIF ExposureTime'].values[0])
    if round_ss:
        shutter_speed = round(shutter_speed, -1)
    f = divide(tags['EXIF FNumber'].values[0])
    return Info(iso, shutter_speed, f)


def print_tags(tags):
    for tag in tags.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            print "Key: %s, value %s" % (tag, tags[tag])

def move(src, dst):
    shutil.move(str(src), str(dst))

def summarize_jpg(root, verbose, round_ss, min_folder_size):
    def print_items(prefix, items):
        for info, files in items:
            print '%s ISO %5d %9.5fs F/%2s: %4d' % (prefix, info.iso, info.shutter_speed,
                                                    info.f, len(files))
            if verbose:
                for f in sorted(files):
                    print '    %s' % f.relto(root)
                print
    #
    root = py.path.local(root)
    infodict = defaultdict(list)
    for jpg in root.visit('*.JPG'):
        info = load_info(jpg, round_ss)
        infodict[info].append(jpg)
    #
    to_move = []
    to_keep = []
    items = infodict.items()
    items.sort(key=lambda item: len(item[1]))
    for info, files in items:
        if len(files) < min_folder_size:
            to_keep.append((info, files))
        else:
            to_move.append((info, files))

    if to_keep:
        print_items(' ', to_keep)
        print
    print_items('*', to_move)
    return to_move

def sort_jpg(root, items):
    root = py.path.local(root)
    for info, files in items:
        target_dir = root.join('iso%s-%ss-F%s' % info)
        target_dir.ensure(dir=True)
        for jpg in files:
            move(jpg, target_dir)
            cr3 = jpg.new(ext='CR3')
            move(cr3, target_dir)


def main():
    args = docopt.docopt(__doc__)
    d = args['DIR'] or '.'
    min_folder_size = int(args['--min-folder-size'])
    to_move = summarize_jpg(d, args['--verbose'], args['--round-ss'], min_folder_size)
    if args['--move']:
        sort_jpg(d, to_move)


if __name__ == '__main__':
    main()
    
