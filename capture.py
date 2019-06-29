#!/usr/bin/python

# USAGE: ./capture.py NUM_PHOTOS

import sys
import os
import time

def cmd(s):
    ret = os.system(s)
    if ret != 0:
        raise ValueError(ret)


class Camera(object):

    def __init__(self):
        print "Setting capturetarget to SD"
        cmd('gphoto2 --set-config capturetarget=1 | cat')

    def capture_many(self, n):
        print "Setting drivemode to single"
        cmd('gphoto2 --set-config /main/capturesettings/drivemode=0 | cat')
        self._do_n_captures(n)

    def get_battery_level(self):
        cmd("gphoto2 --get-config /main/status/batterylevel | grep -E '(Label|Current)'")

    def _do_one_capture(self):
        cmd('gphoto2 --capture-image | cat')

    def _do_n_captures(self, n):
        captured = 0
        while True:
            print
            print 'capture %d/%d' % (captured+1, n)
            try:
                self._do_one_capture()
            except ValueError:
                print ('Error when executing gphoto2, '
                       'sleeping some seconds before retrying')
                time.sleep(5)
                print 'Retry!'
            else:
                captured += 1

            if captured == n:
                break

            if captured % 10 == 0:
                self.get_battery_level()

def main():
    # TODO: I saw this output:
    """
    capture 102/200
    ERROR: Could not capture image.
    ERROR: Could not capture.

    capture 103/200

    *** Error ***
    Canon EOS M Full-Press failed (0x2019: PTP Device Busy)
    ERROR: Could not capture image.
    ERROR: Could not capture.
    *** Error (-110: 'I/O in progress') ***
    """
    # It means that capture 102 was NOT done, but the retvalue was still 0. We
    # need a better way to check for errors

    n = int(sys.argv[1])
    cam = Camera()
    cam.capture_many(n)
    print
    print
    print '===================='
    print 'REMEMBER THE DARKS!'
    print '===================='

if __name__ == '__main__':
    main()

