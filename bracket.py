#!/usr/bin/python

import sys
from capture import BaseCamera, cmd

class Capture(object):

    def __init__(self):
        self.config = []
        self.n = 0

    def __repr__(self):
        return '<Capture: n=%d %s>' % (self.n, ' '.join(sorted(self.config)))

    def get_gphoto2_command(self):
        cmd = ['gphoto2']
        for conf in self.config:
            cmd.append('--set-config')
            cmd.append(conf)
        cmd.append('| cat')
        return ' '.join(cmd)

def parse_options(argv):
    captures = [Capture()]
    for arg in argv:
        current = captures[-1]
        if arg.startswith('n='):
            current.n = int(arg[2:])
            captures.append(Capture())
            continue

        if arg.startswith('s='):
            arg = arg.replace('s=', 'shutterspeed=')
        if arg.startswith('f='):
            arg = arg.replace('f=', 'aperture=')
        current.config.append(arg)
    return [cap for cap in captures if cap.n > 0]

def main():
    if len(sys.argv) == 1:
        print "Example usage:"
        print "  To take 5 shoots at F/3.5, 13s, ISO 6400 and"
        print "          3 shoots at F/3.5,  5s, ISO 6400"
        print "  ./bracket.py f=3.5 s=13 iso=6400 n=5 s=5 n=3"
        return
    captures = parse_options(sys.argv[1:])
    camera = BaseCamera.autodetect()
    if camera is None:
        print 'No camera found'
        return
    for cap in captures:
        print cap
        command = cap.get_gphoto2_command()
        print command
        cmd(command)
        camera.capture_many(cap.n)

if __name__ == '__main__':
    main()
