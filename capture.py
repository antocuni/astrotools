#!/usr/bin/python

# USAGE: ./capture.py NUM_PHOTOS [bulb_speed]

import sys
import os
import time

def cmd(s):
    ret = os.system(s)
    if ret != 0:
        raise ValueError(ret)

def set_config(x):
    cmd('gphoto2 --set-config %s | cat' % x)

class Camera(object):

    def __init__(self):
        print "Setting capturetarget to SD"
        set_config("capturetarget=1")

    def capture_many(self, n, shutterspeed=None):
        print "Setting drivemode to single"
        set_config('/main/capturesettings/drivemode=0')
        if shutterspeed is not None:
            print "Setting shutterspeed to bulb"
            set_config('/main/capturesettings/shutterspeed=bulb')
        self._do_many_captures(n, shutterspeed)

    def get_battery_level(self):
        cmd("gphoto2 --get-config /main/status/batterylevel | grep -E '(Label|Current)'")

    def _do_one_bulb(self, shutterspeed):
        cmd("gphoto2 "
            "--set-config eosremoterelease=Immediate "
            "--wait-event=%ss "
            "--set-config eosremoterelease='Release Full' "
            "--wait-event=2s "
            " | grep -v UNKNOWN " % shutterspeed)

    def _do_many_captures(self, n, shutterspeed):
        captured = 0
        while True:
            print
            print 'capture %d/%d' % (captured+1, n)
            try:
                if shutterspeed is None:
                    cmd('gphoto2 --capture-image | cat')
                else:
                    self._do_one_bulb(shutterspeed)
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

    # 
    if len(sys.argv) == 3:
        n = int(sys.argv[1])
        shutterspeed = int(sys.argv[2])
    elif len(sys.argv) == 2:
        n = int(sys.argv[1])
        shutterspeed = None
    else:
        print "Usage: ./capture.py N [shutterspeed]"
        sys.exit(1)

    cam = Camera()
    cam.capture_many(n, shutterspeed)
    print
    print
    print '===================='
    print 'REMEMBER THE DARKS!'
    print '===================='

if __name__ == '__main__':
    main()

