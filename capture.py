#!/usr/bin/python

# USAGE: ./capture.py NUM_PHOTOS

import sys
import os
import time

def cmd(s):
    ret = os.system(s)
    if ret != 0:
        raise ValueError(ret)


def main():
    # XXX: set drive mode to single, no delay (autoscatto off)
    
    NUM = int(sys.argv[1])
    cmd('gphoto2 --set-config capturetarget=1')
    captured = 0
    while True:
        print
        print 'capture %d/%d' % (captured+1, NUM)
        try:
            cmd('gphoto2 --capture-image')
        except ValueError:
            print 'Error when executing gphoto2, sleeping some seconds before retrying'
            time.sleep(5)
            print 'Retry!'
        else:
            captured += 1

        if captured == NUM:
            break

    print
    print
    print '===================='
    print 'REMEMBER THE DARKS!'
    print '===================='

if __name__ == '__main__':
    main()
