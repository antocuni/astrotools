#!/usr/bin/python

import sys
from capture import capture_many, cmd

def main():
    cmd
    cmd('gphoto2 --set-config /main/capturesettings/shutterspeed=1/4000')
    cmd('gphoto2 --set-config /main/capturesettings/drivemode=0') # 0 ==> single
    N = int(sys.argv[1])
    capture_many(N)

if __name__ == '__main__':
    main()
