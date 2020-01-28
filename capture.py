#!/usr/bin/python

# USAGE: ./capture.py NUM_PHOTOS [bulb_speed]

import sys
import os
import commands
import time
import py

def cmd(s):
    ret = os.system(s)
    if ret != 0:
        raise ValueError(ret)

def set_config(x):
    cmd('gphoto2 --set-config %s | cat' % x)

class BaseCamera(object):

    def __init__(self, model, capture_dir='/tmp/images/'):
        self.capture_dir = py.path.local(capture_dir)
        print 'cd %s' % self.capture_dir
        self.capture_dir.ensure(dir=True)
        self.capture_dir.chdir()
        print "Camera is:", model
        print "Setting capturetarget to SD"
        set_config("capturetarget=1")
        self.set_drivemode()

    @staticmethod
    def autodetect():
        def error(output):
            print 'cannot auto-detect the camera:'
            print output
            raise ValueError()
        #
        output = commands.getoutput('gphoto2 --auto-detect')
        lines = output.splitlines()
        if len(lines) == 2:
            return None
        elif len(lines) != 3:
            error()
        #
        model = lines[-1].lower()
        if model.startswith('canon'):
            return CanonCamera(model)
        elif model.startswith('nikon'):
            return NikonCamera(model)
        else:
            error()

    def set_drivemode(self):
        raise NotImplementedError

    def set_shutterspeed_to_bulb(self):
        raise NotImplementedError

    def do_one_bulb(self):
        raise NotImplementedError

    def capture_many(self, n, shutterspeed=None):
        if shutterspeed is not None:
            self.set_shutterspeed_to_bulb()
        self._do_many_captures(n, shutterspeed)

    def get_battery_level(self):
        cmd("gphoto2 --get-config /main/status/batterylevel | grep -E '(Label|Current)'")

    def _do_many_captures(self, n, shutterspeed):
        captured = 0
        while True:
            print
            print 'capture %d/%d' % (captured+1, n)
            try:
                if shutterspeed is None:
                    # XXX: if/when we switch to --capture-image-and-download,
                    # make sure to investigate whether we need --keep
                    cmd('gphoto2 --capture-image | cat')
                else:
                    self.do_one_bulb(shutterspeed)
                    time.sleep(5)
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


class CanonCamera(BaseCamera):
    """
    Tested with Canon EOS M50
    """

    # XXX how to find this programmatically?
    CAMERA_FOLDER = '/store_00020001/DCIM/100CANON/'

    def set_drivemode(self):
        print "Setting drivemode to single"
        set_config('/main/capturesettings/drivemode=0')

    def set_shutterspeed_to_bulb(self):
        print "Setting shutterspeed to bulb"
        set_config('/main/capturesettings/shutterspeed=bulb')

    def do_one_bulb(self, shutterspeed, download=True):
        if download:
            wait = '--wait-event-and-download=2s --keep'
        else:
            wait = '--wait-event=2s'
        cmd("gphoto2 "
            "--set-config eosremoterelease=Immediate "
            "--wait-event=%ss "
            "--set-config eosremoterelease='Release Full' "
            "%s "
            " | grep -v UNKNOWN " % (shutterspeed, wait))
        self.download_images()

    def download_images(self):
        print 'Downloading new images...'
        for cr3 in self.capture_dir.listdir('*.CR3'):
            print 'Found %s' % cr3
            jpg = cr3.new(ext='JPG')
            cmd("gphoto2 -f %s --get-file %s" % (self.CAMERA_FOLDER, jpg.basename))
            cr3.remove()


class NikonCamera(BaseCamera):
    """
    Tested with Nikon D5300
    """

    def set_drivemode(self):
        # XXX implement me eventually
        pass

    def set_shutterspeed_to_bulb(self):
        # XXX investigate Bulb vs Time
        print "Setting shutterspeed to bulb"
        set_config('/main/capturesettings/shutterspeed=Bulb')

    def do_one_bulb(self, shutterspeed):
        # apparently, with the nikon DSC5300 it is enough to set bulb=1 to start
        # the capture. Then the camure will stop the capture automatically when
        # gphoto2 disconnects
        cmd("gphoto2 "
            "--set-config /main/actions/bulb=1 "
            "--wait-event=%ss "
            " | grep -v UNKNOWN " % shutterspeed)


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

    cam = BaseCamera.autodetect()
    if cam is None:
        print 'No camera found'
        return
    cam.capture_many(n, shutterspeed)
    print
    print
    print '===================='
    print 'REMEMBER THE DARKS!'
    print '===================='

if __name__ == '__main__':
    main()
