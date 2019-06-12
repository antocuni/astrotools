from collections import namedtuple
import shutil
import py

Info = namedtuple('Info', ['filename', 'iso', 'shutter_speed', 'f'])


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
    return Info(fname, iso, shutter_speed, f)


def print_tags(tags):
    for tag in tags.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            print "Key: %s, value %s" % (tag, tags[tag])

def move(src, dst):
    shutil.move(str(src), str(dst))
        
def sort_jpg():
    root = py.path.local('.')
    for jpg in root.listdir('*.JPG'):
        info = load_info(jpg)
        target_dir = root.join('iso%s-%ss-F%s' % (info[1:]))
        target_dir.ensure(dir=True)
        move(jpg, target_dir)
        cr3 = jpg.new(ext='CR3')
        move(cr3, target_dir)


def main():
    sort_jpg()


if __name__ == '__main__':
    main()
    
