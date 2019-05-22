#!/usr/bin/python

# USAGE: ./capture.py NUM_PHOTOS

import sys
import os
import time

def cmd(s):
    ret = os.system(s)
    if ret != 0:
        raise ValueError(ret)

def get_battery_level():
    cmd("gphoto2 --get-config /main/status/batterylevel | grep -E '(Label|Current)'")

def capture_many(n):
    captured = 0
    while True:
        print
        print 'capture %d/%d' % (captured+1, n)
        try:
            cmd('gphoto2 --capture-image')
        except ValueError:
            print 'Error when executing gphoto2, sleeping some seconds before retrying'
            time.sleep(5)
            print 'Retry!'
        else:
            captured += 1

        if captured == n:
            break

        if captured % 10 == 0:
            get_battery_level()

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

    NUM = int(sys.argv[1])
    cmd('gphoto2 --set-config /main/capturesettings/drivemode=0') # 0 ==> single
    cmd('gphoto2 --set-config capturetarget=1')
    capture_many(NUM)

    print
    print
    print '===================='
    print 'REMEMBER THE DARKS!'
    print '===================='

if __name__ == '__main__':
    main()

